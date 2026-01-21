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
    NoticeFilterRequest, SectorInformation, CompanyBaseItem,
    IPODataBasic, IPOListResponse,
    IPORankBasic, IPORankListResponse,
    TimelineDetailListResponse,
    IPOReviewBasic, IPOReviewListResponse,
    FavoriteNoticeRequest, FavoriteNoticeResponse, FavoriteItemResponse,
    GlobalSearchResponse, SectorSearchGroup
)
from app.db import (
    get_db, 
    CompanyModel, NoticeModel, EventModel, NewsModel, 
    IPODataModel, IPORankModel, TimelineDetailModel, IPOReviewModel, SectorInfoModel,
    FavoriteNoticeModel
)
from app.database import db
import uuid
import datetime

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

@app.get("/companies/search", response_model=List[CompanyBaseItem])
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
        results.append(CompanyBaseItem(
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

@app.get("/companies/boards/top", response_model=Dict[str, List[CompanyBaseItem]])
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

            result[board_name].append(CompanyBaseItem(
                id=str(c.id),
                label=f"{code} {ticker}".strip(),
                stockCode=code,
                ticker=ticker
            ))
                
    return result

# --- Notices ---

SECTOR_FIELD_CONFIG = {
    "三市公告": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}, {"name": "地域分布", "field": "Province"}],
    "新三板公告": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}, {"name": "地域分布", "field": "Province"}],
    "港股中文": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}],
    "港股英文": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}],
    "美股": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}],
    "法规库": [{"name": "法规类型", "field": "StockCode"}, {"name": "地域分布", "field": "Province"}, {"name": "发布机构", "field": "Institutions"}],
    "债券公告": [{"name": "债券名称", "field": "StockCode"}, {"name": "发行人", "field": "Publisher"}, {"name": "市场类型", "field": "MarketType"}, {"name": "债券品种", "field": "Category"}, {"name": "公告类型", "field": "NoticeType"}],
    "投行业务审核进程": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}, {"name": "地域分布", "field": "Province"}],
    "公募基金公告": [{"name": "匹配基金", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "基金管理人", "field": "Publisher"}],
    "科创板公告": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}, {"name": "地域分布", "field": "Province"}],
    "辅导信息": [{"name": "公告类型", "field": "NoticeType"}, {"name": "监管机构", "field": "StockCode"}],
    "投资者互动问答": [{"name": "发布主体", "field": "StockCode"}, {"name": "是否回复", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}, {"name": "地域分布", "field": "Province"}],
    "政府采购招标": [{"name": "公告类型", "field": "NoticeType"}, {"name": "项目类型", "field": "Category"}, {"name": "招标机构", "field": "StockCode"}, {"name": "地域分布", "field": "Province"}],
    "招股书比对": [{"name": "发布主体", "field": "StockCode"}],
    "创业板审核公告": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}, {"name": "地域分布", "field": "Province"}],
    "北交所公告": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "地域分布", "field": "Province"}],
    "证券行业监管信息": [{"name": "数据来源", "field": "Source"}, {"name": "监管机构", "field": "StockCode"}, {"name": "监管措施", "field": "Category"}],
    "科创板反馈问答": [{"name": "匹配主体", "field": "StockCode"}, {"name": "中介机构类型", "field": "IntermediaryType"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "地域分布", "field": "Province"}, {"name": "中介机构名称", "field": "IntermediaryName"}, {"name": "市场类型", "field": "MarketType"}],
    "上市公司函件问答": [{"name": "发布主体", "field": "StockCode"}, {"name": "行业统计", "field": "Industry"}, {"name": "地域分布", "field": "Province"}],
    "综合反馈问答": [{"name": "匹配主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "地域分布", "field": "Province"}],
    "创业板反馈问答": [{"name": "匹配主体", "field": "StockCode"}, {"name": "中介机构类型", "field": "IntermediaryType"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "地域分布", "field": "Province"}, {"name": "中介机构名称", "field": "IntermediaryName"}, {"name": "市场类型", "field": "MarketType"}],
    "债券反馈问答": [{"name": "发布主体", "field": "StockCode"}],
    "北交所反馈问答": [{"name": "匹配主体", "field": "StockCode"}, {"name": "中介机构类型", "field": "IntermediaryType"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "地域分布", "field": "Province"}, {"name": "中介机构名称", "field": "IntermediaryName"}, {"name": "市场类型", "field": "MarketType"}],
    "主板反馈问答": [{"name": "匹配主体", "field": "StockCode"}, {"name": "中介机构类型", "field": "IntermediaryType"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "地域分布", "field": "Province"}, {"name": "中介机构名称", "field": "IntermediaryName"}, {"name": "市场类型", "field": "MarketType"}],
    "微信搜索": [{"name": "公告类型", "field": "NoticeType"}],
    "再融资": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}, {"name": "地域分布", "field": "Province"}],
    "并购重组": [{"name": "发布主体", "field": "StockCode"}, {"name": "公告类型", "field": "NoticeType"}, {"name": "行业统计", "field": "Industry"}, {"name": "市场类型", "field": "MarketType"}, {"name": "地域分布", "field": "Province"}]
}

