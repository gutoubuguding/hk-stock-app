package com.hkstock.task;

import com.hkstock.service.PriceAlertService;
import com.hkstock.service.StockService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.TimeUnit;

/**
 * 定时任务 - 港股数据自动同步
 * 
 * 港股交易时段: 9:30 - 16:00（北京时间）
 * akshare 免费数据延迟约 15 分钟
 * 
 * 同步策略:
 * - 每日 9:00 预热sync：同步所有股票前一交易日数据
 * - 每日 12:00 盘中sync：同步上午最新数据
 * - 每日 16:30 收盘sync：同步当日完整数据
 * 
 * 使用 akshare Python 脚本同步数据，不依赖 Futu OpenD
 */
@Component
public class ScheduledTasks {

    private static final Logger log = LoggerFactory.getLogger(ScheduledTasks.class);
    private static final DateTimeFormatter DF = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    // Python 脚本文件名。实际根目录从 application.yml 的 app.scripts.root 读取，
    // 这样以后项目从 .openclaw 移到桌面/服务器时，只改配置，不用重新编译 Java 代码。
    private static final String PYTHON_SCRIPT_KLINE = "sync_daily_kline.py";
    private static final String PYTHON_SCRIPT_IPO = "sync_ipo_futu.py";
    private static final String PYTHON_SCRIPT_MARKET_OVERVIEW = "sync_market_overview.py";
    private static final String PYTHON_SCRIPT_CALENDAR = "sync_calendar_aastocks.py";

    @Value("${app.python.executable:python}")
    private String pythonExe;

    @Value("${app.scripts.root:..}")
    private String scriptRoot;

    private @Autowired PriceAlertService priceAlertService;
    private @Autowired StockService stockService;

    /**
     * ===== 新股数据同步 =====
     * 每天 8:00 和 20:00 两个时间点自动同步IPO数据
     * 通过Python东方财富接口实现，不依赖Futu OpenD
     */
    
    /**
     * 早市同步（8:00）：新股日历更新
     */
    @Scheduled(cron = "0 0 8 * * ?")
    public void updateIpoData() {
        log.info("【IPO同步】早市同步开始 (时间: {})", LocalDateTime.now().format(DF));
        runPythonScript(resolveScript(PYTHON_SCRIPT_IPO), "IPO早市同步");
        log.info("【IPO同步】早市同步触发完成");
    }

    /**
     * 晚市同步（20:00）：收盘后再次更新新股数据
     */
    @Scheduled(cron = "0 0 20 * * ?")
    public void updateIpoDataEvening() {
        log.info("【IPO同步】晚市同步开始 (时间: {})", LocalDateTime.now().format(DF));
        runPythonScript(resolveScript(PYTHON_SCRIPT_IPO), "IPO晚市同步");
        log.info("【IPO同步】晚市同步触发完成");
    }

    /**
     * 每天9点更新股票列表（新股挂牌等）
     */
    @Scheduled(cron = "0 0 9 * * ?")
    public void updateStockList() {
        log.info("定时任务：开始更新股票列表");
        try {
            stockService.refreshStockList();
            log.info("定时任务：股票列表更新完成");
        } catch (Exception e) {
            log.error("定时任务：股票列表更新失败", e);
        }
    }

    /**
     * ===== 大盘概览同步 =====
     * 交易日盘中每30分钟更新一次，收盘后再补一次。
     */
    @Scheduled(cron = "0 */30 9-16 * * MON-FRI")
    public void syncMarketOverviewIntraday() {
        log.info("【大盘概览】盘中同步开始 (时间: {})", LocalDateTime.now().format(DF));
        runPythonScript(resolveScript(PYTHON_SCRIPT_MARKET_OVERVIEW), "大盘概览-盘中");
    }

    @Scheduled(cron = "0 10 17 * * MON-FRI")
    public void syncMarketOverviewClose() {
        log.info("【大盘概览】收盘后同步开始 (时间: {})", LocalDateTime.now().format(DF));
        runPythonScript(resolveScript(PYTHON_SCRIPT_MARKET_OVERVIEW), "大盘概览-收盘");
    }

    /**
     * ===== 财报/分红日历同步 =====
     * 每天开盘前和收盘后从 AASTOCKS 同步港股公司事件。
     */
    @Scheduled(cron = "0 30 7 * * ?")
    public void syncCalendarMorning() {
        log.info("【日历同步】早市同步开始 (时间: {})", LocalDateTime.now().format(DF));
        runPythonScript(resolveScript(PYTHON_SCRIPT_CALENDAR), "日历同步-早市");
    }

    @Scheduled(cron = "0 30 18 * * ?")
    public void syncCalendarEvening() {
        log.info("【日历同步】晚市同步开始 (时间: {})", LocalDateTime.now().format(DF));
        runPythonScript(resolveScript(PYTHON_SCRIPT_CALENDAR), "日历同步-晚市");
    }

