package com.hkstock.vo;

import java.time.LocalDateTime;
import lombok.Data;

/** 用户视图对象（不含密码） */
@Data
public class UserVO {
    private Long id;
    private String username;
    private String nickname;
    private String email;
    private LocalDateTime createdAt;
}