# Map Config Field -> (Request Field Name, DB Column)
FIELD_MAPPING = {
    "StockCode": ("stock_code", NoticeModel.StockCode),
    "NoticeType": ("notice_type", NoticeModel.NoticeType),
    "Industry": ("industry", NoticeModel.Industry),
    "MarketType": ("market_type", NoticeModel.MarketType),
    "Province": ("province", NoticeModel.Province),
    "Category": ("category", NoticeModel.Category),
    "Publisher": ("publisher", NoticeModel.Publisher),
    "Institutions": ("institutions", NoticeModel.Institutions),
    "Source": ("source", NoticeModel.Source),
    "IntermediaryType": ("intermediary_type", NoticeModel.IntermediaryType),
    "IntermediaryName": ("intermediary_name", NoticeModel.IntermediaryName),
}

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
    
    # 1. Sector Filter (Mandatory)
    query = query.filter(NoticeModel.sector == request.sector)
    
    # 2. Dynamic Field Filtering based on Sector Config
    valid_fields = SECTOR_FIELD_CONFIG.get(request.sector, [])
    
    for field_config in valid_fields:
        config_field_name = field_config["field"]
        
        if config_field_name in FIELD_MAPPING:
            req_field, db_col = FIELD_MAPPING[config_field_name]
            
            # Get values from request
            # Include filter
            include_vals = getattr(request, req_field, None)
            if include_vals:
                if config_field_name == "markettype":
                    # MarketType stored as string in DB, ensure string comparison
                    query = query.filter(db_col.in_([str(m) for m in include_vals]))
                else:
                    query = query.filter(db_col.in_(include_vals))
            
            # Exclude filter
            exclude_field = f"{req_field}_exclude"
            exclude_vals = getattr(request, exclude_field, None)
            if exclude_vals:
                if config_field_name == "markettype":
                    query = query.filter(db_col.notin_([str(m) for m in exclude_vals]))
                else:
                    query = query.filter(db_col.notin_(exclude_vals))
        
    # 3. Date Range (Global)
    if request.start_date and request.end_date:
        query = query.filter(
            NoticeModel.PublishDate >= request.start_date,
            NoticeModel.PublishDate <= request.end_date
        )
              
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

    # 4. Title Search (Global)
    if request.title_search_all:
        query = apply_keyword_filter(query, NoticeModel.Title, request.title_search_all, "all")
    if request.title_search_any:
        query = apply_keyword_filter(query, NoticeModel.Title, request.title_search_any, "any")
    if request.title_search_none:
        query = apply_keyword_filter(query, NoticeModel.Title, request.title_search_none, "none")
        
    # 5. Content Search (Preview) (Global)
    if request.content_search_all:
        query = apply_keyword_filter(query, NoticeModel.Preview, request.content_search_all, "all")
    if request.content_search_any:
        query = apply_keyword_filter(query, NoticeModel.Preview, request.content_search_any, "any")
    if request.content_search_none:
        query = apply_keyword_filter(query, NoticeModel.Preview, request.content_search_none, "none")
        
    # 6. AQ Search (List of strings) - Applied to Preview
    # aq_search_all: Each string in the list must be present in Preview
    if request.aq_search_all:
        for term in request.aq_search_all:
            if term:
                query = query.filter(NoticeModel.Preview.ilike(f"%{term}%"))
                
    # aq_search_any: At least one string in the list must be present in Preview
    if request.aq_search_any:
        conditions = [NoticeModel.Preview.ilike(f"%{term}%") for term in request.aq_search_any if term]
        if conditions:
            query = query.filter(or_(*conditions))
            
    # aq_search_none: None of the strings in the list should be present in Preview
    if request.aq_search_none:
        for term in request.aq_search_none:
            if term:
                query = query.filter(~NoticeModel.Preview.ilike(f"%{term}%"))
        
    # Total count (slow on large dataset, maybe optimize later)
    total = query.count()
    
    # Sort
    query = query.order_by(NoticeModel.PublishDate.desc())
    
    # Pagination
    notices = query.offset((current_page - 1) * current_page_size).limit(current_page_size).all()
    
    # 6. Facets Implementation (Dynamic)
    facets = {}
    
    for field_config in valid_fields:
        config_field_name = field_config["field"]
        
        if config_field_name not in FIELD_MAPPING:
            continue
            
        _, db_col = FIELD_MAPPING[config_field_name]
        
        # Special handling for StockCode (Code + Ticker)
        if config_field_name == "StockCode":
            # 1. Count distinct entities
            publish_entity_count = query.with_entities(NoticeModel.StockCode).distinct().count()
            facets["publish_entity_count"] = publish_entity_count
            config_field_name = "publish_entity" if request.sector != "辅导信息" else "StockCode"
            
            # 2. Top entities
            agg_query = query.with_entities(
                 NoticeModel.StockCode, 
                 func.max(NoticeModel.StockTicker), 
                 func.count(NoticeModel.StockCode)
             ).group_by(NoticeModel.StockCode).order_by(func.count(NoticeModel.StockCode).desc()).limit(50)
             
            results = agg_query.all()
            facets[config_field_name] = [
                 {"name": f"{r[0]} {r[1] if r[1] else ''}".strip(), "count": r[2], "StockCode": r[0]} 
                 for r in results if r[0] is not None
            ]
        else:
            # Standard aggregation
            agg_query = query.with_entities(db_col, func.count(db_col)).group_by(db_col).order_by(func.count(db_col).desc()).limit(50)
            
            results = agg_query.all()
            
            facets[config_field_name] = [
                {"name": str(r[0]), "count": r[1]} 
                for r in results if r[0] is not None
            ]
    
    return {
        "total": total,
        "data": notices,
        "facets": facets
    }

