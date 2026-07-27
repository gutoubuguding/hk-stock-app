package com.hkstock.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.hkstock.domain.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
}
