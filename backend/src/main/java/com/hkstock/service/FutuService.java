package com.hkstock.service;

import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONArray;
import com.alibaba.fastjson2.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Futu OpenAPI 服务
 */
@Service
public class FutuService {
    private static final Logger log = LoggerFactory.getLogger(FutuService.class);


    @Value("${futu.opend-host:127.0.0.1}")
    private String opendHost;

    @Value("${futu.opend-port:11111}")
    private int opendPort;

    private static final int PROTOCOL_HEAD_SIZE = 44;
    private static final int CONNECTION_ID = 0;

    /**
     * 获取股票K线数据
     */
    public List<Map<String, Object>> getKlineData(String stockCode, String periodType, int count) {
        try {
            // 构造请求
            JSONObject req = new JSONObject();
            req.put("packetID", createPacketID());
            req.put("header", createHeader());
            
            JSONObject reqBody = new JSONObject();
            reqBody.put("code", stockCode);
            reqBody.put("rehabType", 0); // 不复权
            reqBody.put("periodType", convertPeriodType(periodType));
            reqBody.put("subType", 1); // 日K
            reqBody.put("updatePacketMode", 0);
            
            req.put("body", new JSONObject().put("req", reqBody));
            
            // 发送请求
            String response = sendRequest(3001, req.toJSONString()); // 3001 = GetKLine
            if (response == null) {
                return new ArrayList<>();
            }
            
            // 解析响应
            JSONObject resp = JSON.parseObject(response);
            JSONObject body = resp.getJSONObject("body");
            if (body == null || !body.containsKey("resp")) {
                return new ArrayList<>();
            }
            
            JSONObject respBody = body.getJSONObject("resp");
            if (respBody.getIntValue("retType") != 0) {
                log.error("获取K线数据失败: {}", respBody.getString("retMsg"));
                return new ArrayList<>();
            }
            
            // 解析K线数据
            JSONArray klineList = respBody.getJSONArray("kLineList");
            List<Map<String, Object>> result = new ArrayList<>();
            
            for (int i = 0; i < klineList.size(); i++) {
                JSONObject kline = klineList.getJSONObject(i);
                Map<String, Object> data = new HashMap<>();
                data.put("date", kline.getString("time"));
                data.put("open", kline.getBigDecimal("openPrice"));
                data.put("close", kline.getBigDecimal("closePrice"));
                data.put("high", kline.getBigDecimal("highPrice"));
                data.put("low", kline.getBigDecimal("lowPrice"));
                data.put("volume", kline.getLong("volume"));
                data.put("turnover", kline.getBigDecimal("turnover"));
                data.put("changePercent", kline.getBigDecimal("changeRate"));
                data.put("turnoverRate", kline.getBigDecimal("turnoverRate"));
                result.add(data);
            }
            
            return result;
            
        } catch (Exception e) {
            log.error("获取K线数据异常: {}", e.getMessage(), e);
            return new ArrayList<>();
        }
    }

    /**
     * 获取股票列表
     */
    public List<Map<String, Object>> getStockList() {
        try {
            JSONObject req = new JSONObject();
            req.put("packetID", createPacketID());
            req.put("header", createHeader());
            
            JSONObject reqBody = new JSONObject();
            reqBody.put("market", 1); // 港股市场
            reqBody.put("stockType", 1); // 正股
            
            req.put("body", new JSONObject().put("req", reqBody));
            
            String response = sendRequest(3002, req.toJSONString()); // 3002 = GetStockList
            if (response == null) {
                return new ArrayList<>();
            }
            
            JSONObject resp = JSON.parseObject(response);
            JSONObject body = resp.getJSONObject("body");
            if (body == null || !body.containsKey("resp")) {
                return new ArrayList<>();
            }
            
            JSONObject respBody = body.getJSONObject("resp");
            if (respBody.getIntValue("retType") != 0) {
                log.error("获取股票列表失败: {}", respBody.getString("retMsg"));
                return new ArrayList<>();
            }
            
            JSONArray stockList = respBody.getJSONArray("stockList");
            List<Map<String, Object>> result = new ArrayList<>();
            
            for (int i = 0; i < stockList.size(); i++) {
                JSONObject stock = stockList.getJSONObject(i);
                Map<String, Object> data = new HashMap<>();
                data.put("code", stock.getString("code"));
                data.put("name", stock.getString("name"));
                data.put("lotSize", stock.getIntValue("lotSize"));
                data.put("stockType", stock.getIntValue("stockType"));
                result.add(data);
            }
            
            return result;
            
        } catch (Exception e) {
            log.error("获取股票列表异常: {}", e.getMessage(), e);
            return new ArrayList<>();
        }
    }

