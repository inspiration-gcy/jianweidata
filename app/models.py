from pydantic import BaseModel, Field
from typing import Optional, Any, List

# 1. Company Detail Model (Matches company_list_with_details.xlsx)
class Company(BaseModel):
    id: Optional[str] = None # Added unique ID
    MarketName: Optional[str] = None
    Market: Optional[int] = None
    stockCode: Optional[str] = None
    Ticker: Optional[str] = None
    name: Optional[str] = None
    sName: Optional[str] = None
    engName: Optional[str] = None
    preNames: Optional[str] = None
    briefing: Optional[str] = None
    businessScope: Optional[str] = None
    country: Optional[str] = None
    foundDate: Optional[str] = None
    compProperty: Optional[str] = None
    registerNumber: Optional[str] = None
    regCapital: Optional[float] = None
    chairman: Optional[str] = None
    mainBusiness: Optional[str] = None
    employees: Optional[float] = None
    president: Optional[str] = None
    secretary: Optional[str] = None
    prov: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    office: Optional[str] = None
    zipcode: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    discloser: Optional[str] = None
    accFirm: Optional[str] = None
    cpa: Optional[str] = None
    lawFirm: Optional[str] = None
    solSig: Optional[str] = None
    swInd1: Optional[str] = None
    swInd2: Optional[str] = None
    swInd3: Optional[str] = None
    ind1: Optional[str] = None
    ind2: Optional[str] = None
    indexMem: Optional[str] = None
    sponRep: Optional[str] = None
    sponSor: Optional[str] = None
    ipoPrice: Optional[float] = None
    ipoDilutedPe: Optional[float] = None
    ipoAmount: Optional[float] = None
    ipoAnnDate: Optional[str] = None
    listBoard: Optional[str] = None
    underWriting: Optional[str] = None
    issueType: Optional[str] = None
    valPe: Optional[float] = None
    ipoCollection: Optional[float] = None
    ipoFee: Optional[float] = None
    listDate: Optional[str] = None
    isVie: Optional[str] = None
    isShsc: Optional[str] = None
    isMargin: Optional[str] = None
    isShort: Optional[str] = None

# 2. Sector Notice Model
class Notice(BaseModel):
    id: Optional[str] = None # Added unique ID
    sector: Optional[str] = None
    StockCode: Optional[str] = None
    StockTicker: Optional[str] = None
    Title: Optional[str] = None
    NoticeType: Optional[str] = None
    Preview: Optional[str] = None
    Publisher: Optional[str] = None
    PublishDate: Optional[str] = None
    Url: Optional[str] = None
    Industry: Optional[str] = None
    ParentIndustry: Optional[str] = None
    Province: Optional[str] = None
    Source: Optional[Any] = None
    DocumentNo: Optional[str] = None
    Category: Optional[str] = None
    Administration: Optional[str] = None
    IntermediaryName: Optional[str] = None
    IntermediaryType: Optional[str] = None
    LawType: Optional[str] = None
    Institutions: Optional[str] = None
    MarketType: Optional[Any] = None # Could be int or str

# 3. Event Model
class Event(BaseModel):
    id: Optional[str] = None # Added unique ID
    event_id: Optional[str] = None
    en_title: Optional[str] = None
    market: Optional[str] = None # Changed from int to str
    title: Optional[str] = None
    min_publish_date: Optional[str] = None
    max_publish_date: Optional[str] = None
    count: Optional[int] = None
    heat: Optional[float] = None
    sentiment: Optional[float] = None
    companies: Optional[str] = None

# 4. News Model
class News(BaseModel):
    id: Optional[str] = None # Added unique ID
    newsId: Optional[str] = None
    enTitle: Optional[str] = None
    title: Optional[str] = None
    time: Optional[str] = None
    source: Optional[str] = None
    url: Optional[str] = None
    count: Optional[int] = None
    event_id: Optional[str] = None
    inforId: Optional[str] = None # Foreign key to InfoSource

# Response Models (List wrappers)
class CompanySearchItem(BaseModel):
    id: str
    label: str
    stockCode: Optional[str] = None
    ticker: Optional[str] = None

class FacetItem(BaseModel):
    name: str
    count: int

