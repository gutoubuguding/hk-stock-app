package com.hkstock.dto;

import lombok.Data;

/** 注册请求参数 */
@Data
public class RegisterDTO {
    private String username;
    private String password;
    private String nickname;
    private String email;
}
