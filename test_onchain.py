#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试链上数据获取功能
"""

import sys
import os

# 设置 stdout 编码为 UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# 添加 onchain 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'onchain'))

try:
    from pancake_lp_detector import PancakeLPOwnerInspector
    print("✅ 成功导入 PancakeLPOwnerInspector")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 测试配置
CHAIN_ID = 56
WALLET = "0xxxxxxxxxxxx"
RPC_URL = "https://binance.llamarpc.com/"

print(f"\n正在初始化链上查询器...")
print(f"Chain ID: {CHAIN_ID}")
print(f"RPC URL: {RPC_URL}")
print(f"钱包地址: {WALLET}")

try:
    inspector = PancakeLPOwnerInspector(chain_id=CHAIN_ID, rpc_url=RPC_URL)
    print("✅ 链上查询器初始化成功")
except Exception as e:
    print(f"❌ 初始化失败: {e}")
    sys.exit(1)

print(f"\n正在查询 LP 头寸...")
try:
    positions = inspector.list_positions(owner=WALLET, include_empty=False, limit=5)
    print(f"✅ 查询成功，找到 {len(positions)} 个头寸")

    if positions:
        print("\n头寸详情:")
        for idx, pos in enumerate(positions, 1):
            print(f"\n[{idx}] TokenID: {pos['token_id']}")
            print(f"    Pool: {pos['pool']}")
            print(f"    Fee: {pos['fee']}")
            print(f"    Tick: {pos['tick']['current']} (Range: [{pos['tick']['lower']}, {pos['tick']['upper']}])")
            print(f"    Token0: {pos['tokens']['token0']['symbol']} - {pos['tokens']['token0']['amount']}")
            print(f"    Token1: {pos['tokens']['token1']['symbol']} - {pos['tokens']['token1']['amount']}")
            print(f"    Liquidity: {pos['liquidity']}")

            # 检查是否在区间内
            in_range = pos['tick']['lower'] <= pos['tick']['current'] <= pos['tick']['upper']
            status = "🟢 IN RANGE" if in_range else "🔴 OUT OF RANGE"
            print(f"    Status: {status}")
    else:
        print("⚠️ 未找到任何头寸")

except Exception as e:
    print(f"❌ 查询失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ 测试完成！")
