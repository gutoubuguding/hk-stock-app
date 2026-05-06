package com.hkstock.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.hkstock.entity.News;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface NewsMapper extends BaseMapper<News> {

    @Select("SELECT * FROM news WHERE stock_code = #{stockCode} AND publish_time >= NOW() - (#{days} * INTERVAL '1 day') ORDER BY publish_time DESC")
    List<News> selectByStockCodeAndDays(@Param("stockCode") String stockCode, @Param("days") Integer days);
}
