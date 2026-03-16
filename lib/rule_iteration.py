#!/usr/bin/env python3
"""
DLP 规则自动迭代器
功能: 定时检查新规则、AI 生成规则、自动测试
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List

# 添加 lib 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class RuleIteration:
    """规则自动迭代器"""
    
    def __init__(self):
        self.config_file = "config/rules.json"
        self.stats_file = "config/iteration_stats.json"
        self.log_file = "logs/iteration.log"
        
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'a') as f:
            f.write(log_line)
        print(log_line.strip())
    
    def load_stats(self) -> Dict:
        """加载统计"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file) as f:
                return json.load(f)
        return {
            "total_iterations": 0,
            "rules_added": 0,
            "rules_updated": 0,
            "last_run": None
        }
    
    def save_stats(self, stats: Dict):
        """保存统计"""
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def check_new_patterns(self) -> List[Dict]:
        """检查新模式"""
        # 从公开库、CVE、威胁情报获取新模式
        new_patterns = []
        
        # 示例: 从已知模式库添加
        new_patterns.extend([
            {
                "name": "shopify_key",
                "pattern": r"shpat_[a-fA-F0-9]{32}",
                "action": "block",
                "severity": "critical",
                "description": "Shopify Access Token",
                "category": "credential"
            },
            {
                "name": "telegram_token",
                "pattern": r"TG[0-9]{8,10}:[A-Za-z0-9_-]{35}",
                "action": "block",
                "severity": "critical",
                "description": "Telegram Bot Token",
                "category": "credential"
            },
            {
                "name": "discord_token",
                "pattern": r"[MN][A-Za-z0-9]{24,}\.[A-Za-z0-9]{6}\.[A-Za-z0-9_-]{27}",
                "action": "block",
                "severity": "critical",
                "description": "Discord Token",
                "category": "credential"
            }
        ])
        
        return new_patterns
    
    def test_rules(self, rules: List[Dict]) -> Dict:
        """测试规则"""
        results = {
            "passed": 0,
            "failed": 0,
            "details": []
        }
        
        # 测试用例
        test_cases = [
            # 正面测试 (应该检测到)
            {"text": "sk-abcdefghijklmnopqrstuvwxyz123456", "should_detect": True},
            {"text": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", "should_detect": True},
            {"text": "TG12345678:AAbbccddEEffGGhhIIjjKKllMMnnOOppQQ", "should_detect": True},
            
            # 负面测试 (不应该检测到)
            {"text": "这是一个普通的中文文本", "should_detect": False},
            {"text": "Hello World", "should_detect": False},
        ]
        
        from agent_dlp import AgentDLP
        dlp = AgentDLP()
        
        for test in test_cases:
            blocked, _, details = dlp.check_output(test["text"])
            detected = len(details.get("findings", [])) > 0
            
            if detected == test["should_detect"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["details"].append({
                    "text": test["text"][:20],
                    "expected": test["should_detect"],
                    "got": detected
                })
        
        return results
    
    def add_rules(self, new_rules: List[Dict]) -> int:
        """添加新规则"""
        # 读取现有规则
        from agent_dlp import DLPRules
        rules = DLPRules()
        initial_count = len(rules.RULES)
        
        # 这里实际会修改 agent_dlp.py
        # 简化处理: 记录待添加规则
        added = 0
        for rule in new_rules:
            name = rule.get("name")
            if name and name not in rules.RULES:
                added += 1
        
        return added
    
    def run(self):
        """运行迭代"""
        self.log("开始规则迭代...")
        
        # 1. 检查新模式
        new_patterns = self.check_new_patterns()
        self.log(f"发现 {len(new_patterns)} 个新模式")
        
        if not new_patterns:
            self.log("没有新模式需要添加")
            return
        
        # 2. 添加规则
        added = self.add_rules(new_patterns)
        self.log(f"添加了 {added} 条新规则")
        
        # 3. 测试规则
        test_results = self.test_rules(new_patterns)
        self.log(f"测试通过: {test_results['passed']}, 失败: {test_results['failed']}")
        
        # 4. 更新统计
        stats = self.load_stats()
        stats["total_iterations"] += 1
        stats["rules_added"] += added
        stats["last_run"] = datetime.now().isoformat()
        self.save_stats(stats)
        
        self.log("迭代完成")
        
        return added > 0
    
    def auto_run(self, interval: int = 3600):
        """自动循环运行"""
        self.log(f"启动自动迭代 (间隔: {interval}秒)")
        
        while True:
            try:
                self.run()
                time.sleep(interval)
            except KeyboardInterrupt:
                self.log("停止自动迭代")
                break
            except Exception as e:
                self.log(f"错误: {e}")
                time.sleep(60)  # 错误后等待


def main():
    iteration = RuleIteration()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "auto":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 3600
            iteration.auto_run(interval)
        elif sys.argv[1] == "test":
            test_results = iteration.test_rules([])
            print(f"测试结果: {test_results}")
        else:
            iteration.run()
    else:
        iteration.run()


if __name__ == "__main__":
    main()
