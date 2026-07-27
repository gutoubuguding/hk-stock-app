package com.hkstock.controller;

import com.hkstock.common.ApiResponse;
import com.hkstock.domain.User;
import com.hkstock.dto.LoginDTO;
import com.hkstock.dto.RegisterDTO;
import com.hkstock.service.UserService;
import com.hkstock.utils.JWTUtil;
import com.hkstock.vo.UserVO;
import jakarta.annotation.Resource;
import java.util.HashMap;
import java.util.Map;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

/** 用户控制器 */
@RestController
@RequestMapping("/api/user")
public class UserController {

    @Resource
    private UserService userService;

    @Value("${secret:}")
    private String secret;

    /** 用户登录 */
    @PostMapping("/login")
    public ApiResponse<UserVO> login(@RequestBody LoginDTO dto) {
        // 参数校验
        if (dto.getUsername() == null || dto.getUsername().isBlank()) {
            return ApiResponse.error("用户名不能为空");
        }
        if (dto.getPassword() == null || dto.getPassword().isBlank()) {
            return ApiResponse.error("密码不能为空");
        }

        // 登录验证
        User user = userService.login(dto.getUsername(), dto.getPassword());
        if (user == null) {
            return ApiResponse.error("账号或密码错误");
        }

        // 生成 JWT token
        Map<String, String> payload = new HashMap<>();
        payload.put("username", user.getUsername());
        payload.put("id", user.getId().toString());
        String token = JWTUtil.generateToken(secret, 3600, payload);

        // 转换为 VO（不含密码）
        UserVO vo = new UserVO();
        BeanUtils.copyProperties(user, vo);

        // 返回 token 在 message 中，用户信息在 data 中
        return new ApiResponse<>(200, token, null, vo);
    }

    /** 用户注册 */
    @PostMapping("/register")
    public ApiResponse<UserVO> register(@RequestBody RegisterDTO dto) {
        // 参数校验
        if (dto.getUsername() == null || dto.getUsername().isBlank()) {
            return ApiResponse.error("用户名不能为空");
        }
        if (dto.getPassword() == null || dto.getPassword().isBlank()) {
            return ApiResponse.error("密码不能为空");
        }
        if (dto.getUsername().length() < 3 || dto.getUsername().length() > 20) {
            return ApiResponse.error("用户名长度3-20位");
        }
        if (dto.getPassword().length() < 6 || dto.getPassword().length() > 30) {
            return ApiResponse.error("密码长度6-30位");
        }

        // 注册
        User user = userService.register(dto.getUsername(), dto.getPassword(), dto.getNickname(), dto.getEmail());

        // 转换为 VO
        UserVO vo = new UserVO();
        BeanUtils.copyProperties(user, vo);

        return ApiResponse.success("注册成功", vo);
    }

    /** 获取当前用户信息 */
    @GetMapping("/info")
    public ApiResponse<UserVO> getUserInfo(@RequestAttribute("username") String username) {
        User user = userService.findByUsername(username);
        if (user == null) {
            return ApiResponse.error("用户不存在");
        }
        UserVO vo = new UserVO();
        BeanUtils.copyProperties(user, vo);
        return ApiResponse.success(vo);
    }
}