class Facets(BaseModel):
    publish_entity: List[FacetItem] = []
    Category: List[FacetItem] = []
    NoticeType: List[FacetItem] = []
    Industry: List[FacetItem] = []
    MarketType: List[FacetItem] = []
    Province: List[FacetItem] = []

class NoticeListResponse(BaseModel):
    total: int
    data: List[Notice]
    facets: Optional[Facets] = None

class NoticeFilterRequest(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    stock_code: Optional[List[str]] = None
    sector: Optional[str] = None # Changed to single string
    publish_entity: Optional[List[str]] = None
    category: Optional[List[str]] = None
    notice_type: Optional[List[str]] = None
    industry: Optional[List[str]] = None
    market_type: Optional[List[str]] = None
    province: Optional[List[str]] = None
    
    # New filters
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    company_search: Optional[str] = None # Fuzzy search for code/ticker
    
    title_search: Optional[str] = None
    title_match_mode: Optional[str] = "all" # all, any, none
    
    content_search: Optional[str] = None # Maps to Preview
    content_match_mode: Optional[str] = "all"

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

class SectorInformation(BaseModel):
    sector: str
    information: List[InfoSource]

# 5. IPO Data Models
class IPORank(BaseModel):
    id: Optional[str] = None # Added unique ID
    Rank: Optional[int] = None
    ListingMarket: Optional[str] = None
    Entity: Optional[str] = None
    Sponsor: Optional[str] = None
    AccountingFirm: Optional[str] = None
    LawFirm: Optional[str] = None
    Industry: Optional[str] = None
    Region: Optional[str] = None
    AcceptDate: Optional[str] = None
    CurrentStatuses: Optional[str] = None
    OnsiteInspection: Optional[str] = None # float/str
    RelatedDocuments: Optional[str] = None
    Reviewers: Optional[str] = None
    LastUpdateDate: Optional[str] = None
    ReviewQuestions: Optional[str] = None
    Sector: Optional[int] = None
    HasQa: Optional[int] = None
    
    # Financials (JSON strings)
    balanceSheet: Optional[str] = None
    incomeStatement: Optional[str] = None
    cashflowStatement: Optional[str] = None
    
    # Extended details
    stockCode: Optional[str] = None
    registeredCapital: Optional[float] = None
    establishingTime: Optional[str] = None
    compName: Optional[str] = None
    engName: Optional[str] = None
    registeredAddress: Optional[str] = None
    legalRepresentative: Optional[str] = None
    generalManager: Optional[str] = None
    boardSecretary: Optional[str] = None
    registeredAssets: Optional[float] = None
    telePhone: Optional[str] = None
    fax: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    companyIntroduction: Optional[str] = None
    businessScope: Optional[str] = None
    currentTicker: Optional[str] = None
    listBoard: Optional[str] = None
    lawOffice: Optional[str] = None
    sName: Optional[str] = None
    industry: Optional[str] = None # Note: Duplicate field name in source (Industry vs industry), model handles case-sensitivity? Pydantic fields are case-sensitive.
    chairman: Optional[str] = None
    email: Optional[str] = None
    numberEmployees: Optional[int] = None
    country: Optional[str] = None
    compType: Optional[str] = None
    netAmountOfRaisedFunds: Optional[float] = None
    businessRegistration: Optional[str] = None
    isListed: Optional[int] = None
    topTenShareholders: Optional[str] = None
    updateTime: Optional[str] = None
    listingMarket: Optional[str] = None # Lowercase version
    ipoCompRFA: Optional[str] = None
    timingPlan: Optional[str] = None
    # Dropped: region, securitiesType, mainBusinessScope, independentDirector, accountingFirm (lowercase), city, seniorExecutive, listedExchange, refiOrMergeInfo

class IPOTimeline(BaseModel):
    id: Optional[str] = None # Added unique ID
    Source: Optional[str] = None
    Title: Optional[str] = None
    Content: Optional[str] = None
    PublishDate: Optional[str] = None
    Url: Optional[str] = None

class IPOData(BaseModel):
    id: Optional[str] = None # Added unique ID
    Issuer: Optional[str] = None
    ListingMarket: Optional[str] = None
    LatestDate: Optional[str] = None
    Status: Optional[str] = None
    timeline: Optional[List[IPOTimeline]] = None
    
    stockCode: Optional[str] = None
    registeredCapital: Optional[float] = None
    establishingTime: Optional[str] = None
    compName: Optional[str] = None
    engName: Optional[str] = None
    registeredAddress: Optional[str] = None
    legalRepresentative: Optional[str] = None
    generalManager: Optional[str] = None
    boardSecretary: Optional[str] = None
    registeredAssets: Optional[float] = None
    telePhone: Optional[str] = None
    fax: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    companyIntroduction: Optional[str] = None
    businessScope: Optional[str] = None
    currentTicker: Optional[str] = None
    listBoard: Optional[str] = None
    lawOffice: Optional[str] = None
    sName: Optional[str] = None
    industry: Optional[str] = None
    chairman: Optional[str] = None
    email: Optional[str] = None
    numberEmployees: Optional[int] = None
    country: Optional[str] = None
    compType: Optional[str] = None
    netAmountOfRaisedFunds: Optional[float] = None
    businessRegistration: Optional[str] = None
    isListed: Optional[int] = None
    topTenShareholders: Optional[str] = None # JSON string or list
    updateTime: Optional[str] = None
    ipoCompRFA: Optional[str] = None
    timingPlan: Optional[str] = None
    
    # Financials (JSON strings)
    balanceSheet: Optional[str] = None
    incomeStatement: Optional[str] = None
    cashflowStatement: Optional[str] = None

class IPODataBasic(BaseModel):
    id: Optional[str] = None
    Issuer: Optional[str] = None
    ListingMarket: Optional[str] = None
    LatestDate: Optional[str] = None
    Status: Optional[str] = None
    timeline: Optional[List[IPOTimeline]] = None

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
    stockCode: Optional[str] = None
    year: Optional[int] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    stockTicker: Optional[str] = None
    sector: Optional[int] = None
    documentId: Optional[str] = None
    documentKey: Optional[str] = None
    fileType: Optional[int] = None
    publishDate: Optional[str] = None
    process_result: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None

class TimelineDetailListResponse(BaseModel):
    total: int
    data: List[TimelineDetail]

# 7. IPO Review Model
class IPOReview(BaseModel):
    id: Optional[str] = None
    Rank: Optional[int] = None
    Entity: Optional[str] = None
    CurrentStatuses: Optional[str] = None
    RelatedDocuments: Optional[str] = None # JSON string
    Reviewers: Optional[str] = None # JSON string
    LastUpdateDate: Optional[str] = None
    ReviewStatus: Optional[str] = None
    ReviewQuestions: Optional[str] = None # JSON string
    Sector: Optional[int] = None
    HasQa: Optional[int] = None
    
    # Financials (JSON strings)
    balanceSheet: Optional[str] = None
    incomeStatement: Optional[str] = None
    cashflowStatement: Optional[str] = None
    
    # Company Details
    stockCode: Optional[str] = None
    registeredCapital: Optional[float] = None
    establishingTime: Optional[str] = None
    compName: Optional[str] = None
    engName: Optional[str] = None
    registeredAddress: Optional[str] = None
    legalRepresentative: Optional[str] = None
    generalManager: Optional[str] = None
    boardSecretary: Optional[str] = None
    registeredAssets: Optional[float] = None
    telePhone: Optional[str] = None
    fax: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    companyIntroduction: Optional[str] = None
    businessScope: Optional[str] = None
    currentTicker: Optional[str] = None
    listBoard: Optional[str] = None
    lawOffice: Optional[str] = None
    sName: Optional[str] = None
    industry: Optional[str] = None
    chairman: Optional[str] = None
    email: Optional[str] = None
    numberEmployees: Optional[int] = None
    country: Optional[str] = None
    compType: Optional[str] = None
    netAmountOfRaisedFunds: Optional[float] = None
    businessRegistration: Optional[str] = None
    isListed: Optional[int] = None
    topTenShareholders: Optional[str] = None
    updateTime: Optional[str] = None
    listingMarket: Optional[str] = None
    ipoCompRFA: Optional[str] = None
    timingPlan: Optional[str] = None

class IPOReviewBasic(BaseModel):
    id: Optional[str] = None
    Rank: Optional[int] = None
    Entity: Optional[str] = None
    CurrentStatuses: Optional[str] = None
    LastUpdateDate: Optional[str] = None
    ReviewStatus: Optional[str] = None

class IPOReviewListResponse(BaseModel):
    total: int
    data: List[IPOReviewBasic]
