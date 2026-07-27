# 港股智能分析平台

**HK Stock Intelligence Platform** 是一个本地可运行的港股智能分析系统，覆盖行情检索、K 线与技术指标、自选股、价格预警、新股表现统计、新股 AI 分析、财报/分红日历、AI 模型配置、用户登录注册和数据同步任务。

项目采用 Vue 3 + Spring Boot 3.2 + FastAPI + PostgreSQL，提供 Docker Compose 一键启动、Knife4j 接口文档、定时同步任务、JWT 用户认证和统一 API 响应结构，适合作为 Java 后端 / 全栈 / 金融科技方向作品集项目。

## 功能概览

### 核心功能

| 模块 | 功能说明 |
|------|----------|
| **大盘概览** | 展示港股市场整体行情与指数概览（恒生指数、恒生科技指数等） |
| **股票搜索** | 按代码、名称或板块模糊搜索，显示板块、市值、港股通标识 |
| **股票详情** | 展示 K 线（日K/周K/月K）、技术指标（MA/MACD/RSI/KDJ）、估值、新闻和 AI 分析 |
| **自选股** | 维护关注列表，查看最新行情和估值信息（用户数据隔离） |
| **价格预警** | 配置价格触发条件，定时检查并返回触发结果（用户数据隔离） |
| **IPO 分析** | 即将上市 IPO、近一年新股对比、板块统计、破发率、阶梯中签率和单只新股 AI 报告 |
| **日历** | 财报、分红和市场事件日历 |
| **AI 对话** | 与 AI 分析师实时对话，获取投资建议 |
| **AI 模型配置** | 支持 OpenAI / Claude / DeepSeek / Qwen / MiMo 等多模型配置 |

### 用户系统

| 功能 | 说明 |
|------|------|
| **用户注册** | 用户名 + 密码注册（MD5 + 盐值加密） |
| **用户登录** | JWT Token 认证，有效期 1 小时 |
| **数据隔离** | 自选股、价格预警、API 配置按用户隔离 |
| **路由守卫** | 前端未登录自动跳转登录页 |

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | Vue 3 + Vite + Element Plus + ECharts + Pinia |
| 后端 | Java 17 + Spring Boot 3.2 + MyBatis-Plus + Caffeine Cache |
| AI 微服务 | Python FastAPI + httpx + akshare |
| 数据库 | PostgreSQL 16 |
| 认证 | JWT (HMAC256) + Token 拦截器 |
| 数据源 | Futu OpenD、AKShare、AAStocks、HKEXnews、新闻爬虫 |
| 工程化 | Docker Compose、Knife4j、Nginx |

## 项目结构

```text
hk-stock-app/
├── backend/                         # Java Spring Boot 后端
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/hkstock/
│       │   ├── HkStockApplication.java
│       │   ├── common/              # ApiResponse 统一响应结构
│       │   ├── config/              # Spring / 缓存 / 跨域 / Knife4j 配置
│       │   ├── controller/          # REST API 接口（9个Controller）
│       │   ├── domain/              # 数据表实体（8个实体类）
│       │   ├── dto/                 # 数据传输对象
│       │   ├── vo/                  # 视图对象
│       │   ├── query/               # 查询参数对象
│       │   ├── exception/           # 业务异常和全局异常处理
│       │   ├── interceptor/         # JWT Token 拦截器
│       │   ├── mapper/              # MyBatis-Plus 数据访问层
│       │   ├── service/             # 业务逻辑接口
│       │   ├── service/impl/        # 业务逻辑实现
│       │   ├── task/                # 定时同步与预警任务
│       │   └── utils/               # JWT 工具类
│       └── resources/
│           ├── application.yml
│           └── schema.sql
├── frontend/                        # Vue 前端
│   ├── package.json
│   ├── vite.config.js
│   ├── nginx.conf                   # Nginx 配置（超时 300 秒）
│   └── src/
│       ├── App.vue                  # 根组件（导航栏 + 退出登录）
│       ├── main.js                  # 入口文件
│       ├── assets/style/reset.css   # CSS 重置
│       ├── http/request.js          # Axios 封装（自动 token 注入）
│       ├── router/index.js          # 路由配置 + 登录守卫
│       ├── stores/                  # Pinia 状态管理
│       │   ├── index.js
│       │   ├── stock.js
│       │   └── user.js
│       └── views/                   # 页面组件（10个）
│           ├── Dashboard.vue        # 大盘概览
│           ├── Search.vue           # 股票搜索
│           ├── StockDetail.vue      # 股票详情（K线/估值/新闻/AI）
│           ├── Watchlist.vue        # 自选股
│           ├── IPO.vue              # 新股分析
│           ├── Calendar.vue         # 日历
│           ├── Alerts.vue           # 价格预警
│           ├── Settings.vue         # 设置
│           ├── LoginView.vue        # 登录页
│           └── RegisterView.vue     # 注册页
├── ai-service/                      # Python FastAPI AI 微服务
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       └── routers/
│           ├── analyze.py           # AI 分析（新闻/新股/对话）
│           ├── config.py            # 配置管理
│           ├── scraper.py           # 数据爬取
│           └── sync.py              # Futu 数据同步
├── scripts/                         # 数据同步脚本
│   ├── sync/                        # 数据同步脚本
│   │   ├── sync_market_overview.py  # 大盘概览同步
│   │   ├── sync_daily_kline.py      # K线数据同步
│   │   ├── sync_ipo_futu.py         # IPO数据同步
│   │   ├── sync_ipo_detail_aastocks.py  # IPO详情+阶梯中签率
│   │   ├── sync_calendar_aastocks.py    # 日历数据同步
│   │   ├── sync_valuation_futu.py   # 估值数据同步
│   │   └── sync_akshare.py          # AKShare K线同步
│   ├── scrapers/                    # 网页爬取脚本
│   └── utils/                       # 工具脚本
├── tests/                           # 测试脚本
├── archive/                         # 归档脚本
├── docker/                          # Docker 初始化脚本
│   └── postgres/
│       └── 01_schema.sql            # 数据库初始化
├── docker-compose.yml               # 一键启动配置
├── .env                             # 环境变量
├── .env.example                     # 环境变量示例
├── .gitignore
└── README.md
```

