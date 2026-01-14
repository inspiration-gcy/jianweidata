from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import RedirectResponse
from typing import List, Optional, Dict
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import or_,func
import json

from app.models import (
    Company,IPORank,IPOData,IPOReview,
    NoticeListResponse, EventListResponse, NewsListResponse,
    NoticeFilterRequest, SectorInformation, CompanySearchItem,
    IPODataBasic, IPOListResponse,
    IPORankBasic, IPORankListResponse,
    TimelineDetailListResponse,
    IPOReviewBasic, IPOReviewListResponse
)
from app.db import (
    get_db, 
    CompanyModel, NoticeModel, EventModel, NewsModel, 
    IPODataModel, IPORankModel, TimelineDetailModel, IPOReviewModel, SectorInfoModel
)
from app.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Data loading is handled via 'manage.py load' command.
    # Server startup assumes database is already populated.
    print("Lifespan: Server started. Ensuring database connection...")
    # Optional: Check if DB has tables/data? 
    # For now, just yield.
    yield
    # Clean up on shutdown

app = FastAPI(title="Jianwei Data API", lifespan=lifespan)

# --- Companies ---

@app.get("/companies/search", response_model=List[CompanySearchItem])
async def search_companies(
    keyword: str = Query(..., min_length=1),
    limit: int = Query(6, ge=1, le=20),
    db_session: Session = Depends(get_db)
):
    """
    Search companies by stockCode or Ticker (fuzzy match).
    Only includes companies with Market < 7.
    """
    keyword_lower = f"%{keyword}%"
    
    # SQLAlchemy filter
    query = db_session.query(CompanyModel).filter(
        CompanyModel.Market < 7,
        or_(
            CompanyModel.stockCode.ilike(keyword_lower),
            CompanyModel.Ticker.ilike(keyword_lower)
        )
    ).limit(limit)
    
    results = []
    for c in query.all():
        stock_code = c.stockCode or ""
        ticker = c.Ticker or ""
        results.append(CompanySearchItem(
            id=str(c.id),
            label=f"[{stock_code} {ticker}]",
            stockCode=stock_code,
            ticker=ticker
        ))
        
    return results

@app.get("/companies/{company_id}", response_model=Company)
async def get_company_by_id(company_id: str, db_session: Session = Depends(get_db)):
    """
    Get A-share company details by ID.
    """
    company = db_session.query(CompanyModel).filter(CompanyModel.id == company_id).first()
    
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company

@app.get("/companies/boards/top", response_model=Dict[str, List[str]])
async def get_top_companies_by_board(db_session: Session = Depends(get_db)):
    """
    Get top 100 companies for each A-share board.
    Boards: 沪市主板(1), 深市主板(2), 深市中小板(3), 深市创业板(4), 科创板(5)
    """
    boards = {
        1: "沪市主板",
        2: "深市主板",
        3: "深市中小板",
        4: "深市创业板",
        5: "科创板"
    }
    
    result = {name: [] for name in boards.values()}
    
    for market_code, board_name in boards.items():
        companies = db_session.query(CompanyModel).filter(
            CompanyModel.Market == market_code
        ).limit(100).all()
        
        for c in companies:
            code = c.stockCode or ""
            ticker = c.Ticker or ""
            label = f"{code} {ticker}".strip()
            result[board_name].append(label)
                
    return result

