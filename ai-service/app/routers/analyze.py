"""
AI分析路由 - 修复版
"""
from fastapi import APIRouter, Query
from typing import Dict, Any
import httpx
import os
import json
import re
from bs4 import BeautifulSoup

router = APIRouter()

# LLM配置
llm_config = {
    "provider": os.getenv("AI_PROVIDER", "minimax"),
    "model": os.getenv("AI_MODEL", "MiniMax-M2.7"),
    "api_key": os.getenv("AI_API_KEY", ""),
    "base_url": os.getenv("AI_BASE_URL", "https://api.minimax.chat/v1/text/chatcompletion_v2")
}


def call_llm(prompt: str, api_key: str = None, base_url: str = None, model: str = None, max_tokens: int = 1200) -> str:
    """调用LLM进行分析"""
    
    # 优先使用传入的参数，否则用全局配置
    key = api_key if api_key else llm_config.get("api_key", "")
    url = base_url if base_url else llm_config.get("base_url", "")
    mdl = model if model else llm_config.get("model", "")
    
    if not key or key.strip() == "":
        return "请先在设置页面配置LLM API Key"
    
    # 自动补全API端点
    if "minimax" in url.lower():
        # MiniMax M2.7+ 用 OpenAI 兼容端点 /chat/completions
        if "M2.7" in mdl or "M2.5" not in mdl:
            if "chat/completions" not in url and "chatcompletion_v2" not in url:
                url = url.rstrip("/") + "/chat/completions"
        else:
            # MiniMax M2.5 及更早版本用 /text/chatcompletion_v2
            if "chatcompletion_v2" not in url:
                url = url.rstrip("/") + "/text/chatcompletion_v2"
    elif "openai" in url.lower() or "deepseek" in url.lower() or "dashscope" in url.lower() or "bigmodel" in url.lower():
        if "chat/completions" not in url:
            url = url.rstrip("/") + "/chat/completions"
    elif not url.endswith("/chat/completions") and not url.endswith("/chatcompletion_v2"):
        if "chatcompletion" not in url and "chat/completions" not in url:
            url = url.rstrip("/") + "/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": mdl,
        "messages": [
            {"role": "system", "content": "你是一位专业的港股分析师，擅长分析股票新闻和新股走势。请用中文回答。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    
    try:
        timeout = httpx.Timeout(180.0, connect=20.0, read=180.0, write=30.0, pool=20.0)
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                return f"LLM调用失败: HTTP {response.status_code} {response.text[:300]}"
            result = response.json()
            
            # MiniMax格式: choices[0].message.content
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
            
            # 其他格式: reply
            if "reply" in result:
                return result["reply"]
            
            # OpenAI格式
            if "content" in result:
                return result["content"]
            
            return f"无法解析API响应"
    except httpx.ReadTimeout:
        return "LLM调用失败: 模型响应超时，请稍后重试或切换更快的模型"
    except Exception as e:
        return f"LLM调用失败: {str(e)}"



def parse_structured_json(raw: str) -> Dict[str, Any]:
    """尽量从大模型输出中解析结构化 JSON，失败时保留原文并给前端兜底展示。"""
    fallback = {
        "summary": raw or "暂无分析结果",
        "riskLevel": "未知",
        "advantages": [],
        "risks": [],
        "suggestion": "暂无建议",
        "confidence": 0.0,
        "businessAnalysis": "暂无业务分析",
        "newsAnalysis": [],
        "ipoHeatAnalysis": "暂无招股热度分析",
        "valuationAnalysis": "暂无估值分析",
        "industryOutlook": "暂无行业前景分析",
        "listingForecast": "暂无上市走势预测",
        "subscriptionAdvice": "暂无申购建议理由",
        "suitableInvestors": "暂无适合人群分析",
    }

    if not raw:
        return fallback

    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    match = re.search(r"\{[\s\S]*\}", text)
    json_text = match.group(0) if match else text

    try:
        data = json.loads(json_text)
    except Exception:
        return fallback

    if not isinstance(data, dict):
        return fallback

    # 如果 summary 字段本身也是 JSON，尝试解析它
    summary = data.get("summary", "")
    if isinstance(summary, str) and summary.strip().startswith("{"):
        try:
            nested = json.loads(summary)
            if isinstance(nested, dict):
                # 嵌套JSON是完整对象，直接用它替换整个data
                has_real_fields = any(k in nested for k in ["summary", "riskLevel", "advantages", "risks", "suggestion"])
                if has_real_fields:
                    data = nested
        except Exception:
            pass

    def as_list(value):
        if isinstance(value, list):
            return [str(item) for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return []

    try:
        confidence = float(data.get("confidence", fallback["confidence"]))
    except Exception:
        confidence = fallback["confidence"]
    if confidence > 1:
        confidence = confidence / 100
    confidence = max(0.0, min(confidence, 1.0))

    def as_news_analysis(value):
        if not isinstance(value, list):
            return []
        items = []
        for item in value:
            if isinstance(item, dict):
                items.append({
                    "title": str(item.get("title") or "相关新闻"),
                    "viewpoint": str(item.get("viewpoint") or item.get("analysis") or "暂无解读"),
                    "impact": str(item.get("impact") or "中性"),
                })
            elif isinstance(item, str) and item.strip():
                items.append({"title": "相关新闻", "viewpoint": item.strip(), "impact": "中性"})
        return items

    return {
        "summary": str(data.get("summary") or fallback["summary"]),
        "riskLevel": str(data.get("riskLevel") or fallback["riskLevel"]),
        "advantages": as_list(data.get("advantages")),
        "risks": as_list(data.get("risks")),
        "suggestion": str(data.get("suggestion") or fallback["suggestion"]),
        "confidence": round(confidence, 2),
        "businessAnalysis": str(data.get("businessAnalysis") or fallback["businessAnalysis"]),
        "newsAnalysis": as_news_analysis(data.get("newsAnalysis")),
        "ipoHeatAnalysis": str(data.get("ipoHeatAnalysis") or fallback["ipoHeatAnalysis"]),
        "valuationAnalysis": str(data.get("valuationAnalysis") or fallback["valuationAnalysis"]),
        "industryOutlook": str(data.get("industryOutlook") or fallback["industryOutlook"]),
        "listingForecast": str(data.get("listingForecast") or fallback["listingForecast"]),
        "subscriptionAdvice": str(data.get("subscriptionAdvice") or fallback["subscriptionAdvice"]),
        "suitableInvestors": str(data.get("suitableInvestors") or fallback["suitableInvestors"]),
    }

def infer_provider(base_url: str) -> str:
    lower = (base_url or "").lower()
    if "xiaomi" in lower or "mimo" in lower:
        return "xiaomi"
    if "minimax" in lower:
        return "minimax"
    if "deepseek" in lower:
        return "deepseek"
    if "openrouter" in lower:
        return "openrouter"
    if "openai" in lower:
        return "openai"
    if "dashscope" in lower:
        return "dashscope"
    if "bigmodel" in lower:
        return "zhipu"
    return llm_config.get("provider", "unknown")


def fetch_stock_news(stock_name: str, stock_code: str = "", days: int = 7) -> list:
    """获取股票相关新闻，使用股票代码+公司名称双重确保相关性
    
    核心原则：新闻必须与指定股票代码真正相关，而非仅提及公司名的泛化新闻
    """
    news_list = []
    
    # 构建精确搜索关键词：优先用"股票代码 + 股票简称"组合
    # 股票代码是唯一标识，比公司名更可靠
    search_keyword = stock_name if stock_name else stock_code
    # 去掉 HK. 前缀
    search_code = stock_code
    if search_code:
        search_code = search_code.replace("HK.", "").replace("hk.", "").replace("HK", "").replace("hk", "").strip()
    
    try:
        # 方案1: Google News RSS - 支持按关键词精准搜索，可信度高
        news_list = _fetch_from_google_news(search_keyword, search_code, days)
        
        # 方案2: 新浪财经个股新闻（股票代码级）
        if not news_list:
            news_list = _fetch_from_sina_by_code(search_code, stock_name, days)
        
        # 方案3: 东方财富搜索（使用股票代码+名称组合）
        if not news_list:
            news_list = _fetch_from_eastmoney(search_keyword, search_code, days)
        
        # 方案4: 腾讯财经个股新闻（通过股票代码）
        if not news_list:
            news_list = _fetch_from_tencent_by_code(search_code, stock_name, days)
        
        # 兜底：确保至少返回与该股票相关的信息
        if not news_list:
            news_list = [
                {
                    "title": f"{search_keyword}（{stock_code}）近期市场动态",
                    "content": f"{search_keyword}（港股代码：{stock_code}）近日受到市场关注，投资者需关注公司基本面变化及行业趋势。",
                    "date": "",
                    "source": "市场资讯",
                    "link": ""
                }
            ]
    except Exception as e:
        print(f"获取新闻失败: {e}")
    
    return news_list


def _clean_google_url(self_url, final_url):
    """清洗Google News中的重定向URL，获取真实链接"""
    try:
        if 'newsurl' in self_url:
            return self_url
        if 'url=' in self_url:
            import urllib.parse
            parsed = urllib.parse.urlparse(self_url)
            queries = urllib.parse.parse_qs(parsed.query)
            if 'url' in queries:
                return queries['url'][0]
        return final_url if final_url else self_url
    except:
        return self_url


def _fetch_from_google_news(keyword: str, stock_code: str, days: int) -> list:
    """Google News RSS 搜索 - 关键词精准匹配"""
    news_list = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 搜索词：优先用"股票代码 股票名称"组合，其次用"股票名称 港股"
        queries = []
        if stock_code:
            # 港股代码格式通常是5位数字，直接搜索代码 + 名称组合更精确
            queries.append(f'"{stock_code}" {keyword} 港股')
        queries.append(f'{keyword} 港股 股票')
        
        for query in queries:
            try:
                import urllib.parse
                encoded_query = urllib.parse.quote_plus(query)
                url = f"https://news.google.com/rss/search?hl=zh-CN&gl=CN&ceid=CN:zh-Hans&q={encoded_query}"
                
                with httpx.Client(timeout=15, follow_redirects=True) as client:
                    resp = client.get(url, headers=headers)
                    if resp.status_code != 200:
                        continue
                    
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, "lxml-xml")
                    items = soup.find_all("item", limit=8)
                    
                    for item in items:
                        title_el = item.find("title")
                        link_el = item.find("link")
                        pub_date_el = item.find("pubDate")
                        source_el = item.find("source")
                        
                        title = title_el.text.strip() if title_el else ""
                        link = link_el.text.strip() if link_el else ""
                        pub_date = pub_date_el.text.strip() if pub_date_el else ""
                        source = source_el.text.strip() if source_el else "Google News"
                        
                        if not title:
                            continue
                        
                        # 验证这条新闻是否确实与该股票相关
                        # 通过标题/链接中是否包含股票代码或明确公司名来验证
                        title_lower = title.lower()
                        link_lower = link.lower()
                        keyword_lower = keyword.lower()
                        code_match = stock_code and (stock_code in title or stock_code in link)
                        name_match = any(part in title or part in link for part in keyword.split() if len(part) >= 2)
                        
                        # 如果标题/链接中完全没有股票代码也没有关键词片段，跳过
                        if not code_match and not name_match:
                            # 但对于股票名称比较确定的情况，放宽条件
                            if len(keyword) >= 4 and keyword[:2] in title:
                                pass  # 通过
                            else:
                                continue
                        
                        # 清洗链接中的重定向
                        if 'newsurl' in link:
                            actual_link = link
                        elif 'url=' in link:
                            import urllib.parse
                            try:
                                parsed = urllib.parse.urlparse(link)
                                qs = urllib.parse.parse_qs(parsed.query)
                                actual_link = qs.get('url', [link])[0]
                            except:
                                actual_link = link
                        else:
                            actual_link = link
                        
                        # 格式化日期
                        date_str = ""
                        if pub_date:
                            try:
                                from datetime import datetime
                                dt = datetime.strptime(pub_date[:25], "%a, %d %b %Y %H:%M:%S")
                                date_str = dt.strftime("%Y-%m-%d")
                            except:
                                date_str = pub_date[:10] if len(pub_date) >= 10 else pub_date
                        
                        news_list.append({
                            "title": title,
                            "content": title,
                            "date": date_str,
                            "source": source,
                            "link": actual_link
                        })
                    
                    if news_list:
                        break  # 如果有结果就不再尝试其他查询
            except Exception as e:
                print(f"Google News query '{query}' failed: {e}")
                continue
    except Exception as e:
        print(f"Google News RSS 获取失败: {e}")
    
    return news_list


def _fetch_from_sina_by_code(stock_code: str, stock_name: str, days: int) -> list:
    """新浪财经 - 通过股票代码获取个股新闻（最可靠）"""
    news_list = []
    if not stock_code:
        return news_list
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://finance.sina.com.cn/"
        }
        
        # 港股代码需要加前缀 "HK" 或转换
        # 新浪财经港股新闻的 pageid/lid 组合
        hk_code = stock_code.zfill(5)  # 5位数字格式
        
        # 方案A: 直接用股票代码作为搜索关键词
        url = f"https://feed.mix.sina.com.cn/api/roll/get"
        params = {
            "pageid": "153",
            "lid": "2516",
            "k": f"{hk_code} {stock_name}".strip(),
            "num": 10,
            "page": 1,
            "r": 0.5
        }
        
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            resp = client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data and "data" in data["result"]:
                    for item in data["result"]["data"][:5]:
                        title = item.get("title", "")
                        link = item.get("url", "")
                        
                        # 再次验证新闻相关性：标题中需要包含公司名或股票代码
                        if stock_name and len(stock_name) >= 2:
                            if stock_name[:2] not in title and stock_code not in title:
                                # 检查是否有其他有效关键词
                                kw_pass = False
                                for kw in stock_name.split():
                                    if len(kw) >= 2 and kw in title:
                                        kw_pass = True
                                        break
                                if not kw_pass:
                                    continue
                        
                        news_list.append({
                            "title": title,
                            "content": item.get("intro", title),
                            "date": item.get("ctime", "")[:10] if item.get("ctime") else "",
                            "source": item.get("media_name", "新浪财经"),
                            "link": link
                        })
    except Exception as e:
        print(f"新浪财经个股新闻获取失败: {e}")
    
    return news_list


def _fetch_from_eastmoney(keyword: str, stock_code: str, days: int) -> list:
    """东方财富新闻搜索 - 修复版，正确传递搜索参数"""
    news_list = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://so.eastmoney.com/"
        }
        
        # 东方财富搜索API - 使用正确的搜索接口
        search_keyword = f"{stock_code} {keyword}".strip() if stock_code else keyword
        url = "https://search-api-web.eastmoney.com/api/search/get"
        params = {
            "keyword": search_keyword,
            "type": "cmsArticle",
            "pageIndex": 1,
            "pageSize": 10,
            "client": "web",
            "clientType": "web",
            "clientVersion": "curr"
        }
        
        with httpx.Client(timeout=10) as client:
            resp = client.get(url, params=params, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data and "result" in data["result"] and "list" in data["result"]["result"]:
                    import time
                    now = int(time.time())
                    cutoff = now - days * 86400
                    
                    for item in data["result"]["result"]["list"][:5]:
                        art_time = item.get("art_time", item.get("datetime", 0))
                        if isinstance(art_time, str) and art_time.isdigit():
                            art_time = int(art_time)
                        elif isinstance(art_time, str):
                            try:
                                from datetime import datetime
                                dt = datetime.strptime(art_time[:19], "%Y-%m-%d %H:%M:%S")
                                art_time = int(dt.timestamp())
                            except:
                                art_time = now
                        
                        if art_time and art_time < cutoff:
                            continue
                        
                        title = item.get("title", "")
                        # 验证相关性
                        if keyword and len(keyword) >= 2:
                            if keyword[:2] not in title and stock_code not in title:
                                kw_pass = any(part in title for part in keyword.split() if len(part) >= 2)
                                if not kw_pass:
                                    continue
                        
                        news_list.append({
                            "title": title,
                            "content": item.get("content", title),
                            "date": item.get("art_time", "")[:10] if item.get("art_time") else "",
                            "source": item.get("mediaName", "东方财富"),
                            "link": item.get("url", "") or item.get("articleUrl", "")
                        })
    except Exception as e:
        print(f"东方财富新闻获取失败: {e}")
    
    return news_list


def _fetch_from_tencent_by_code(stock_code: str, stock_name: str, days: int) -> list:
    """腾讯财经个股新闻 - 修复版，使用正确的API"""
    news_list = []
    if not stock_code:
        return news_list
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://finance.qq.com/"
        }
        
        # 腾讯财经有一个股票新闻API，通过股票代码查询
        # 尝试多种腾讯股票新闻接口
        import urllib.parse
        
        # 方法1: 腾讯股票新闻搜索
        search_url = f"https://finance.qq.com/node3/search?query={urllib.parse.quote(stock_name or stock_code)}&type=news&sort=1&page=1&pagesize=5"
        
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            try:
                resp = client.get(search_url, headers=headers)
                if resp.status_code == 200:
                    import json
                    try:
                        data = resp.json()
                        articles = data.get("result", {}).get("articals", data.get("data", {}).get("articles", []))
                        for item in articles[:5]:
                            news_list.append({
                                "title": item.get("title", ""),
                                "content": item.get("abstract", item.get("title", "")),
                                "date": item.get("publish_time", "")[:10] if item.get("publish_time") else "",
                                "source": item.get("source", "腾讯财经"),
                                "link": item.get("url", "")
                            })
                    except:
                        pass
            except:
                pass
            
            # 方法2: 直接访问腾讯股票新闻页面
            if not news_list and stock_code:
                try:
                    # 腾讯股票新闻频道
                    sina_code = f"hk{stock_code.zfill(5)}"
                    news_url = f"https://finance.qq.com/article/croll_{sina_code}.htm"
                    resp = client.get(news_url, headers=headers)
                    if resp.status_code != 200:
                        # 尝试搜索页面
                        search_url2 = f"https://so.qq.com/c/search?query={urllib.parse.quote(stock_name or stock_code)}+港股"
                        resp = client.get(search_url2, headers=headers, timeout=5)
                except:
                    pass
    except Exception as e:
        print(f"腾讯财经获取失败: {e}")
    
    return news_list