@app.post("/notices/search", response_model=GlobalSearchResponse)
async def global_search_notices(
    keyword: str = Query(..., min_length=1, description="Search keyword"),
    limit: int = Query(20, ge=1, le=100, description="Items per sector"),
    page: int = Query(1, ge=1, description="Page number"),
    stock_code: Optional[str] = Query(None, description="Filter by stock code"),
    start_date: Optional[str] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[str] = Query(None, description="End date (inclusive)"),
    order_by: str = Query("desc", description="Sort order: 'desc' (newest), 'asc' (oldest), 'company' (company aggregation)"),
    db_session: Session = Depends(get_db)
):
    """
    Global search for notices across all sectors.
    Returns top {limit} results for each sector where keyword matches.
    Matches against: Title, StockCode, StockTicker, NoticeType, Publisher
    """
    keyword_like = f"%{keyword}%"
    
    # Base query filters (Date and StockCode)
    filters = []
    
    if stock_code:
        filters.append(NoticeModel.StockCode == stock_code)
        
    if start_date and end_date:
        filters.append(NoticeModel.PublishDate >= start_date)
        filters.append(NoticeModel.PublishDate <= end_date)
    
    # 1. Get all sectors that have matches
    # We want to search across multiple columns.
    # Condition: Title LIKE %k% OR StockCode LIKE %k% OR ...
    
    search_condition = or_(
        NoticeModel.Title.ilike(keyword_like),
        NoticeModel.StockCode.ilike(keyword_like),
        NoticeModel.StockTicker.ilike(keyword_like),
        NoticeModel.NoticeType.ilike(keyword_like),
        NoticeModel.Publisher.ilike(keyword_like),
        NoticeModel.Category.ilike(keyword_like),
        NoticeModel.Industry.ilike(keyword_like),
        NoticeModel.MarketType.ilike(keyword_like),
        NoticeModel.Province.ilike(keyword_like),
        NoticeModel.Institutions.ilike(keyword_like),
        NoticeModel.Source.ilike(keyword_like),
        NoticeModel.IntermediaryName.ilike(keyword_like),
        NoticeModel.Preview.ilike(keyword_like)
    )
    
    # Combine all filters
    full_condition = search_condition
    for f in filters:
        full_condition = (full_condition) & (f)
    
    # Get counts per sector
    sector_counts = db_session.query(
        NoticeModel.sector, 
        func.count(NoticeModel.id)
    ).filter(full_condition).group_by(NoticeModel.sector).all()
    
    results = {}
    
    # 2. For each sector, fetch top N items
    for sector, count in sector_counts:
        if not sector:
            continue
            
        query = db_session.query(NoticeModel).filter(
            NoticeModel.sector == sector,
            full_condition
        )
        
        if order_by == "company":
            # Aggregate by company (StockCode), sort by date desc within company
            query = query.order_by(NoticeModel.StockCode.asc(), NoticeModel.PublishDate.desc())
        elif order_by == "asc":
            query = query.order_by(NoticeModel.PublishDate.asc())
        else: # desc
            query = query.order_by(NoticeModel.PublishDate.desc())
            
        items = query.offset((page - 1) * limit).limit(limit).all()
        
        # Convert SQLAlchemy objects to dicts to avoid Pydantic validation errors
        # if the model fields don't match exactly 1:1 or if there are extra fields
        items_dict = []
        for item in items:
            # Use __dict__ but remove internal SA state
            d = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
            items_dict.append(d)
        
        results[sector] = SectorSearchGroup(
            sector=sector,
            total=count,
            data=items_dict
        )
        
    return GlobalSearchResponse(results=results)

