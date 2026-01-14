from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL (SQLite)
DATABASE_URL = "sqlite:///./jianweidata.db"

# Create Engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

# --- Models ---

class CompanyModel(Base):
    __tablename__ = "companies"
    
    id = Column(String, primary_key=True, index=True)
    stockCode = Column(String, index=True)
    Ticker = Column(String, index=True)
    Market = Column(Integer, index=True)
    MarketName = Column(String)
    name = Column(String)
    sName = Column(String)
    engName = Column(String)
    preNames = Column(String)
    briefing = Column(Text)
    businessScope = Column(Text)
    country = Column(String)
    foundDate = Column(String)
    compProperty = Column(String)
    registerNumber = Column(String)
    regCapital = Column(Float)
    chairman = Column(String)
    mainBusiness = Column(Text)
    employees = Column(Float)
    president = Column(String)
    secretary = Column(String)
    prov = Column(String)
    city = Column(String)
    address = Column(String)
    office = Column(String)
    zipcode = Column(String)
    phone = Column(String)
    fax = Column(String)
    email = Column(String)
    website = Column(String)
    discloser = Column(String)
    accFirm = Column(String)
    cpa = Column(String)
    lawFirm = Column(String)
    solSig = Column(String)
    swInd1 = Column(String)
    swInd2 = Column(String)
    swInd3 = Column(String)
    ind1 = Column(String)
    ind2 = Column(String)
    indexMem = Column(String)
    sponRep = Column(String)
    sponSor = Column(String)
    ipoPrice = Column(Float)
    ipoDilutedPe = Column(Float)
    ipoAmount = Column(Float)
    ipoAnnDate = Column(String)
    listBoard = Column(String)
    underWriting = Column(String)
    issueType = Column(String)
    valPe = Column(Float)
    ipoCollection = Column(Float)
    ipoFee = Column(Float)
    listDate = Column(String)
    isVie = Column(String)
    isShsc = Column(String)
    isMargin = Column(String)
    isShort = Column(String)

class NoticeModel(Base):
    __tablename__ = "notices"
    
    id = Column(String, primary_key=True, index=True)
    sector = Column(String, index=True)
    StockCode = Column(String, index=True)
    StockTicker = Column(String, index=True)
    Title = Column(String, index=True)
    NoticeType = Column(String, index=True)
    Preview = Column(Text)
    Publisher = Column(String, index=True)
    PublishDate = Column(String, index=True)
    Url = Column(String)
    Industry = Column(String, index=True)
    ParentIndustry = Column(String)
    Province = Column(String, index=True)
    Source = Column(Text) # JSON or string
    DocumentNo = Column(String)
    Category = Column(String, index=True)
    Administration = Column(String)
    IntermediaryName = Column(String)
    IntermediaryType = Column(String)
    LawType = Column(String)
    Institutions = Column(String)
    MarketType = Column(String, index=True) # Stored as string

class EventModel(Base):
    __tablename__ = "events"
    
    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, index=True)
    en_title = Column(String)
    market = Column(String, index=True)
    title = Column(String)
    min_publish_date = Column(String)
    max_publish_date = Column(String)
    count = Column(Integer)
    heat = Column(Float)
    sentiment = Column(String) # Changed from Float to String
    companies = Column(Text)

class NewsModel(Base):
    __tablename__ = "news"
    
    id = Column(String, primary_key=True, index=True)
    newsId = Column(String, index=True)
    enTitle = Column(String)
    title = Column(String)
    time = Column(String, index=True)
    source = Column(String)
    url = Column(String)
    count = Column(Integer)
    event_id = Column(String, index=True)
    inforId = Column(String, index=True)

class SectorInfoModel(Base):
    __tablename__ = "sector_info"
    
    id = Column(String, primary_key=True, index=True)
    Sector = Column(String, index=True)
    SourceName = Column(String)
    SourceUrl = Column(String)
    # News relationship handled by joining NewsModel via inforId

class IPODataModel(Base):
    __tablename__ = "ipo_data"
    
    id = Column(String, primary_key=True, index=True)
    Issuer = Column(String, index=True)
    ListingMarket = Column(String, index=True)
    LatestDate = Column(String, index=True)
    Status = Column(String, index=True)
    timeline = Column(Text) # JSON string
    category = Column(String, index=True)
    
    stockCode = Column(String)
    registeredCapital = Column(Float)
    establishingTime = Column(String)
    compName = Column(String)
    engName = Column(String)
    registeredAddress = Column(String)
    legalRepresentative = Column(String)
    generalManager = Column(String)
    boardSecretary = Column(String)
    registeredAssets = Column(Float)
    telePhone = Column(String)
    fax = Column(String)
    address = Column(String)
    website = Column(String)
    companyIntroduction = Column(Text)
    businessScope = Column(Text)
    currentTicker = Column(String)
    listBoard = Column(String)
    lawOffice = Column(String)
    sName = Column(String)
    industry = Column(String)
    chairman = Column(String)
    email = Column(String)
    numberEmployees = Column(Integer)
    country = Column(String)
    compType = Column(String)
    netAmountOfRaisedFunds = Column(Float)
    businessRegistration = Column(String)
    isListed = Column(Integer)
    topTenShareholders = Column(Text)
    updateTime = Column(String)
    ipoCompRFA = Column(String)
    timingPlan = Column(String)
    balanceSheet = Column(Text)
    incomeStatement = Column(Text)
    cashflowStatement = Column(Text)