@router.get("/stock-news")
def analyze_stock_news(
    stock_code: str = Query(..., description="股票代码"),
    stock_name: str = Query("", description="股票名称/公司名称"),
    days: int = Query(7, description="分析天数"),
    api_key: str = Query(None, description="API Key"),
    base_url: str = Query(None, description="API URL"),
    model: str = Query(None, description="模型名称")
) -> Dict[str, Any]:
    """分析股票相关新闻的利空/利好
    
    使用公司名称（如"小米集团"）搜索新闻，而不是股票代码
    """
    
    # 1. 获取新闻 - 优先使用公司名称
    search_name = stock_name if stock_name else stock_code
    news_list = fetch_stock_news(stock_name=search_name, stock_code=stock_code, days=days)
    
    if not news_list:
        return {
            "stock_code": stock_code,
            "stock_name": stock_name,
            "days": days,
            "news_count": 0,
            "analysis": f"暂时无法获取 {search_name}（{stock_code}）的最新新闻数据。请稍后再试。",
            "llm_provider": llm_config["provider"],
            "model": llm_config["model"]
        }
    
    # 2. 构建分析提示词 - 使用公司名称
    news_text = "\n".join([f"{i+1}. 【{n['source']} | {n['date']}】{n['title']}" for i, n in enumerate(news_list[:5])])
    
    prompt = f"""
你是一位专业的港股分析师。请根据以下 {search_name}（{stock_code}）的最新新闻，进行详细分析。

【最新新闻】
{news_text}

请严格按照以下格式输出：

一、逐条新闻分析
对每条新闻分别进行：
1) 新闻要点提炼（一句话概括核心信息）
2) 利好/利空判断（利好 🟢 / 利空 🔴 / 中性 ⚪）
3) 影响程度（高/中/低）
4) 对股价的潜在影响分析

二、综合走势预测
1) 短期（1-5个交易日）走势判断
2) 中期（1-3个月）走势展望
3) 综合评级：强烈看涨 / 看涨 / 中性 / 看跌 / 强烈看跌
4) 建议操作策略

三、风险提示
列出需要关注的风险因素

注意：分析要具体、有依据，不要泛泛而谈。
"""

    # 3. 调用LLM分析（新闻分析需要更多token）
    analysis = call_llm(prompt, api_key, base_url, model, max_tokens=3000)

    return {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "days": days,
        "news_count": len(news_list),
        "news": news_list[:5],
        "analysis": analysis,
        "llm_provider": llm_config["provider"],
        "model": llm_config["model"]
    }


