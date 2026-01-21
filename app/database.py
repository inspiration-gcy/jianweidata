import pandas as pd
import os
import json
import glob
import uuid
from app.db import (
    SessionLocal, init_db, 
    CompanyModel, EventModel, NewsModel, SectorInfoModel,
    IPODataModel, IPORankModel, TimelineDetailModel, IPOReviewModel
)

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

FILE_PATHS = {
    "CompanyModel": os.path.join(DATA_DIR, "company.csv"),
    "NoticeModel": os.path.join(DATA_DIR, "notice"),
    "EventModel": os.path.join(DATA_DIR, "event.csv"),
    "NewsModel": os.path.join(DATA_DIR, "news.csv"),
    "SectorInfoModel": os.path.join(DATA_DIR, "sector_info.csv"),
    "IPODataModel": os.path.join(DATA_DIR, "ipo_data.csv"),
    "IPORankModel": os.path.join(DATA_DIR, "ipo_rank.csv"),
    "TimelineDetailModel": os.path.join(DATA_DIR, "timeline_details.csv"),
    "IPOReviewModel": os.path.join(DATA_DIR, "ipo_review.csv")
}

class Database:
    def __init__(self):
        self.loaded = False
        init_db()

    def load_from_directory(self, directory: str, model_name: str = None):
        """
        Load all data from a specified directory into the SQLite database.
        If model_name is provided, only load data for that specific model and clear old data.
        """
        print(f"Loading data from directory: {directory} into database...")
        if model_name:
            print(f"Target Model: {model_name}")
        
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            return

        session = SessionLocal()
        try:
            # Helper to clear table
            def clear_table(model):
                print(f"Clearing table for {model.__tablename__}...")
                session.query(model).delete()
                session.commit()

            # 1. Load Notices
            if not model_name or model_name == "NoticeModel":
                if model_name == "NoticeModel":
                    from app.db import NoticeModel
                    clear_table(NoticeModel)

                notice_dir = os.path.join(directory, "notice")
                if os.path.exists(notice_dir):
                    files = glob.glob(os.path.join(notice_dir, "notice_all_part_*.csv"))
                    files.sort()
                    
                    if files:
                        print(f"Found {len(files)} split notice CSV files in notice/ dir")
                        
                        # Use list to collect DataFrames for batch insert
                        # Or process in parallel? SQLite doesn't like parallel writes.
                        # Optimization: Increase chunksize and use 'multi' method if possible (not in standard pandas to_sql for sqlite)
                        # Optimization: Use transaction for all files? Already inside a session transaction?
                        # session.commit() is at the end. But to_sql uses its own connection/transaction unless we pass the connection.
                        # We are passing session.bind (engine).
                        
                        for f in files:
                            try:
                                print(f"Reading {os.path.basename(f)}...")
                                df = pd.read_csv(f, low_memory=False)
                                df = df.where(pd.notnull(df), None)
                                if 'StockCode' in df.columns:
                                    # Ensure StockCode is string
                                    df['StockCode'] = df['StockCode'].astype(str)
                                
                                # Generate IDs
                                if 'id' not in df.columns:
                                    df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
                                else:
                                    df['id'] = df['id'].apply(lambda x: str(x) if x else str(uuid.uuid4()))
                                    
                                # Convert 'MarketType' to string if it exists, to match model
                                if 'MarketType' in df.columns:
                                    df['MarketType'] = df['MarketType'].astype(str)

                                # Bulk Insert - Optimized chunksize
                                print(f"Inserting {len(df)} notices...")
                                df.to_sql('notices', con=session.bind, if_exists='append', index=False, chunksize=5000, method='multi')
                                print("Done.")
                            except Exception as e:
                                print(f"Error reading/inserting {f}: {e}")
                    else:
                        pass
            
            # 2. Load other standard files
            file_map = {
                "company.csv": (CompanyModel, "companies", "stockCode", "CompanyModel"),
                "event.csv": (EventModel, "events", None, "EventModel"),
                "news.csv": (NewsModel, "news", None, "NewsModel"),
                "ipo_data.csv": (IPODataModel, "ipo_data", None, "IPODataModel"),
                "ipo_rank.csv": (IPORankModel, "ipo_ranks", None, "IPORankModel"),
                "timeline_details.csv": (TimelineDetailModel, "timeline_details", "stockCode", "TimelineDetailModel"),
                "ipo_review.csv": (IPOReviewModel, "ipo_reviews", None, "IPOReviewModel")
            }

            for filename, (model, table_name, str_col, m_name) in file_map.items():
                if model_name and model_name != m_name:
                    continue

                if model_name == m_name:
                    clear_table(model)

                fpath = os.path.join(directory, filename)
                if os.path.exists(fpath):
                    print(f"Loading {filename}...")
                    try:
                        df = pd.read_csv(fpath, low_memory=False)
                        df = df.where(pd.notnull(df), None)

                        if "stockCode" in df.columns:
                            df['stockCode'] = df['stockCode'].astype(str)
                        
                        if str_col and str_col in df.columns:
                            df[str_col] = df[str_col].astype(str)
                        
                        # Generate IDs
                        if 'id' not in df.columns:
                            df['id'] = [str(uuid.uuid4()) for _ in range(len(df))]
                        else:
                            df['id'] = df['id'].apply(lambda x: str(x) if x else str(uuid.uuid4()))

                        # Additional processing
                        if table_name == "ipo_data":
                             # Convert dict/list cols to JSON string if they aren't already
                             # But to_sql handles string conversion? No, we need to ensure they are strings.
                             pass 
                        
                        # Handle potential column mismatches (simple approach: select only columns that exist in model)
                        # For now assume CSV matches model columns mostly.
                        
                        # Special handling for 'industry' in IPORank to avoid conflict if needed
                        if table_name == "ipo_ranks":
                            pass

                        # Filter columns: Keep only those that exist in the SQLAlchemy model
                        # This prevents "table has no column named X" errors
                        model_columns = {c.name for c in model.__table__.columns}
                        existing_columns = [c for c in df.columns if c in model_columns]
                        df = df[existing_columns]

                        print(f"Inserting {len(df)} items into {table_name}...")
                        df.to_sql(table_name, con=session.bind, if_exists='append', index=False, chunksize=5000, method='multi')
                        print(f"Loaded {table_name}.")
                    except Exception as e:
                        print(f"Error loading {filename}: {e}")
            
            # 3. Sector Info
            if not model_name or model_name == "SectorInfoModel":
                if model_name == "SectorInfoModel":
                    # Clear SectorInfoModel
                    clear_table(SectorInfoModel)
                    
                    # Also clear associated NewsModel entries?
                    # Since NewsModel is shared with news.csv, clearing all news might be too aggressive
                    # if we are just reloading sector info.
                    # However, sector_info.csv loads data into both 'sector_info' and 'news' tables.
                    # If we don't clear related news, we might get duplicates.
                    # A safer approach for partial reload is to delete news where inforId is not null?
                    # But NewsModel from news.csv might not have inforId.
                    # Let's assume if user explicitly asks to reload SectorInfoModel, they want to reset related data.
                    # BUT, clearing entire NewsModel table would wipe data from news.csv.
                    # So we should only clear news that are linked to sectors.
                    print("Clearing related news entries...")
                    session.query(NewsModel).filter(NewsModel.inforId != None).delete(synchronize_session=False)
                    session.commit()

                sector_file = os.path.join(directory, "sector_info.csv")
                if os.path.exists(sector_file):
                    print(f"Loading sector info from {sector_file}...")
                    try:
                        df = pd.read_csv(sector_file, low_memory=False)
                        df = df.where(pd.notnull(df), None)
                        
                        # We need to split this into SectorInfoModel and NewsModel
                        # 1. Sector Info
                        sector_items = []
                        news_items = []
                        
                        for _, row in df.iterrows():
                            row_id = str(row.get("id")) if row.get("id") else str(uuid.uuid4())
                            
                            sector_items.append({
                                "id": row_id,
                                "Sector": row.get("Sector"),
                                "SourceName": row.get("SourceName"),
                                "SourceUrl": row.get("SourceUrl")
                            })
                            
                            # Process News
                            if row.get("News"):
                                try:
                                    news_content = row["News"]
                                    if isinstance(news_content, str):
                                        raw_news = json.loads(news_content)
                                        for n in raw_news:
                                            news_items.append({
                                                "id": str(uuid.uuid4()),
                                                "newsId": str(uuid.uuid4()),
                                                "title": n.get("Title"),
                                                "time": n.get("PublishDate"),
                                                "url": n.get("Url"),
                                                "source": row.get("SourceName"),
                                                "inforId": row_id
                                            })
                                except:
                                    pass
                                    
                        if sector_items:
                            pd.DataFrame(sector_items).to_sql('sector_info', con=session.bind, if_exists='append', index=False, chunksize=1000)
                        
                        if news_items:
                            pd.DataFrame(news_items).to_sql('news', con=session.bind, if_exists='append', index=False, chunksize=1000)
                            
                        print("Sector info loaded.")
                    except Exception as e:
                        print(f"Error loading sector info: {e}")

            session.commit()
            self.loaded = True
            print("Database load complete.")
        except Exception as e:
            session.rollback()
            print(f"Database load failed: {e}")
        finally:
            session.close()

db = Database()