# --- Notices ---
@app.post("/notices", response_model=NoticeListResponse)
async def get_notices(
    request: NoticeFilterRequest, 
    page: Optional[int] = Query(None, ge=1, description="Page number (overrides body)"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Page size (overrides body)"),
    db_session: Session = Depends(get_db)
):
    # Determine pagination
    current_page = page if page is not None else request.page
    current_page_size = page_size if page_size is not None else request.page_size

    # Build query
    query = db_session.query(NoticeModel)
    
    # Standard Filtering
    if request.stock_code:
        query = query.filter(NoticeModel.StockCode.in_(request.stock_code))
    if request.sector:
        query = query.filter(NoticeModel.sector == request.sector)
    if request.category:
        query = query.filter(NoticeModel.Category.in_(request.category))
    if request.notice_type:
        query = query.filter(NoticeModel.NoticeType.in_(request.notice_type))
    if request.industry:
        query = query.filter(NoticeModel.Industry.in_(request.industry))
    if request.market_type:
        query = query.filter(NoticeModel.MarketType.in_([str(m) for m in request.market_type]))
    if request.province:
        query = query.filter(NoticeModel.Province.in_(request.province))
        
    # Date Range
    if request.start_date:
        query = query.filter(NoticeModel.PublishDate >= request.start_date)
    if request.end_date:
        query = query.filter(NoticeModel.PublishDate <= request.end_date)
              
    def apply_keyword_filter(q, col, search_text, match_mode):
        if not search_text:
            return q
        
        keywords = search_text.split()
        if not keywords:
            return q
            
        if match_mode == "all":
            for k in keywords:
                q = q.filter(col.ilike(f"%{k}%"))
        elif match_mode == "any":
            conditions = [col.ilike(f"%{k}%") for k in keywords]
            q = q.filter(or_(*conditions))
        elif match_mode == "none":
            for k in keywords:
                q = q.filter(~col.ilike(f"%{k}%"))
            
        return q

    # Title Search
    if request.title_search_all:
        query = apply_keyword_filter(query, NoticeModel.Title, request.title_search_all, "all")
    if request.title_search_any:
        query = apply_keyword_filter(query, NoticeModel.Title, request.title_search_any, "any")
    if request.title_search_none:
        query = apply_keyword_filter(query, NoticeModel.Title, request.title_search_none, "none")
        
    # Content Search (Preview)
    if request.content_search_all:
        query = apply_keyword_filter(query, NoticeModel.Preview, request.content_search_all, "all")
    if request.content_search_any:
        query = apply_keyword_filter(query, NoticeModel.Preview, request.content_search_any, "any")
    if request.content_search_none:
        query = apply_keyword_filter(query, NoticeModel.Preview, request.content_search_none, "none")
        
    # Total count (slow on large dataset, maybe optimize later)
    total = query.count()
    
    # Sort
    query = query.order_by(NoticeModel.PublishDate.desc())
    
    # Pagination
    notices = query.offset((current_page - 1) * current_page_size).limit(current_page_size).all()
    
    # Facets Implementation
    facet_fields = {
        "publish_entity": NoticeModel.StockCode,
        "Category": NoticeModel.Category,
        "NoticeType": NoticeModel.NoticeType,
        "Industry": NoticeModel.Industry,
        "MarketType": NoticeModel.MarketType,
        "Province": NoticeModel.Province
    }
    
    facets = {}
    
    # Calculate publish_entity count (total unique entities in current query)
    publish_entity_count = query.with_entities(NoticeModel.StockCode).distinct().count()
    facets["publish_entity_count"] = publish_entity_count
    
    for field_name, model_col in facet_fields.items():
        # Special handling for publish_entity to return "Code Ticker" format
        if field_name == "publish_entity":
             # Group by StockCode, but fetch a sample StockTicker to display
             agg_query = query.with_entities(
                 NoticeModel.StockCode, 
                 func.max(NoticeModel.StockTicker), # Get a ticker for this code
                 func.count(NoticeModel.StockCode)
             ).group_by(NoticeModel.StockCode).order_by(func.count(NoticeModel.StockCode).desc()).limit(50)
             
             results = agg_query.all()
             facets[field_name] = [
                 {"name": f"{r[0]} {r[1]}", "count": r[2]} 
                 for r in results if r[0] is not None
             ]
             continue

        # Construct aggregation query
        agg_query = query.with_entities(model_col, func.count(model_col)).group_by(model_col).order_by(func.count(model_col).desc()).limit(50)
        
        results = agg_query.all()
        
        facets[field_name] = [
            {"name": str(r[0]), "count": r[1]} 
            for r in results if r[0] is not None
        ]
    
    return {
        "total": total,
        "data": notices,
        "facets": facets
    }

# --- Events ---
@app.get("/events/top", response_model=EventListResponse)
async def get_top_events(
    market_type: str = Query("全部", description="Market type: A股, 港股, 美股, 全部"),
    limit: int = Query(100, ge=1, le=100),
    db_session: Session = Depends(get_db)
):
    query = db_session.query(EventModel)
    
    if market_type != "全部":
        if market_type == "A股":
            query = query.filter(or_(EventModel.market.like("%A股%"), EventModel.market.like("%科创板%")))
        else:
            query = query.filter(EventModel.market.like(f"%{market_type}%"))
            
    # Sort by heat (descending)
    query = query.order_by(EventModel.heat.desc())
    
    total = query.count()
    events = query.limit(limit).all()
    
    return {
        "total": total,
        "data": events
    }

@app.get("/events", response_model=EventListResponse)
async def get_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    event_id: Optional[str] = None,
    keyword: Optional[str] = Query(None, description="Fuzzy search by event title"),
    db_session: Session = Depends(get_db)
):
    query = db_session.query(EventModel)
    
    if event_id:
        query = query.filter(EventModel.event_id == event_id)
        
    if keyword:
        query = query.filter(EventModel.title.ilike(f"%{keyword}%"))
        
    total = query.count()
    events = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "data": events
    }

# --- News ---
@app.get("/news", response_model=NewsListResponse)
async def get_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    event_id: Optional[str] = None,
    keyword: Optional[str] = Query(None, description="Fuzzy search by news title"),
    db_session: Session = Depends(get_db)
):
    query = db_session.query(NewsModel)
    
    if event_id:
        query = query.filter(NewsModel.event_id == event_id)
        
    if keyword:
        query = query.filter(NewsModel.title.ilike(f"%{keyword}%"))
        
    total = query.count()
    news = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "data": news
    }

# --- IPO Data ---