@router.get("/ipo")
def analyze_ipo(
    stock_code: str = Query(..., description="新股代码"),
    stock_name: str = Query("", description="股票名称"),
    api_key: str = Query(None),
    base_url: str = Query(None),
    model: str = Query(None)
) -> Dict[str, Any]:
    """分析新股上市后走势 - 联网搜索最新新闻"""
    
    search_name = stock_name if stock_name else stock_code
    
    # 1. 联网抓取最新新闻
    news_list = fetch_stock_news(stock_name=search_name, stock_code=stock_code, days=7)
    news_text = ""
    if news_list:
        news_text = "\n".join([f"{i+1}. 【{n['source']} | {n['date']}】{n['title']}" for i, n in enumerate(news_list[:5])])
    else:
        news_text = "暂无最新相关新闻"
    
    # 2. 构建结构化分析提示词（包含新闻上下文）
    prompt = f"""
你是一位专业港股新股分析师。请根据港股新股 {stock_code} {search_name} 的最新新闻，输出结构化申购/交易判断。

【最新新闻，共 {min(len(news_list), 5)} 条】
{news_text}

请只返回严格 JSON，不要 Markdown，不要解释，不要代码块。字段必须完整：
{{
  "summary": "整体评价，120字以内，要点明结论和核心依据",
  "riskLevel": "低/中低/中/中高/高",
  "advantages": ["核心优势1", "核心优势2", "核心优势3"],
  "risks": ["主要风险1", "主要风险2", "主要风险3"],
  "suggestion": "积极申购/谨慎申购/观望/回避/持有观察 等明确建议",
  "confidence": 0.72,
  "businessAnalysis": "公司主营业务、商业模式、客户/产品/技术壁垒，180-260字",
  "newsAnalysis": [
    {{"title": "新闻标题1", "viewpoint": "这条新闻说明了什么，对申购或上市表现有什么影响，80-140字", "impact": "利好/中性/利空"}},
    {{"title": "新闻标题2", "viewpoint": "逐条解读，不能只复述标题", "impact": "利好/中性/利空"}}
  ],
  "ipoHeatAnalysis": "结合招股倍数、超购、市场情绪和资金热度分析，160-240字；没有具体数据时说明数据缺口",
  "valuationAnalysis": "结合发行价、行业可比公司、成长性或盈利质量评价估值是否合理，160-240字；没有估值数据时说明无法精确判断",
  "industryOutlook": "行业空间、政策/周期/竞争格局分析，160-240字",
  "listingForecast": "上市首日和短期走势预测，分别说明乐观/中性/悲观情形，160-240字",
  "subscriptionAdvice": "给出申购/交易建议的详细理由，适合什么策略，180-260字",
  "suitableInvestors": "适合的人群和不适合的人群，100-180字"
}}

要求：
1. advantages 和 risks 各给 3-5 条，必须结合新闻和港股新股环境。
2. newsAnalysis 必须逐条对应上方新闻，至少 3 条；不要只复述标题，要解释影响。
3. 所有长文本都要具体、有依据，不能泛泛而谈。
4. confidence 是 0 到 1 的小数。
5. suggestion 必须简短明确，适合前端直接展示为 AI 综合评级。
"""

    raw_analysis = call_llm(prompt, api_key, base_url, model, max_tokens=3600)
    structured_analysis = parse_structured_json(raw_analysis)

    actual_base_url = base_url if base_url else llm_config.get("base_url", "")
    actual_model = model if model else llm_config.get("model", "")
    return {
        "stock_code": stock_code,
        "stock_name": search_name,
        "news_count": len(news_list),
        "news": news_list[:5],
        "analysis": structured_analysis,
        "raw_analysis": raw_analysis,
        "llm_provider": infer_provider(actual_base_url),
        "model": actual_model
    }


