package com.hkstock.service;

import com.hkstock.domain.User;

/** 用户服务接口 */
public interface UserService {

    /** 用户登录 */
    User login(String username, String password);

    /** 用户注册 */
    User register(String username, String password, String nickname, String email);

    /** 根据用户名查找用户 */
    User findByUsername(String username);

    /** 根据ID查找用户 */
    User findById(Long id);
}
