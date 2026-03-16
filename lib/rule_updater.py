#!/usr/bin/env python3
"""
DLP 规则自动更新器
功能: 自动检测规则更新、下载新规则、合并规则
"""

import json
import os
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

class RuleUpdater:
    """规则自动更新器"""
    
    # 规则源 (可扩展)
    RULE_SOURCES = {
        "crypto": [
            r"https://raw.githubusercontent.com/ethereum/execution-specs/main/",
        ],
        "credential": [
            # GitHub 安全规则
        ]
    }
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "config/rules.json"
        self.rules = {}
        self.last_update = None
        
    def load_rules(self) -> Dict:
        """加载现有规则"""
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                return json.load(f)
        return {}
    
    def save_rules(self, rules: Dict):
        """保存规则"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
            
    def check_update(self) -> bool:
        """检查是否有更新"""
        # 检查远程版本
        current = self.load_rules().get("version", "0.0.0")
        remote = self.fetch_remote_version()
        return remote > current if remote else False
    
    def fetch_remote_version(self) -> Optional[str]:
        """获取远程版本号"""
        # 实际实现中从 API 获取
        return None
    
    def fetch_new_rules(self) -> Dict:
        """获取新规则"""
        # 从远程或生成 AI 规则
        new_rules = {}
        
        # 1. 从公开源获取
        new_rules.update(self.fetch_public_rules())
        
        # 2. AI 辅助生成
        new_rules.update(self.ai_generate_rules())
        
        return new_rules
    
    def fetch_public_rules(self) -> Dict:
        """从公开源获取规则"""
        rules = {}
        
        # 加密货币地址格式
        crypto_patterns = {
            "ltc_address": {
                "pattern": r"[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}",
                "action": "block",
                "severity": "high",
                "description": "莱特币地址",
                "category": "crypto"
            },
            "xrp_address": {
                "pattern": r"r[1-9A-HJ-NP-Za-km-z]{24,34}",
                "action": "block",
                "severity": "high",
                "description": "瑞波币地址",
                "category": "crypto"
            },
            "dot_address": {
                "pattern": r"[1][a-zA-Z0-9]{6,}",
                "action": "block",
                "severity": "high",
                "description": "波卡地址",
                "category": "crypto"
            }
        }
        rules.update(crypto_patterns)
        
        return rules
    
    def ai_generate_rules(self) -> Dict:
        """AI 辅助规则生成"""
        # 基于常见模式生成规则
        rules = {}
        
        # 常见 API Key 模式
        api_patterns = [
            ("telegram_key", r"TG-[0-9]{8,10}:[A-Za-z0-9_-]{35}", "Telegram Bot Token"),
            ("discord_key", r"[MN][A-Za-z0-9]{24,}\.[A-Za-z0-9]{6}\.[A-Za-z0-9_-]{27}", "Discord Token"),
            ("notion_key", r"secret_[a-zA-Z0-9]{43,}", "Notion API Key"),
            ("shopify_key", r"shpat_[a-fA-F0-9]{32}", "Shopify Access Token"),
            ("square_key", r"sq0atp-[0-9A-Za-z_-]{22}", "Square Access Token"),
            ("stripe_key", r"sk_live_[0-9a-zA-Z]{24,}", "Stripe Live Key"),
        ]
        
        for name, pattern, desc in api_patterns:
            rules[name] = {
                "pattern": pattern,
                "action": "block",
                "severity": "critical",
                "description": desc,
                "category": "credential"
            }
        
        return rules
    
    def merge_rules(self, new_rules: Dict) -> Dict:
        """合并规则"""
        current = self.load_rules()
        existing = current.get("rules", {})
        
        # 合并并去重
        merged = existing.copy()
        for name, rule in new_rules.items():
            if name not in merged:
                merged[name] = rule
            elif rule != merged[name]:
                # 保留更严格的规则
                if rule.get("severity") == "critical":
                    merged[name] = rule
        
        return merged
    
    def update(self) -> bool:
        """执行更新"""
        if not self.check_update():
            print("规则已是最新")
            return False
        
        new_rules = self.fetch_new_rules()
        merged = self.merge_rules(new_rules)
        
        # 备份当前规则
        self.backup()
        
        # 保存新规则
        self.save_rules({
            "version": "2.2.0",
            "updated": datetime.now().isoformat(),
            "rules": merged
        })
        
        print(f"规则已更新: {len(merged)} 条")
        return True
    
    def backup(self):
        """备份当前规则"""
        if os.path.exists(self.config_path):
            backup_path = self.config_path + ".bak"
            with open(self.config_path) as f:
                content = f.read()
            with open(backup_path, 'w') as f:
                f.write(content)
            print(f"已备份到: {backup_path}")


def main():
    import sys
    updater = RuleUpdater()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            print(f"需要更新: {updater.check_update()}")
        elif sys.argv[1] == "update":
            updater.update()
        elif sys.argv[1] == "generate":
            rules = updater.ai_generate_rules()
            print(f"AI 生成规则: {len(rules)} 条")
            for name in rules:
                print(f"  - {name}")
    else:
        print("用法: python rule_updater.py [check|update|generate]")


if __name__ == "__main__":
    main()