    /**
     * 获取IPO列表
     */
    public List<Map<String, Object>> getIpoList() {
        try {
            JSONObject req = new JSONObject();
            req.put("packetID", createPacketID());
            req.put("header", createHeader());
            
            JSONObject reqBody = new JSONObject();
            reqBody.put("market", 1); // 港股市场
            
            req.put("body", new JSONObject().put("req", reqBody));
            
            String response = sendRequest(3200, req.toJSONString()); // 3200 = GetIPOList
            if (response == null) {
                return new ArrayList<>();
            }
            
            JSONObject resp = JSON.parseObject(response);
            JSONObject body = resp.getJSONObject("body");
            if (body == null || !body.containsKey("resp")) {
                return new ArrayList<>();
            }
            
            JSONObject respBody = body.getJSONObject("resp");
            if (respBody.getIntValue("retType") != 0) {
                log.error("获取IPO列表失败: {}", respBody.getString("retMsg"));
                return new ArrayList<>();
            }
            
            JSONArray ipoList = respBody.getJSONArray("ipoList");
            List<Map<String, Object>> result = new ArrayList<>();
            
            for (int i = 0; i < ipoList.size(); i++) {
                JSONObject ipo = ipoList.getJSONObject(i);
                Map<String, Object> data = new HashMap<>();
                data.put("code", ipo.getString("code"));
                data.put("name", ipo.getString("name"));
                data.put("listTime", ipo.getString("listTime"));
                data.put("listTimestamp", ipo.getLongValue("listTimestamp"));
                data.put("ipoPrice", ipo.getBigDecimal("ipoPrice"));
                data.put("issueSize", ipo.getLongValue("issueSize"));
                result.add(data);
            }
            
            return result;
            
        } catch (Exception e) {
            log.error("获取IPO列表异常: {}", e.getMessage(), e);
            return new ArrayList<>();
        }
    }

    /**
     * 发送请求到Futu OpenD
     */
    private String sendRequest(int commandId, String jsonData) {
        try (Socket socket = new Socket(opendHost, opendPort);
             OutputStream os = socket.getOutputStream();
             InputStream is = socket.getInputStream()) {
            
            // 构造协议头
            byte[] header = createProtocolHeader(commandId, jsonData.length());
            
            // 发送请求
            os.write(header);
            os.write(jsonData.getBytes("UTF-8"));
            os.flush();
            
            // 读取响应头
            byte[] respHeader = new byte[PROTOCOL_HEAD_SIZE];
            int bytesRead = is.read(respHeader);
            if (bytesRead < PROTOCOL_HEAD_SIZE) {
                log.error("读取响应头失败");
                return null;
            }
            
            // 解析响应头
            ByteBuffer buffer = ByteBuffer.wrap(respHeader).order(ByteOrder.LITTLE_ENDIAN);
            int nHeadSize = buffer.getShort() & 0xFFFF;
            int nProtoID = buffer.getShort() & 0xFFFF;
            int nProtoFmtType = buffer.get() & 0xFF;
            int nProtoVer = buffer.get() & 0xFF;
            int nSerialNo = buffer.getInt();
            int nBodyLen = buffer.getInt();
            
            // 读取响应体
            if (nBodyLen > 0) {
                byte[] body = new byte[nBodyLen];
                bytesRead = is.read(body);
                if (bytesRead < nBodyLen) {
                    log.error("读取响应体失败");
                    return null;
                }
                return new String(body, "UTF-8");
            }
            
            return null;
            
        } catch (Exception e) {
            log.error("发送请求异常: {}", e.getMessage(), e);
            return null;
        }
    }

    /**
     * 创建协议头
     */
    private byte[] createProtocolHeader(int commandId, int bodyLength) {
        ByteBuffer buffer = ByteBuffer.allocate(PROTOCOL_HEAD_SIZE).order(ByteOrder.LITTLE_ENDIAN);
        buffer.putShort((short) PROTOCOL_HEAD_SIZE); // nHeadSize
        buffer.putShort((short) commandId); // nProtoID
        buffer.put((byte) 2); // nProtoFmtType = JSON
        buffer.put((byte) 1); // nProtoVer = 1
        buffer.putInt(1); // nSerialNo
        buffer.putInt(bodyLength); // nBodyLen
        buffer.putLong(0); // nConnID
        buffer.putInt(0); // nConnID (high)
        buffer.putInt(0); // nConnID (low)
        buffer.putInt(0); // nCheckSum (简化处理)
        
        return buffer.array();
    }

    /**
     * 创建包ID
     */
    private JSONObject createPacketID() {
        JSONObject packetID = new JSONObject();
        packetID.put("connID", CONNECTION_ID);
        packetID.put("serialNo", 1);
        return packetID;
    }

    /**
     * 创建请求头
     */
    private JSONObject createHeader() {
        JSONObject header = new JSONObject();
        header.put("trdSide", 0);
        header.put("packetID", createPacketID());
        return header;
    }

    /**
     * 转换周期类型
     */
    private int convertPeriodType(String periodType) {
        return switch (periodType.toUpperCase()) {
            case "D", "5D" -> 1; // 日K / 5日（取最近5根日K）
            case "W" -> 2; // 周K
            case "M" -> 3; // 月K
            case "Y" -> 4; // 年K
            default -> 1;
        };
    }
}
