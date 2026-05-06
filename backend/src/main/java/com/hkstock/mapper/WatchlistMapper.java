package com.hkstock.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.hkstock.entity.Watchlist;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface WatchlistMapper extends BaseMapper<Watchlist> {
}