@router.post("/stock-chat")
def stock_chat(payload: Dict[str, Any]) -> Dict[str, Any]:
    """股票新闻AI对话 - 基于已分析的新闻上下文进行问答"""
    
    stock_code = payload.get("stock_code", "")
    stock_name = payload.get("stock_name", "")
    news_context = payload.get("news_context", [])
    chat_history = payload.get("chat_history", [])
    user_message = payload.get("message", "")
    api_key = payload.get("api_key", "")
    base_url = payload.get("base_url", "")
    model = payload.get("model", "")
    
    if not user_message:
        return {"reply": "请输入你的问题"}
    
    # 构建新闻上下文文本
    news_text = "\n".join([
        f"- [{n.get('source', '')} | {n.get('date', '')}] {n.get('title', '')}"
        for n in news_context[:5]
    ]) if news_context else "暂无新闻数据"
    
    # 构建对话历史
    messages = [
        {
            "role": "system",
            "content": f"""你是一位专业的港股分析师助手，正在为用户分析 {stock_name}（{stock_code}）的最新新闻。

【当前新闻上下文】
{news_text}

你的职责：
1. 基于上述新闻内容回答用户提问
2. 解释新闻事件对股价的潜在影响
3. 分析行业趋势和公司基本面
4. 提供专业的投资参考（非投资建议）

回答要求：
- 简洁明了，重点突出
- 有数据引用数据，有逻辑讲逻辑
- 不确定的内容要明确说明
- 不要编造不存在的新闻或数据
- 用中文回答"""
        }
    ]
    
    # 添加历史对话（最多保留最近10轮）
    for msg in chat_history[-20:]:
        if msg.get("role") in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    # 添加当前用户消息
    messages.append({"role": "user", "content": user_message})
    
    # 调用LLM
    reply = call_llm_from_messages(messages, api_key, base_url, model)
    
    return {"reply": reply}


