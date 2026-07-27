package com.hkstock.query;

import lombok.Data;

/** IPO对比查询参数 */
@Data
public class IpoComparisonQuery {
    private String sortBy = "listingDate";
    private String sortOrder = "desc";
}
