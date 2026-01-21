from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict

# 1. Company Detail Model
class Company(BaseModel):
    id: Optional[str] = None
    Market: Optional[int] = None
    MarketName: Optional[str] = None
    Ticker: Optional[str] = None
    accFirm: Optional[str] = None
    address: Optional[str] = None
    briefing: Optional[str] = None
    businessScope: Optional[str] = None
    chairman: Optional[str] = None
    city: Optional[str] = None
    compProperty: Optional[str] = None
    country: Optional[str] = None
    cpa: Optional[str] = None
    discloser: Optional[str] = None
    email: Optional[str] = None
    employees: Optional[float] = None
    engName: Optional[str] = None
    fax: Optional[str] = None
    foundDate: Optional[str] = None
    ind1: Optional[str] = None
    ind2: Optional[str] = None
    indexMem: Optional[str] = None
    ipoAmount: Optional[float] = None
    ipoAnnDate: Optional[str] = None
    ipoCollection: Optional[float] = None
    ipoDilutedPe: Optional[float] = None
    ipoFee: Optional[float] = None
    ipoPrice: Optional[float] = None
    isMargin: Optional[str] = None
    isShort: Optional[str] = None
    isShsc: Optional[str] = None
    isVie: Optional[str] = None
    issueType: Optional[str] = None
    lawFirm: Optional[str] = None
    listBoard: Optional[str] = None
    listDate: Optional[str] = None
    mainBusiness: Optional[str] = None
    name: Optional[str] = None
    office: Optional[str] = None
    phone: Optional[str] = None
    preNames: Optional[str] = None
    president: Optional[str] = None
    prov: Optional[str] = None
    regCapital: Optional[float] = None
    registerNumber: Optional[str] = None
    sName: Optional[str] = None
    secretary: Optional[str] = None
    solSig: Optional[str] = None
    sponRep: Optional[str] = None
    sponSor: Optional[str] = None
    stockCode: Optional[str] = None
    swInd1: Optional[str] = None
    swInd2: Optional[str] = None
    swInd3: Optional[str] = None
    underWriting: Optional[str] = None
    valPe: Optional[float] = None
    website: Optional[str] = None
    zipcode: Optional[str] = None

# 2. Notice Model
class Notice(BaseModel):
    id: Optional[str] = None
    Administration: Optional[str] = None
    Availability: Optional[str] = None
    Category: Optional[str] = None
    DocumentKey: Optional[str] = None
    DocumentNo: Optional[str] = None
    EncryptionKey: Optional[str] = None
    FileType: Optional[str] = None # int in csv? keep flexible
    Href: Optional[str] = None
    Industry: Optional[str] = None
    Institutions: Optional[str] = None
    IntermediaryName: Optional[str] = None
    IntermediaryType: Optional[str] = None
    IsDir: Optional[str] = None
    IsExtracted: Optional[str] = None
    IsFav: Optional[str] = None
    Key: Optional[str] = None
    LawType: Optional[str] = None
    MarketType: Optional[str] = None
    NoticeType: Optional[str] = None
    ParentIndustry: Optional[str] = None
    Preview: Optional[str] = None
    Province: Optional[str] = None
    PublishDate: Optional[str] = None
    Publisher: Optional[str] = None
    Source: Optional[Any] = None
    SourcePath: Optional[str] = None
    StockCode: Optional[str] = None
    StockTicker: Optional[str] = None
    Title: Optional[str] = None
    TotalPage: Optional[str] = None
    Url: Optional[str] = None
    sector: Optional[str] = None

# 3. Event Model
class Event(BaseModel):
    id: Optional[str] = None 
    companies: Optional[str] = None
    count: Optional[int] = None
    en_title: Optional[str] = None
    event_id: Optional[str] = None
    heat: Optional[float] = None
    market: Optional[str] = None 
    max_publish_date: Optional[str] = None
    min_publish_date: Optional[str] = None
    sentiment: Optional[str] = None
    title: Optional[str] = None

