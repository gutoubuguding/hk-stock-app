package com.hkstock.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.hkstock.domain.StockInfo;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface StockInfoMapper extends BaseMapper<StockInfo> {}