    /**
     * ===== 价格预警检查 =====
     * 交易日盘中每5分钟检查一次，命中后标记为已触发。
     */
    @Scheduled(cron = "0 */5 9-16 * * MON-FRI")
    public void checkPriceAlertsIntraday() {
        try {
            int count = priceAlertService.checkAlerts().size();
            if (count > 0) {
                log.info("【价格预警】本次触发 {} 条", count);
            }
        } catch (Exception e) {
            log.error("【价格预警】检查失败", e);
        }
    }

    /**
     * ===== K线数据批量同步 =====
     * 每天9:00 / 12:00 / 16:30 三个时间点自动同步所有股票的日K数据
     * 通过调用Python akshare脚本实现，不依赖Futu OpenD
     */
    
    /**
     * 早市预热（9:00）：同步所有股票前日收盘数据
     * 港股前一天16:00收盘后数据此时已更新到akshare
     */
    @Scheduled(cron = "0 0 9 * * ?")
    public void syncAllKlineMorning() {
        log.info("【K线同步】早市预热开始 (时间: {})", LocalDateTime.now().format(DF));
        runPythonScript(resolveScript(PYTHON_SCRIPT_KLINE), "K线同步-早市预热");
    }

    /**
     * 午间同步（12:00）：同步上午盘中数据
     */
    @Scheduled(cron = "0 0 12 * * ?")
    public void syncAllKlineNoon() {
        log.info("【K线同步】午间同步开始 (时间: {})", LocalDateTime.now().format(DF));
        runPythonScript(resolveScript(PYTHON_SCRIPT_KLINE), "K线同步-午间");
    }

    /**
     * 收盘同步（16:30）：港股16:00收盘后同步当日最终数据
     * 这是最重要的同步节点
     */
    @Scheduled(cron = "0 30 16 * * ?")
    public void syncAllKlineClose() {
        log.info("【K线同步】收盘同步开始 (时间: {})", LocalDateTime.now().format(DF));
        runPythonScript(resolveScript(PYTHON_SCRIPT_KLINE), "K线同步-收盘");
    }

    /**
     * 把脚本文件名拼成完整路径。
     * 这里集中处理路径，是为了避免每个定时任务都写死绝对路径。
     */
    private String resolveScript(String scriptName) {
        return Path.of(scriptRoot, scriptName).toString();
    }

    /**
     * 执行 Python 脚本（通用方法）。
     *
     * <p>为什么要异步读取 stdout/stderr：外部进程如果持续输出但没人消费，缓冲区满了可能导致脚本卡住。
     * 所以这里单独启动两个 reader 线程，把脚本日志接到 Java 日志里，方便以后排查同步失败。
     *
     * @param scriptPath 脚本完整路径
     * @param syncName  同步名称（用于日志）
     */
    private void runPythonScript(String scriptPath, String syncName) {
        log.info("【{}】开始执行Python脚本...", syncName);
        long startTime = System.currentTimeMillis();
        
        try {
            ProcessBuilder pb = new ProcessBuilder(pythonExe, scriptPath);
            pb.redirectErrorStream(false);
            
            Process process = pb.start();
            
            // 异步读取stdout
            Thread stdoutReader = new Thread(() -> {
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(process.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        log.info("[{}] {}", syncName, line);
                    }
                } catch (Exception e) {
                    log.warn("[{}] 读取stdout异常", syncName);
                }
            });
            stdoutReader.start();
            
            // 异步读取stderr
            Thread stderrReader = new Thread(() -> {
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(process.getErrorStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        log.warn("[{}] stderr: {}", syncName, line);
                    }
                } catch (Exception e) {
                    log.warn("[{}] 读取stderr异常", syncName);
                }
            });
            stderrReader.start();
            
            // K线脚本最多60分钟，IPO脚本最多10分钟
            long timeout = scriptPath.contains("kline") ? 60 : 10;
            boolean finished = process.waitFor(timeout, TimeUnit.MINUTES);
            
            if (!finished) {
                process.destroyForcibly();
                log.error("【{}】超时（>{}分钟），强制终止", syncName, timeout);
                return;
            }
            
            int exitCode = process.exitValue();
            long elapsed = (System.currentTimeMillis() - startTime) / 1000;
            
            if (exitCode == 0) {
                log.info("【{}】完成！耗时: {}秒", syncName, elapsed);
            } else {
                log.error("【{}】失败，退出码: {}，耗时: {}秒", syncName, exitCode, elapsed);
            }
            
        } catch (Exception e) {
            log.error("【{}】执行异常", syncName, e);
        }
    }
}