# 4. News Model
class News(BaseModel):
    id: Optional[str] = None
    count: Optional[int] = None
    enTitle: Optional[str] = None
    event_id: Optional[str] = None
    newsId: Optional[str] = None
    source: Optional[str] = None
    time: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    inforId: Optional[str] = None # Added for DB consistency

# 5. IPO Data Models
class IPORank(BaseModel):
    id: Optional[str] = None
    AcceptDate: Optional[str] = None
    AccountingFirm: Optional[str] = None
    CurrentStatuses: Optional[str] = None
    Entity: Optional[str] = None
    HasQa: Optional[int] = None
    Industry: Optional[str] = None
    LastUpdateDate: Optional[str] = None
    LawFirm: Optional[str] = None
    ListingMarket: Optional[str] = None
    OnsiteInspection: Optional[str] = None
    Rank: Optional[int] = None
    Region: Optional[str] = None
    RelatedDocuments: Optional[str] = None
    ReviewQuestions: Optional[str] = None
    Reviewers: Optional[str] = None
    Sector: Optional[int] = None
    Sponsor: Optional[str] = None
    address: Optional[str] = None
    balanceSheet: Optional[str] = None
    boardSecretary: Optional[str] = None
    businessRegistration: Optional[str] = None
    businessScope: Optional[str] = None
    cashflowStatement: Optional[str] = None
    category: Optional[str] = None
    chairman: Optional[str] = None
    compName: Optional[str] = None
    compType: Optional[str] = None
    companyIntroduction: Optional[str] = None
    country: Optional[str] = None
    currentTicker: Optional[str] = None
    email: Optional[str] = None
    engName: Optional[str] = None
    establishingTime: Optional[str] = None
    fax: Optional[str] = None
    generalManager: Optional[str] = None
    incomeStatement: Optional[str] = None
    ipoCompRFA: Optional[str] = None
    isListed: Optional[int] = None
    lawOffice: Optional[str] = None
    legalRepresentative: Optional[str] = None
    listBoard: Optional[str] = None
    netAmountOfRaisedFunds: Optional[float] = None
    numberEmployees: Optional[int] = None
    registeredAddress: Optional[str] = None
    registeredAssets: Optional[float] = None
    registeredCapital: Optional[float] = None
    sName: Optional[str] = None
    stockCode: Optional[str] = None
    telePhone: Optional[str] = None
    timingPlan: Optional[str] = None
    topTenShareholders: Optional[str] = None
    updateTime: Optional[str] = None
    website: Optional[str] = None

class IPOTimeline(BaseModel):
    id: Optional[str] = None
    Source: Optional[str] = None
    Title: Optional[str] = None
    Content: Optional[str] = None
    PublishDate: Optional[str] = None
    Url: Optional[str] = None

class IPOData(BaseModel):
    id: Optional[str] = None
    Issuer: Optional[str] = None
    LatestDate: Optional[str] = None
    ListingMarket: Optional[str] = None
    Status: Optional[str] = None
    address: Optional[str] = None
    balanceSheet: Optional[str] = None
    boardSecretary: Optional[str] = None
    businessRegistration: Optional[str] = None
    businessScope: Optional[str] = None
    cashflowStatement: Optional[str] = None
    category: Optional[str] = None
    chairman: Optional[str] = None
    compName: Optional[str] = None
    compType: Optional[str] = None
    companyIntroduction: Optional[str] = None
    country: Optional[str] = None
    currentTicker: Optional[str] = None
    email: Optional[str] = None
    engName: Optional[str] = None
    establishingTime: Optional[str] = None
    fax: Optional[str] = None
    generalManager: Optional[str] = None
    incomeStatement: Optional[str] = None
    industry: Optional[str] = None
    ipoCompRFA: Optional[str] = None
    isListed: Optional[int] = None
    lawOffice: Optional[str] = None
    legalRepresentative: Optional[str] = None
    listBoard: Optional[str] = None
    netAmountOfRaisedFunds: Optional[float] = None
    numberEmployees: Optional[int] = None
    registeredAddress: Optional[str] = None
    registeredAssets: Optional[float] = None
    registeredCapital: Optional[float] = None
    sName: Optional[str] = None
    stockCode: Optional[str] = None
    telePhone: Optional[str] = None
    timeline: Optional[Any] = None # List[IPOTimeline] or JSON string
    timingPlan: Optional[str] = None
    topTenShareholders: Optional[str] = None
    updateTime: Optional[str] = None
    website: Optional[str] = None