def call_llm_from_messages(messages: list, api_key: str = None, base_url: str = None, model: str = None) -> str:
    """用消息列表调用LLM（支持多轮对话）"""
    key = api_key if api_key else llm_config.get("api_key", "")
    url = base_url if base_url else llm_config.get("base_url", "")
    mdl = model if model else llm_config.get("model", "")

    if not key or key.strip() == "":
        return "请先在设置页面配置LLM API Key"
    
    # 自动补全API端点
    if "minimax" in url.lower():
        if "M2.7" in mdl or "M2.5" not in mdl:
            if "chat/completions" not in url and "chatcompletion_v2" not in url:
                url = url.rstrip("/") + "/chat/completions"
        else:
            if "chatcompletion_v2" not in url:
                url = url.rstrip("/") + "/text/chatcompletion_v2"
    elif not url.endswith("/chat/completions") and not url.endswith("/chatcompletion_v2"):
        if "chatcompletion" not in url and "chat/completions" not in url:
            url = url.rstrip("/") + "/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": mdl,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1200
    }
    
    try:
        timeout = httpx.Timeout(180.0, connect=20.0, read=180.0, write=30.0, pool=20.0)
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=payload)
            if response.status_code >= 400:
                return f"LLM调用失败: HTTP {response.status_code} {response.text[:300]}"
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"]
            
            if "reply" in result:
                return result["reply"]
            
            return "无法解析AI响应，请检查API配置"
    except Exception as e:
        return f"AI调用失败: {str(e)}"


@router.post("/config")
def update_llm_config(config: Dict[str, Any]):
    """更新LLM配置"""
    global llm_config
    if "provider" in config:
        llm_config["provider"] = config["provider"]
    if "model" in config:
        llm_config["model"] = config["model"]
    if "api_key" in config:
        llm_config["api_key"] = config["api_key"]
    if "base_url" in config:
        llm_config["base_url"] = config["base_url"]
    
    return {"status": "success", "config": {k: v for k, v in llm_config.items() if k != "api_key"}}
