package com.hkstock.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.hkstock.entity.StockKline;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface StockKlineMapper extends BaseMapper<StockKline> {
}
