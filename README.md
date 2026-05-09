# 港股智能分析平台

**HK Stock Intelligence Platform** 是一个本地可运行的港股智能分析系统，覆盖行情检索、K 线与技术指标、自选股、价格预警、新股表现统计、新股 AI 分析、财报/分红日历、AI 模型配置和数据同步任务。

项目采用 Vue 3 + Spring Boot 3.2 + FastAPI + PostgreSQL，提供 Docker Compose 一键启动、Swagger 接口文档、定时同步任务和统一 API 响应结构，适合作为 Java 后端 / 全栈 / 金融科技方向作品集项目。

## 功能概览

- **大盘概览**：展示港股市场整体行情与指数概览。
- **股票搜索**：按代码或名称搜索港股。
- **股票详情**：展示 K 线、技术指标、估值、新闻和 AI 分析入口。
- **自选股**：维护关注列表，查看最新行情和估值信息。
- **新股分析**：即将上市 IPO、近一年新股对比、板块统计、破发率和单只新股 AI 报告。
- **日历**：财报、分红和市场事件日历。
- **价格预警**：配置价格触发条件，定时检查并返回触发结果。
- **AI 模型配置**：支持 OpenAI-compatible / MiniMax / Xiaomi MiMo / DeepSeek / Qwen 等模型配置。
- **数据同步**：Futu OpenD、AKShare、AAStocks/HKEX 公告与新闻爬虫多源同步。

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 前端 | Vue 3 + Vite + Element Plus + ECharts |
| 后端 | Java 17 + Spring Boot 3.2 + MyBatis-Plus + Caffeine Cache |
| AI 微服务 | Python FastAPI + httpx + akshare |
| 数据库 | PostgreSQL |
| 数据源 | Futu OpenD、AKShare、AAStocks、HKEXnews、新闻爬虫 |
| 工程化 | Docker Compose、Swagger/OpenAPI、GitHub Actions |

## 项目结构

```text
hk-stock-intelligence-platform/
├── backend/                         # Java Spring Boot 后端
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/hkstock/
│       │   ├── HkStockApplication.java
│       │   ├── common/              # 统一响应结构
│       │   ├── config/              # Spring / 缓存 / 跨域配置
│       │   ├── controller/          # REST API 接口
│       │   ├── entity/              # 数据表实体
│       │   ├── exception/           # 业务异常和全局异常处理
│       │   ├── mapper/              # MyBatis-Plus 数据访问层
│       │   ├── service/             # 业务逻辑
│       │   └── task/                # 定时同步与预警任务
│       └── resources/
│           ├── application.yml
│           └── schema.sql
├── frontend/                        # Vue 前端
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── ai-service/                      # Python FastAPI AI 微服务
│   ├── requirements.txt
│   └── app/
├── docker/                          # Docker 初始化脚本
├── docker-compose.yml               # PostgreSQL + 后端 + AI 服务 + 前端一键启动
├── requirements-sync.txt            # 同步脚本在 Docker 内需要的 Python 依赖
├── .env.example                     # 环境变量示例，不要填写真实密钥后提交
├── .github/workflows/ci.yml         # GitHub Actions 构建检查
└── README.md
```

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

```text
frontend:   http://localhost:3000
backend:    http://localhost:8080
ai-service: http://localhost:8082
postgres:   localhost:5432 / hk_stock
Swagger:    http://localhost:8080/swagger-ui.html
Health:     http://localhost:8080/api/health
```

### 可选：准备本地环境变量

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

后端集成 Swagger / OpenAPI UI，启动后访问：

```text
http://localhost:8080/swagger-ui.html
```

截图：

![Swagger UI](docs/images/swagger-ui.png)

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

- 新股页面：`frontend/src/views/IPO.vue`
- 新股接口：`backend/src/main/java/com/hkstock/controller/IpoController.java`
- 新股业务：`backend/src/main/java/com/hkstock/service/IpoService.java`
- 统一响应：`backend/src/main/java/com/hkstock/common/ApiResponse.java`
- 全局异常处理：`backend/src/main/java/com/hkstock/exception/GlobalExceptionHandler.java`
- 健康检查：`backend/src/main/java/com/hkstock/controller/HealthController.java`
- 缓存清理：`backend/src/main/java/com/hkstock/service/CacheInvalidationService.java`
- 定时任务：`backend/src/main/java/com/hkstock/task/`
  - `IpoSyncTask.java`：IPO 基础数据同步
  - `IpoMetricsSyncTask.java`：IPO 对比 / 板块 / 破发率指标同步
  - `MarketOverviewSyncTask.java`：大盘概览和股票列表同步
  - `CalendarSyncTask.java`：财报 / 分红日历同步
  - `KlineSyncTask.java`：K 线数据同步
  - `PriceAlertTask.java`：价格预警检查
  - `PythonScriptRunner.java`：统一执行 Python 脚本、读取 stdout/stderr、处理超时和失败
- AI 分析：`ai-service/app/routers/analyze.py`
