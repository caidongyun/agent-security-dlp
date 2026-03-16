#!/usr/bin/env python3
"""
行业专用规则深化
为特定行业生成更精确的规则
"""

import re
from typing import Dict, List

class IndustryRules:
    """行业专用规则生成器"""
    
    @staticmethod
    def generate_fintech_rules() -> Dict:
        """金融科技行业规则"""
        return {
            # 支付网关
            "paypal_email": {
                "pattern": r"paypal\.[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "action": "sanitize",
                "severity": "high",
                "description": "PayPal 关联邮箱",
                "category": "fintech"
            },
            "alipay_id": {
                "pattern": r"(?i)支付宝[:=]\s*[a-zA-Z0-9]{6,20}",
                "action": "sanitize",
                "severity": "high",
                "description": "支付宝账号",
                "category": "fintech"
            },
            "wechat_pay_id": {
                "pattern": r"(?i)微信支付[:=]\s*[a-zA-Z0-9]{6,20}",
                "action": "sanitize",
                "severity": "high",
                "description": "微信支付账号",
                "category": "fintech"
            },
            
            # 交易信息
            "transaction_id": {
                "pattern": r"(?i)交易流水号[:=]\s*[A-Za-z0-9]{10,30}",
                "action": "sanitize",
                "severity": "medium",
                "description": "交易流水号",
                "category": "fintech"
            },
            "order_amount": {
                "pattern": r"(?i)(金额|总额|价格)[:=]\s*[¥$€£]?\d+[,，.]?\d*",
                "action": "sanitize",
                "severity": "low",
                "description": "交易金额",
                "category": "fintech"
            }
        }
    
    @staticmethod
    def generate_healthcare_rules() -> Dict:
        """医疗健康行业规则"""
        return {
            # 病历信息
            "patient_name": {
                "pattern": r"(?i)患者姓名[:=]\s*[^\s,，]{2,10}",
                "action": "sanitize",
                "severity": "high",
                "description": "患者姓名",
                "category": "healthcare"
            },
            "patient_id": {
                "pattern": r"(?i)患者ID[:=]\s*[A-Za-z0-9]{6,15}",
                "action": "block",
                "severity": "critical",
                "description": "患者ID",
                "category": "healthcare"
            },
            "medical_insurance_no": {
                "pattern": r"(?i)(医保|社保)号码[:=]\s*\d{8,18}",
                "action": "block",
                "severity": "critical",
                "description": "医保/社保号码",
                "category": "healthcare"
            },
            
            # 处方信息
            "prescription_no": {
                "pattern": r"(?i)处方号[:=]\s*[A-Za-z0-9]{6,15}",
                "action": "sanitize",
                "severity": "high",
                "description": "处方号",
                "category": "healthcare"
            },
            "medication": {
                "pattern": r"(?i)(药品|药物)名称[:=][^\n]{2,20}",
                "action": "sanitize",
                "severity": "medium",
                "description": "药品名称",
                "category": "healthcare"
            }
        }
    
    @staticmethod
    def generate_ecommerce_rules() -> Dict:
        """电商行业规则"""
        return {
            # 店铺信息
            "shop_name": {
                "pattern": r"(?i)店铺名称[:=][^\n]{2,30}",
                "action": "sanitize",
                "severity": "low",
                "description": "店铺名称",
                "category": "ecommerce"
            },
            "merchant_id": {
                "pattern": r"(?i)商户ID[:=]\s*[A-Za-z0-9]{8,15}",
                "action": "sanitize",
                "severity": "medium",
                "description": "商户ID",
                "category": "ecommerce"
            },
            
            # 订单信息
            "ebay_order_id": {
                "pattern": r"[0-9]{12,}",
                "action": "sanitize",
                "severity": "low",
                "description": "eBay 订单号",
                "category": "ecommerce"
            },
            "amazon_order_id": {
                "pattern": r"114-[0-9]{7}-[0-9]{7}",
                "action": "sanitize",
                "severity": "low",
                "description": "Amazon 订单号",
                "category": "ecommerce"
            }
        }
    
    @staticmethod
    def generate_manufacturing_rules() -> Dict:
        """制造业规则"""
        return {
            # 生产信息
            "production_no": {
                "pattern": r"(?i)(生产|批次)号[:=]\s*[A-Za-z0-9]{8,20}",
                "action": "sanitize",
                "severity": "low",
                "description": "生产批次号",
                "category": "manufacturing"
            },
            "serial_no": {
                "pattern": r"(?i)序列号[:=]\s*[A-Za-z0-9]{8,20}",
                "action": "sanitize",
                "severity": "medium",
                "description": "产品序列号",
                "category": "manufacturing"
            },
            
            # 供应链
            "supplier_id": {
                "pattern": r"(?i)供应商ID[:=]\s*[A-Za-z0-9]{6,15}",
                "action": "sanitize",
                "severity": "low",
                "description": "供应商ID",
                "category": "manufacturing"
            }
        }
    
    @staticmethod
    def generate_government_rules() -> Dict:
        """政府/政务行业规则"""
        return {
            # 公务员
            "civil_servant_no": {
                "pattern": r"(?i)公务编号[:=]\s*[A-Za-z0-9]{6,15}",
                "action": "block",
                "severity": "critical",
                "description": "公务员编号",
                "category": "government"
            },
            
            # 政务信息
            "case_no": {
                "pattern": r"(?i)(案件|案号)[:=]\s*[A-Za-z0-9]{8,20}",
                "action": "sanitize",
                "severity": "high",
                "description": "案件编号",
                "category": "government"
            },
            
            # 证件
            "police_no": {
                "pattern": r"(?i)警官证号[:=]\s*[A-Za-z0-9]{8,12}",
                "action": "block",
                "severity": "critical",
                "description": "警官证号",
                "category": "government"
            }
        }
    
    @classmethod
    def get_all_industry_rules(cls) -> Dict:
        """获取所有行业规则"""
        all_rules = {}
        all_rules.update(cls.generate_fintech_rules())
        all_rules.update(cls.generate_healthcare_rules())
        all_rules.update(cls.generate_ecommerce_rules())
        all_rules.update(cls.generate_manufacturing_rules())
        all_rules.update(cls.generate_government_rules())
        return all_rules
    
    @classmethod
    def generate_all(cls) -> Dict:
        """生成所有行业深化规则"""
        return cls.get_all_industry_rules()


def main():
    rules = IndustryRules.generate_all()
    print(f"行业深化规则: {len(rules)} 条")
    print()
    
    categories = {}
    for name, rule in rules.items():
        cat = rule.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
