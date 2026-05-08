package com.hkstock.controller;

import com.hkstock.entity.Watchlist;
import com.hkstock.service.WatchlistService;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/** 自选股控制器 */
@RestController
@RequestMapping("/api/watchlist")
public class WatchlistController {

  private @Autowired WatchlistService watchlistService;

  /** 获取自选股列表 */
  @GetMapping
  public List<Watchlist> getWatchlist() {
    return watchlistService.getWatchlist();
  }

  /** 添加自选股 */
  @PostMapping
  public Map<String, String> addToWatchlist(@RequestBody Watchlist watchlist) {
    watchlistService.addToWatchlist(watchlist);
    return Map.of("status", "success");
  }

  /** 删除自选股 */
  @DeleteMapping("/{stockCode}")
  public Map<String, String> removeFromWatchlist(@PathVariable String stockCode) {
    watchlistService.removeFromWatchlist(stockCode);
    return Map.of("status", "success");
  }
}
