-- 港股分析应用 数据库初始化脚本
-- 数据库: PostgreSQL

CREATE DATABASE hk_stock;

-- 股票基本信息
CREATE TABLE stock_info (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL UNIQUE,
    stock_name VARCHAR(100) NOT NULL,
    sector VARCHAR(100),
    is_hk_stock_connect BOOLEAN DEFAULT FALSE,
    market_cap DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_stock_info_code ON stock_info(stock_code);
CREATE INDEX idx_stock_info_name ON stock_info(stock_name);
CREATE INDEX idx_stock_info_sector ON stock_info(sector);

-- K线数据
CREATE TABLE stock_kline (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    period_type VARCHAR(5) NOT NULL,  -- D=日K, W=周K, M=月K, Y=年K
    trade_date DATE NOT NULL,
    open_price DECIMAL(12, 4),
    close_price DECIMAL(12, 4),
    high_price DECIMAL(12, 4),
    low_price DECIMAL(12, 4),
    volume BIGINT,
    turnover DECIMAL(20, 2),
    change_percent DECIMAL(8, 4),
    turnover_rate DECIMAL(8, 4),
    UNIQUE(stock_code, period_type, trade_date)
);
CREATE INDEX idx_kline_code_date ON stock_kline(stock_code, trade_date);
CREATE INDEX idx_kline_period ON stock_kline(period_type);

-- 新股IPO信息
CREATE TABLE stock_ipo (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100) NOT NULL,
    sector VARCHAR(100),
    subscription_start DATE,
    subscription_end DATE,
    pricing_date DATE,
    allotment_date DATE,
    listing_date DATE,
    issue_price DECIMAL(12, 4),
    entry_fee DECIMAL(20, 2),
    fundraising_amount DECIMAL(20, 2),
    allotment_rate DECIMAL(8, 4),
    oversubscription_ratio DECIMAL(12, 2),
    public_offering_ratio DECIMAL(8, 4),
    international_placement_ratio DECIMAL(8, 4),
    sponsor VARCHAR(200),
    cornerstone_investor VARCHAR(500),
    cornerstone_amount DECIMAL(20, 2),
    issue_pe DECIMAL(12, 2),
    industry_avg_pe DECIMAL(12, 2),
    is_hk_stock_connect BOOLEAN DEFAULT FALSE,
    first_day_change DECIMAL(8, 4),
    seven_day_change DECIMAL(8, 4),
    thirty_day_change DECIMAL(8, 4),
    current_change DECIMAL(8, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ipo_code ON stock_ipo(stock_code);
CREATE INDEX idx_ipo_listing_date ON stock_ipo(listing_date);
CREATE INDEX idx_ipo_sector ON stock_ipo(sector);

-- 新闻信息
CREATE TABLE news (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    title VARCHAR(500) NOT NULL,
    source VARCHAR(100),
    url TEXT,
    publish_time TIMESTAMP,
    ai_sentiment VARCHAR(20),  -- 利好/利空/中性
    ai_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_news_code_time ON news(stock_code, publish_time);

-- 自选股
CREATE TABLE watchlist (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code)
);

-- 价格预警
CREATE TABLE price_alert (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    alert_type VARCHAR(10) NOT NULL,  -- ABOVE/BELOW
    target_price DECIMAL(12, 4) NOT NULL,
    triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_alert_code ON price_alert(stock_code);
CREATE INDEX idx_alert_triggered ON price_alert(triggered);

-- 估值指标
CREATE TABLE stock_valuation (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    pe DECIMAL(12, 2),
    pb DECIMAL(12, 2),
    dividend_yield DECIMAL(8, 4),
    market_cap DECIMAL(20, 2),
    data_date DATE NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_code, data_date)
);
CREATE INDEX idx_valuation_code ON stock_valuation(stock_code);

-- 财报/分红日历
CREATE TABLE stock_calendar (
    id BIGSERIAL PRIMARY KEY,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    event_type VARCHAR(20) NOT NULL,  -- FINANCIAL/DIVIDEND
    event_date DATE NOT NULL,
    dividend_per_share DECIMAL(12, 4),
    ex_dividend_date DATE,
    payment_date DATE,
    financial_report_type VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_calendar_code ON stock_calendar(stock_code);
CREATE INDEX idx_calendar_date ON stock_calendar(event_date);
CREATE INDEX idx_calendar_type ON stock_calendar(event_type);
CREATE UNIQUE INDEX uk_stock_calendar_event ON stock_calendar(stock_code, event_type, event_date);