@app.get("/ipo/list", response_model=IPOListResponse)
async def get_ipo_list(
    category: str = Query("首次公开发行", description="Category filter"),
    db_session: Session = Depends(get_db)
):
    query = db_session.query(IPODataModel).filter(IPODataModel.category == category)
    total = query.count()
    
    items = query.all()
    
    # Map to basic model
    result_data = []
    for item in items:
        tl = item.timeline
        if isinstance(tl, str):
            try:
                tl = json.loads(tl)
            except:
                # If parsing fails, try to clean potential formatting issues or just return empty list
                # Some CSVs might have single quotes instead of double quotes
                try:
                    tl = json.loads(tl.replace("'", '"'))
                except:
                    tl = []
        
        # Ensure it's a list (if None or other type)
        if tl is None:
            tl = []
                
        result_data.append(IPODataBasic(
            id=str(item.id),
            Issuer=item.Issuer,
            ListingMarket=item.ListingMarket,
            LatestDate=item.LatestDate,
            Status=item.Status,
            timeline=tl
        ))
        
    return {
        "total": total,
        "data": result_data
    }

@app.get("/ipo/{ipo_id}", response_model=IPOData)
async def get_ipo_detail(ipo_id: str, db_session: Session = Depends(get_db)):
    item = db_session.query(IPODataModel).filter(IPODataModel.id == ipo_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="IPO data not found")
        
    # Handle JSON fields
    if isinstance(item.timeline, str):
        try:
            item.timeline = json.loads(item.timeline)
        except:
            pass
            
    return item

# --- IPO Rank ---
@app.get("/ipo/rank/list", response_model=IPORankListResponse)
async def get_ipo_rank_list(
    category: str = Query("首次公开发行", description="Category filter"),
    listing_market: Optional[str] = Query(None, description="Listing Market filter"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db_session: Session = Depends(get_db)
):
    query = db_session.query(IPORankModel).filter(IPORankModel.category == category)
    
    if listing_market:
        query = query.filter(IPORankModel.ListingMarket == listing_market)
        
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    result_data = []
    for item in items:
        result_data.append(IPORankBasic(
            id=str(item.id),
            Rank=item.Rank,
            ListingMarket=item.ListingMarket,
            Entity=item.Entity,
            Sponsor=item.Sponsor,
            AccountingFirm=item.AccountingFirm,
            LawFirm=item.LawFirm,
            AcceptDate=item.AcceptDate,
            CurrentStatuses=item.CurrentStatuses,
            LastUpdateDate=item.LastUpdateDate,
            Reviewers=item.Reviewers,
            RelatedDocuments=item.RelatedDocuments
        ))
        
    return {
        "total": total,
        "data": result_data
    }

@app.get("/ipo/rank/{rank_id}", response_model=IPORank)
async def get_ipo_rank_detail(rank_id: str, db_session: Session = Depends(get_db)):
    item = db_session.query(IPORankModel).filter(IPORankModel.id == rank_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="IPO Rank data not found")
        
    return item

# --- Timeline Details ---

@app.get("/timeline/details", response_model=TimelineDetailListResponse)
async def get_timeline_details(
    stock_code: str = Query("000001", description="Stock Code to filter timeline details"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db_session: Session = Depends(get_db)
):
    query = db_session.query(TimelineDetailModel).filter(TimelineDetailModel.stockCode == stock_code)
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "data": items
    }

# --- IPO Review ---

@app.get("/ipo/review/list", response_model=IPOReviewListResponse)
async def get_ipo_review_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db_session: Session = Depends(get_db)
):
    query = db_session.query(IPOReviewModel)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    result_data = []
    for item in items:
        result_data.append(IPOReviewBasic(
            id=str(item.id),
            Rank=item.Rank,
            Entity=item.Entity,
            CurrentStatuses=item.CurrentStatuses,
            LastUpdateDate=item.LastUpdateDate,
            ReviewStatus=item.ReviewStatus,
            Reviewers=item.Reviewers,
            ReviewQuestions=item.ReviewQuestions
        ))
        
    return {
        "total": total,
        "data": result_data
    }

@app.get("/ipo/review/{review_id}", response_model=IPOReview)
async def get_ipo_review_detail(review_id: str, db_session: Session = Depends(get_db)):
    item = db_session.query(IPOReviewModel).filter(IPOReviewModel.id == review_id).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="IPO Review data not found")
        
    return item

@app.get("/sector/information", response_model=List[SectorInformation])
async def get_sector_information(sector: str = Query(..., description="The sector name"), db_session: Session = Depends(get_db)):
    """
    Get information for a specific sector.
    """
    # 1. Get Sector Info
    sector_info_items = db_session.query(SectorInfoModel).filter(SectorInfoModel.Sector == sector).all()
    
    if not sector_info_items:
        return []
        
    # Reconstruct the nested structure
    result_list = []
    
    for item in sector_info_items:
        # Get News for this item
        news = db_session.query(NewsModel).filter(NewsModel.inforId == item.id).all()
        
        # Convert to dict and add news
        item_dict = {
            "id": item.id,
            "Sector": item.Sector,
            "SourceName": item.SourceName,
            "SourceUrl": item.SourceUrl,
            "news": news # Pydantic model will handle serialization if names match
        }
        result_list.append(item_dict)
        
    return [{
        "sector": sector,
        "information": result_list
    }]

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
