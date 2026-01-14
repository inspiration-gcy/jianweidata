#健伟数据 API

这是一个基于 FastAPI 的数据服务后端，用于提供公司、公告、事件、新闻、IPO 等金融数据的查询接口。

## 项目简介

本项目使用 **SQLite** 数据库存储数据，通过 RESTful API 提供高效的检索和筛选服务。原始数据来源于 CSV 文件，首次使用时需要将其导入数据库。

主要功能模块包括：
- **公司信息 (Companies)**: A股公司基本信息、工商详情。
- **公告 (Notices)**: 上市公司公告检索（支持多条件筛选、关键词搜索）。
- **事件 (Events)**: 市场热点事件。
- **新闻 (News)**: 相关财经新闻。
- **IPO 数据**: IPO 排队、审核、发行等全流程数据。
- **时间轴详情 (Timeline)**: 股票相关的时间轴事件。

## 环境准备

建议使用 Python 3.9+ 环境。

1. **创建虚拟环境**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # venv\Scripts\activate  # Windows
   ```

2. **安装依赖**
   ```bash
   pip install fastapi uvicorn pandas openpyxl sqlalchemy
   ```

## 数据准备

项目默认从 `data/` 目录加载数据。该目录应包含以下核心 CSV 文件：
- `company.csv`
- `event.csv`
- `news.csv`
- `sector_info.csv`
- `ipo_data.csv`
- `ipo_rank.csv`
- `timeline_details.csv`
- `ipo_review.csv`
- `notice/` 目录：包含拆分后的公告数据 (`notice_all_part_*.csv`)

## 运行服务

使用 `manage.py` 管理脚本来启动服务。

### 1. 首次运行：导入数据
由于本项目改为使用 SQLite 数据库，**初次使用**或**数据更新**时，必须执行数据加载命令，将 CSV 数据导入 `jianweidata.db` 数据库文件。

#### 导入所有数据（默认追加，不清空旧数据）
```bash
python manage.py load
```
*注意：由于数据量较大（特别是公告数据），导入过程可能需要几分钟时间。导入完成后，会在当前目录生成 `jianweidata.db` 文件。*

#### 导入指定模型数据（自动清空旧数据）
如果只想更新特定表的数据（例如只更新 IPO 数据），可以使用 `--model` 参数。这会自动清空该表原有的数据并重新加载。

支持的模型名称：
- `CompanyModel` (公司信息)
- `NoticeModel` (公告)
- `EventModel` (事件)
- `NewsModel` (新闻)
- `SectorInfoModel` (行业信息，同时会重置关联新闻)
- `IPODataModel` (IPO 基础数据)
- `IPORankModel` (IPO 排队数据)
- `TimelineDetailModel` (时间轴详情)
- `IPOReviewModel` (IPO 审核数据)

示例：
```bash
python manage.py load --model IPODataModel
```

### 2. 启动服务
数据导入完成后，即可启动 API 服务。
```bash
python manage.py start
```
- 服务地址: http://127.0.0.1:8000
- 接口文档: http://127.0.0.1:8000/docs

### 3. 指定端口或目录
```bash
python manage.py start --port 8080 --dir /path/to/your/data
```

## API 接口说明

启动服务后，访问 Swagger UI 查看完整接口定义：
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

主要接口路径：
- `GET /companies`: 获取公司列表
- `GET /companies/search`: 模糊搜索公司
- `POST /notices`: 高级公告筛选（支持关键字、日期、行业等）
- `GET /events`: 获取事件列表
- `GET /news`: 获取新闻列表
- `GET /ipo/list`: 获取 IPO 基础列表
- `GET /ipo/rank/list`: 获取 IPO 排队列表

## 项目结构

```
.
├── app/
│   ├── db.py          # 数据库连接与 ORM 模型定义
│   ├── database.py    # 数据导入逻辑 (CSV -> SQLite)
│   ├── api.py         # API 路由与业务逻辑
│   └── models.py      # Pydantic 数据模型定义 (用于 API 响应)
├── data/              # 原始数据文件目录
│   └── notice/        # 公告拆分数据
├── manage.py          # 项目管理脚本 (CLI)
├── jianweidata.db     # SQLite 数据库文件 (自动生成)
└── README.md          # 项目文档
```