class IPODataBasic(BaseModel):
    id: Optional[str] = None
    Issuer: Optional[str] = None
    ListingMarket: Optional[str] = None
    LatestDate: Optional[str] = None
    Status: Optional[str] = None
    timeline: Optional[Any] = None

class IPOListResponse(BaseModel):
    total: int
    data: List[IPODataBasic]

class IPORankBasic(BaseModel):
    id: Optional[str] = None
    Rank: Optional[int] = None
    ListingMarket: Optional[str] = None
    Entity: Optional[str] = None
    Sponsor: Optional[str] = None
    AccountingFirm: Optional[str] = None
    LawFirm: Optional[str] = None
    AcceptDate: Optional[str] = None
    CurrentStatuses: Optional[str] = None
    LastUpdateDate: Optional[str] = None
    Reviewers: Optional[str] = None
    RelatedDocuments: Optional[str] = None

class IPORankListResponse(BaseModel):
    total: int
    data: List[IPORankBasic]

# 6. Timeline Detail Model
class TimelineDetail(BaseModel):
    id: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    documentId: Optional[str] = None
    documentKey: Optional[str] = None
    fileType: Optional[int] = None
    process_result: Optional[str] = None
    publishDate: Optional[str] = None
    sector: Optional[int] = None
    stockCode: Optional[str] = None
    stockTicker: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    year: Optional[int] = None

class TimelineDetailListResponse(BaseModel):
    total: int
    data: List[TimelineDetail]
    facets: Optional[Dict[str, Any]] = None

# 7. IPO Review Model
class IPOReview(BaseModel):
    id: Optional[str] = None
    CurrentStatuses: Optional[str] = None
    Entity: Optional[str] = None
    HasQa: Optional[int] = None
    LastUpdateDate: Optional[str] = None
    Rank: Optional[int] = None
    RelatedDocuments: Optional[str] = None
    ReviewQuestions: Optional[str] = None
    ReviewStatus: Optional[str] = None
    Reviewers: Optional[str] = None
    Sector: Optional[int] = None
    address: Optional[str] = None
    balanceSheet: Optional[str] = None
    boardSecretary: Optional[str] = None
    businessRegistration: Optional[str] = None
    businessScope: Optional[str] = None
    cashflowStatement: Optional[str] = None
    chairman: Optional[str] = None
    compName: Optional[str] = None
    compType: Optional[str] = None
    companyIntroduction: Optional[str] = None
    country: Optional[str] = None
    currentTicker: Optional[str] = None
    email: Optional[str] = None
    engName: Optional[str] = None
    establishingTime: Optional[str] = None
    fax: Optional[str] = None
    generalManager: Optional[str] = None
    incomeStatement: Optional[str] = None
    industry: Optional[str] = None
    ipoCompRFA: Optional[str] = None
    isListed: Optional[int] = None
    lawOffice: Optional[str] = None
    legalRepresentative: Optional[str] = None
    listBoard: Optional[str] = None
    listingMarket: Optional[str] = None
    netAmountOfRaisedFunds: Optional[float] = None
    numberEmployees: Optional[int] = None
    registeredAddress: Optional[str] = None
    registeredAssets: Optional[float] = None
    registeredCapital: Optional[float] = None
    sName: Optional[str] = None
    stockCode: Optional[str] = None
    telePhone: Optional[str] = None
    timingPlan: Optional[str] = None
    topTenShareholders: Optional[str] = None
    updateTime: Optional[str] = None
    website: Optional[str] = None