## 数据库设计

### 核心表结构（9张表）

| 表名 | 说明 | 数据量 |
|------|------|--------|
| `stock_info` | 股票基本信息 | 3,781 只 |
| `stock_kline` | K线数据（日K/周K/月K） | 2,844 只 |
| `stock_valuation` | 估值指标（PE/PB/股息率/市值） | 2,829 只 |
| `stock_ipo` | 新股IPO信息（含阶梯中签率） | 102 条 |
| `stock_calendar` | 财报/分红日历 | 47 条 |
| `news` | 新闻数据 | - |
| `watchlist` | 自选股（用户隔离） | - |
| `price_alert` | 价格预警（用户隔离） | - |
| `users` | 用户账号 | - |

### 数据隔离规则

- **用户级别**：`watchlist`、`price_alert`、`api_config`（有 `user_id` 字段）
- **全局数据**：`stock_info`、`stock_kline`、`stock_ipo`、`stock_calendar`、`market_overview`、`stock_valuation`

## API 接口

### 后端接口（20+ REST API）

| 路径 | 说明 |
|------|------|
| `POST /api/user/register` | 用户注册 |
| `POST /api/user/login` | 用户登录 |
| `GET /api/stock/search` | 股票搜索 |
| `GET /api/stock/{code}` | 股票详情 |
| `GET /api/stock/{code}/kline` | K线数据 |
| `GET /api/stock/{code}/valuation` | 估值数据 |
| `GET /api/stock/{code}/news` | 新闻数据 |
| `GET /api/watchlist/list` | 自选股列表 |
| `POST /api/watchlist/add` | 添加自选股 |
| `DELETE /api/watchlist/remove/{code}` | 删除自选股 |
| `GET /api/alert/list` | 预警列表 |
| `POST /api/alert/add` | 添加预警 |
| `DELETE /api/alert/remove/{id}` | 删除预警 |
| `GET /api/ipo/upcoming` | 即将上市IPO |
| `GET /api/ipo/comparison` | IPO对比统计 |
| `GET /api/calendar/list` | 日历事件 |
| `GET /api/config/current` | AI模型配置 |
| `POST /api/config/model` | 设置AI模型 |

### AI 服务接口

| 路径 | 说明 |
|------|------|
| `POST /api/analyze/stock-news` | 新闻AI分析 |
| `POST /api/analyze/ipo` | IPO AI分析 |
| `POST /api/analyze/chat` | AI对话 |
| `GET /api/config` | 获取AI配置 |
| `POST /api/config` | 更新AI配置 |

## Docker Compose 一键启动

项目根目录已提供 `docker-compose.yml`，clone 后可以一次启动 PostgreSQL、Spring Boot 后端、FastAPI AI 服务和 Vue 前端。

```bash
docker compose up -d
```

首次启动如果本地没有镜像，Docker Compose 会按各模块 Dockerfile 自动构建。需要强制重建时执行：

```bash
docker compose up -d --build
```

### 端口说明

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:3000 | Vue 3 前端 |
| 后端 | http://localhost:8080 | Spring Boot API |
| AI 服务 | http://localhost:8082 | FastAPI AI 微服务 |
| PostgreSQL | localhost:5433 | 数据库（Docker） |
| Knife4j | http://localhost:8080/doc.html | API 文档 |
| 健康检查 | http://localhost:8080/api/health | 后端健康状态 |

### 环境变量配置

不创建 `.env` 也能用默认值启动；如需修改数据库密码、Futu OpenD 地址或端口，可复制示例文件：

```bash
copy .env.example .env
```

常用配置：

```env
POSTGRES_DB=hk_stock
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_database_password
FUTU_OPEND_HOST=host.docker.internal
FUTU_OPEND_PORT=11111
```

## 接口文档

后端集成 Knife4j（增强版 Swagger），启动后访问：

```text
http://localhost:8080/doc.html
```

常用命令：

```bash
# 查看容器状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down

# 停止并删除数据库数据卷（会清空数据）
docker compose down -v
```