@app.post("/notices/favorite", response_model=FavoriteNoticeResponse)
async def toggle_favorite_notices(request: FavoriteNoticeRequest, db_session: Session = Depends(get_db)):
    """
    Toggle favorite status for multiple notices. 
    If a notice is favorite, remove it. If not, add it.
    """
    user_id = "default_user"
    results = []
    
    # 1. Fetch all target notices at once
    notices = db_session.query(NoticeModel).filter(NoticeModel.id.in_(request.notice_ids)).all()
    notice_map = {n.id: n for n in notices}
    
    # 2. Fetch all existing favorites for these notices
    existing_favs = db_session.query(FavoriteNoticeModel).filter(
        FavoriteNoticeModel.notice_id.in_(request.notice_ids),
        FavoriteNoticeModel.user_id == user_id
    ).all()
    fav_map = {f.notice_id: f for f in existing_favs}
    
    current_time = datetime.datetime.now().isoformat()
    
    for notice_id in request.notice_ids:
        notice = notice_map.get(notice_id)
        if not notice:
            results.append({
                "notice_id": notice_id,
                "status": "not_found"
            })
            continue
            
        existing_fav = fav_map.get(notice_id)
        
        if existing_fav:
            # Remove
            db_session.delete(existing_fav)
            notice.IsFav = "0"
            
            results.append({
                "id": existing_fav.id,
                "notice_id": notice_id,
                "status": "removed"
            })
        else:
            # Add
            fav_id = str(uuid.uuid4())
            new_fav = FavoriteNoticeModel(
                id=fav_id,
                notice_id=notice_id,
                user_id=user_id,
                create_time=current_time
            )
            db_session.add(new_fav)
            notice.IsFav = "1"
            
            results.append({
                "id": fav_id,
                "notice_id": notice_id,
                "status": "added"
            })
    
    db_session.commit()
    
    return {"results": results}

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
    title_search_all: Optional[str] = Query(None, description="All keywords match in title"),
    title_search_any: Optional[str] = Query(None, description="Any keywords match in title"),
    title_search_none: Optional[str] = Query(None, description="No keywords match in title"),
    category_name: Optional[List[str]] = Query(None, description="Filter by category_name"),
    category_name_exclude: Optional[List[str]] = Query(None, description="Exclude by category_name"),
    start_date: Optional[str] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[str] = Query(None, description="End date (inclusive)"),
    db_session: Session = Depends(get_db)
):
    query = db_session.query(TimelineDetailModel).filter(TimelineDetailModel.stockCode == stock_code)
    

    # Date Range
    if start_date and end_date:
        query = query.filter(
            TimelineDetailModel.publishDate >= start_date,
            TimelineDetailModel.publishDate <= end_date
        )
    
    # Category Filter
    if category_name:
        query = query.filter(TimelineDetailModel.category_name.in_(category_name))
    if category_name_exclude:
        query = query.filter(TimelineDetailModel.category_name.notin_(category_name_exclude))
    
    # Helper for keyword filtering (reused from notices logic basically)
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
    if title_search_all:
        query = apply_keyword_filter(query, TimelineDetailModel.title, title_search_all, "all")
    if title_search_any:
        query = apply_keyword_filter(query, TimelineDetailModel.title, title_search_any, "any")
    if title_search_none:
        query = apply_keyword_filter(query, TimelineDetailModel.title, title_search_none, "none")
    
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    
    # Facets: category_name counts
    # We need to compute counts for all categories based on the current filter (excluding category_name filter itself? usually facets respect other filters)
    # But usually facets show distribution. 
    # Let's count grouping by category_name
    facet_query = query.with_entities(TimelineDetailModel.category_name, func.count(TimelineDetailModel.category_name)).group_by(TimelineDetailModel.category_name)
    facet_results = facet_query.all()
    
    category_facets = [
        {"name": r[0], "count": r[1]} for r in facet_results if r[0]
    ]
    
    return {
        "total": total,
        "data": items,
        "facets": {"category_name": category_facets}
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