class IPOReviewBasic(BaseModel):
    id: Optional[str] = None
    Rank: Optional[int] = None
    Entity: Optional[str] = None
    CurrentStatuses: Optional[str] = None
    LastUpdateDate: Optional[str] = None
    ReviewStatus: Optional[str] = None
    Reviewers: Optional[str] = None
    ReviewQuestions: Optional[str] = None

class IPOReviewListResponse(BaseModel):
    total: int
    data: List[IPOReviewBasic]

# Response Models (List wrappers)
class CompanyBaseItem(BaseModel):
    id: str
    label: str
    stockCode: Optional[str] = None
    ticker: Optional[str] = None

class SectorSearchGroup(BaseModel):
    sector: str
    total: int
    data: List[Dict[str, Any]] # Can be Notice dict or Company Aggregation dict

class GlobalSearchResponse(BaseModel):
    results: Dict[str, SectorSearchGroup] # Key is sector name


class FacetItem(BaseModel):
    name: str
    count: int
    StockCode: Optional[str] = None

class Facets(BaseModel):
    publish_entity: List[FacetItem] = []
    publish_entity_count: int = 0 
    Category: List[FacetItem] = []
    NoticeType: List[FacetItem] = []
    Industry: List[FacetItem] = []
    MarketType: List[FacetItem] = []
    Province: List[FacetItem] = []
    Institutions: List[FacetItem] = []
    Source: List[FacetItem] = []
    IntermediaryType: List[FacetItem] = []
    IntermediaryName: List[FacetItem] = []

class NoticeListResponse(BaseModel):
    total: int
    data: List[Notice]
    facets: Optional[Dict[str, Any]] = None

class NoticeFilterRequest(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sector: str = Field(..., description="The sector name")
    
    # Common filters
    stock_code: Optional[List[str]] = None
    category: Optional[List[str]] = None
    notice_type: Optional[List[str]] = None
    industry: Optional[List[str]] = None
    market_type: Optional[List[str]] = None
    province: Optional[List[str]] = None
    
    # New filters from config
    publisher: Optional[List[str]] = None # issuer
    institutions: Optional[List[str]] = None
    source: Optional[List[str]] = None
    intermediary_type: Optional[List[str]] = None
    intermediary_name: Optional[List[str]] = None
    
    # Exclude filters
    stock_code_exclude: Optional[List[str]] = None
    category_exclude: Optional[List[str]] = None
    notice_type_exclude: Optional[List[str]] = None
    industry_exclude: Optional[List[str]] = None
    market_type_exclude: Optional[List[str]] = None
    province_exclude: Optional[List[str]] = None
    
    publisher_exclude: Optional[List[str]] = None
    institutions_exclude: Optional[List[str]] = None
    source_exclude: Optional[List[str]] = None
    intermediary_type_exclude: Optional[List[str]] = None
    intermediary_name_exclude: Optional[List[str]] = None
    
    # New filters
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    title_search_all: Optional[str] = None
    title_search_any: Optional[str] = None
    title_search_none: Optional[str] = None
    
    content_search_all: Optional[str] = None
    content_search_any: Optional[str] = None
    content_search_none: Optional[str] = None
    
    # AQ Search (List of strings, each must be in Preview)
    aq_search_all: Optional[List[str]] = None
    aq_search_any: Optional[List[str]] = None
    aq_search_none: Optional[List[str]] = None

class EventListResponse(BaseModel):
    total: int
    data: List[Event]

class NewsListResponse(BaseModel):
    total: int
    data: List[News]

class InfoSource(BaseModel):
    id: Optional[str] = None # Unique identifier
    SourceName: Optional[str] = None
    SourceUrl: Optional[str] = None
    news: List[News] = []

class FavoriteNoticeRequest(BaseModel):
    notice_ids: List[str]

class FavoriteItemResponse(BaseModel):
    id: Optional[str] = None
    notice_id: str
    status: str # "added" or "removed" or "not_found"

class FavoriteNoticeResponse(BaseModel):
    results: List[FavoriteItemResponse]

class SectorInformation(BaseModel):
    sector: str
    information: List[InfoSource]