> 首次启动会自动执行 `docker/postgres/01_schema.sql` 初始化表结构。已有数据卷不会重复初始化；如果改了初始化 SQL 并想重建空库，需要先执行 `docker compose down -v`。

## 本地启动

### 1. 准备 PostgreSQL

```bash
createdb -U postgres hk_stock
psql -U postgres -d hk_stock -f backend/src/main/resources/schema.sql
```

### 2. 配置环境变量

```bash
copy .env.example .env
```

然后按本机环境填写：

```env
DB_URL=jdbc:postgresql://localhost:5432/hk_stock
DB_USER=postgres
DB_PASSWORD=your_database_password
AI_SERVICE_URL=http://localhost:8082
PYTHON_EXECUTABLE=python
APP_SCRIPT_ROOT=..
```

> Spring Boot 不会自动读取根目录 `.env`。可以在 IDEA 运行配置或系统环境变量里配置这些值。

### 3. 启动后端

```bash
cd backend
mvn spring-boot:run
```

### 4. 启动 AI 微服务

```bash
cd ai-service
pip install -r requirements.txt
uvicorn app.main:app --port 8082 --reload
```

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

## 常用验证命令

```bash
# Docker Compose 配置检查
docker compose config

# 后端编译
cd backend
mvn -DskipTests compile

# 前端构建
cd frontend
npm install
npm run build

# AI 微服务健康检查
curl http://localhost:8082/health
```

## 重要代码入口

### 后端

| 模块 | 文件路径 |
|------|----------|
| 启动类 | `backend/src/main/java/com/hkstock/HkStockApplication.java` |
| 统一响应 | `backend/src/main/java/com/hkstock/common/ApiResponse.java` |
| 全局异常 | `backend/src/main/java/com/hkstock/exception/GlobalExceptionHandler.java` |
| JWT 工具 | `backend/src/main/java/com/hkstock/utils/JWTUtil.java` |
| Token 拦截器 | `backend/src/main/java/com/hkstock/interceptor/TokenInterceptor.java` |
| 缓存配置 | `backend/src/main/java/com/hkstock/config/CacheConfig.java` |

### 前端

| 模块 | 文件路径 |
|------|----------|
| 入口文件 | `frontend/src/main.js` |
| 根组件 | `frontend/src/App.vue` |
| 路由配置 | `frontend/src/router/index.js` |
| HTTP 封装 | `frontend/src/http/request.js` |
| 用户状态 | `frontend/src/stores/user.js` |

### 定时任务

| 任务 | 说明 |
|------|------|
| `MarketOverviewSyncTask` | 大盘概览和股票列表同步 |
| `KlineSyncTask` | K 线数据同步 |
| `IpoSyncTask` | IPO 基础数据同步 |
| `IpoMetricsSyncTask` | IPO 对比 / 板块 / 破发率指标同步 |
| `CalendarSyncTask` | 财报 / 分红日历同步 |
| `PriceAlertTask` | 价格预警检查 |

### AI 分析

| 模块 | 文件路径 |
|------|----------|
| AI 分析路由 | `ai-service/app/routers/analyze.py` |
| 配置管理 | `ai-service/app/routers/config.py` |
| 数据同步 | `ai-service/app/routers/sync.py` |

## 数据同步

### 数据源

| 数据源 | 数据类型 | 同步方式 |
|--------|----------|----------|
| Futu OpenD | 股票列表、K线、估值、IPO | Python futu-api |
| AKShare | K线、市场行情 | Python akshare |
| AAStocks | IPO详情、阶梯中签率 | 网页爬取 |
| HKEXnews | IPO公告PDF | PDF解析 |
| 新闻RSS | 新闻数据 | RSS解析 |

### 同步脚本

```bash
# 同步股票列表
python scripts/sync/sync_market_overview.py

# 同步K线数据
python scripts/sync/sync_daily_kline.py

# 同步IPO数据
python scripts/sync/sync_ipo_futu.py

# 同步估值数据
python scripts/sync/sync_valuation_futu.py

# 同步日历数据
python scripts/sync/sync_calendar_aastocks.py
```

## 项目亮点

1. **微服务架构**：前后端分离 + AI 服务独立，职责清晰
2. **多源数据融合**：8 个外部数据源统一整合
3. **AI 智能分析**：LLM 驱动的投资分析（新闻/新股/对话）
4. **用户系统**：JWT 认证 + 数据隔离
5. **Docker 一键部署**：4 个容器一键启动
6. **缓存优化**：11 个 Caffeine 缓存域，10 分钟 TTL
7. **定时任务**：6 个 @Scheduled 任务自动同步数据

## 技术难点

1. **HKEX 公告 PDF 解析**：从 PDF 中提取阶梯中签率数据
2. **LLM 嵌套 JSON 解析**：处理大模型返回的嵌套 JSON 结构
3. **Nginx 代理超时**：AI 分析需要 300 秒超时配置
4. **Futu API 连接稳定性**：容器内长连接断开处理
5. **数据一致性**：多源数据同步的一致性保障

## 许可证

本项目仅供学习交流使用。