class IPORankModel(Base):
    __tablename__ = "ipo_ranks"
    
    id = Column(String, primary_key=True, index=True)
    Rank = Column(Integer)
    ListingMarket = Column(String)
    Entity = Column(String, index=True)
    Sponsor = Column(String)
    AccountingFirm = Column(String)
    LawFirm = Column(String)
    Industry = Column(String)
    Region = Column(String)
    AcceptDate = Column(String)
    CurrentStatuses = Column(String)
    OnsiteInspection = Column(String)
    RelatedDocuments = Column(String)
    Reviewers = Column(String)
    LastUpdateDate = Column(String)
    ReviewQuestions = Column(String)
    Sector = Column(Integer)
    HasQa = Column(Integer)
    category = Column(String, index=True)
    
    stockCode = Column(String)
    registeredCapital = Column(Float)
    establishingTime = Column(String)
    compName = Column(String)
    engName = Column(String)
    registeredAddress = Column(String)
    legalRepresentative = Column(String)
    generalManager = Column(String)
    boardSecretary = Column(String)
    registeredAssets = Column(Float)
    telePhone = Column(String)
    fax = Column(String)
    address = Column(String)
    website = Column(String)
    companyIntroduction = Column(Text)
    businessScope = Column(Text)
    currentTicker = Column(String)
    listBoard = Column(String)
    lawOffice = Column(String)
    sName = Column(String)
    industry_detail = Column("industry_detail", String) # Rename to avoid conflict if needed, or map 'industry'
    chairman = Column(String)
    email = Column(String)
    numberEmployees = Column(Integer)
    country = Column(String)
    compType = Column(String)
    netAmountOfRaisedFunds = Column(Float)
    businessRegistration = Column(String)
    isListed = Column(Integer)
    topTenShareholders = Column(Text)
    updateTime = Column(String)
    listingMarket_detail = Column("listingMarket_detail", String)
    ipoCompRFA = Column(String)
    timingPlan = Column(String)
    balanceSheet = Column(Text)
    incomeStatement = Column(Text)
    cashflowStatement = Column(Text)

class TimelineDetailModel(Base):
    __tablename__ = "timeline_details"
    
    id = Column(String, primary_key=True, index=True)
    stockCode = Column(String, index=True)
    year = Column(Integer)
    category_id = Column(Integer)
    category_name = Column(String)
    stockTicker = Column(String)
    sector = Column(Integer)
    documentId = Column(String)
    documentKey = Column(String)
    fileType = Column(Integer)
    publishDate = Column(String)
    process_result = Column(String)
    title = Column(String)
    url = Column(String)

class IPOReviewModel(Base):
    __tablename__ = "ipo_reviews"
    
    id = Column(String, primary_key=True, index=True)
    Rank = Column(Integer)
    Entity = Column(String, index=True)
    CurrentStatuses = Column(String)
    RelatedDocuments = Column(Text)
    Reviewers = Column(Text)
    LastUpdateDate = Column(String)
    ReviewStatus = Column(String)
    ReviewQuestions = Column(Text)
    Sector = Column(Integer)
    HasQa = Column(Integer)
    
    stockCode = Column(String)
    registeredCapital = Column(Float)
    establishingTime = Column(String)
    compName = Column(String)
    engName = Column(String)
    registeredAddress = Column(String)
    legalRepresentative = Column(String)
    generalManager = Column(String)
    boardSecretary = Column(String)
    registeredAssets = Column(Float)
    telePhone = Column(String)
    fax = Column(String)
    address = Column(String)
    website = Column(String)
    companyIntroduction = Column(Text)
    businessScope = Column(Text)
    currentTicker = Column(String)
    listBoard = Column(String)
    lawOffice = Column(String)
    sName = Column(String)
    industry = Column(String)
    chairman = Column(String)
    email = Column(String)
    numberEmployees = Column(Integer)
    country = Column(String)
    compType = Column(String)
    netAmountOfRaisedFunds = Column(Float)
    businessRegistration = Column(String)
    isListed = Column(Integer)
    topTenShareholders = Column(Text)
    updateTime = Column(String)
    listingMarket = Column(String)
    ipoCompRFA = Column(String)
    timingPlan = Column(String)
    balanceSheet = Column(Text)
    incomeStatement = Column(Text)
    cashflowStatement = Column(Text)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
