package com.hkstock.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.hkstock.domain.User;
import com.hkstock.exception.BusinessException;
import com.hkstock.mapper.UserMapper;
import com.hkstock.service.UserService;
import jakarta.annotation.Resource;
import java.time.LocalDateTime;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.DigestUtils;

/** 用户服务实现 */
@Service
public class UserServiceImpl implements UserService {

    @Resource
    private UserMapper userMapper;

    @Value("${salt:}")
    private String salt;

    @Override
    public User login(String username, String password) {
        // 密码加盐MD5加密
        String encryptedPassword = encryptPassword(password);

        // 查询用户
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, username)
               .eq(User::getPassword, encryptedPassword);
        return userMapper.selectOne(wrapper);
    }

    @Override
    public User register(String username, String password, String nickname, String email) {
        // 检查用户名是否已存在
        User existing = findByUsername(username);
        if (existing != null) {
            throw new BusinessException("用户名已存在");
        }

        // 创建用户
        User user = new User();
        user.setUsername(username);
        user.setPassword(encryptPassword(password));
        user.setNickname(nickname != null ? nickname : username);
        user.setEmail(email);
        user.setCreatedAt(LocalDateTime.now());
        user.setUpdatedAt(LocalDateTime.now());

        userMapper.insert(user);
        return user;
    }

    @Override
    public User findByUsername(String username) {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, username);
        return userMapper.selectOne(wrapper);
    }

    @Override
    public User findById(Long id) {
        return userMapper.selectById(id);
    }

    /** 密码加密：password + salt -> MD5 */
    private String encryptPassword(String password) {
        String raw = password + salt;
        return DigestUtils.md5DigestAsHex(raw.getBytes());
    }
}
