#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PancakeSwap V3 LP 监控器 (Public Edition) - 使用链上数据
Author: DXH430
"""

import sys
import os

# 设置 stdout 编码为 UTF-8，避免 Windows 控制台编码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import requests
import time
from datetime import datetime

# 添加 onchain 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'onchain'))
from pancake_lp_detector import PancakeLPOwnerInspector

# ================== 用户配置 ==================
CHAIN_ID = 56  # BSC Mainnet (56) 或 BSC Testnet (97)
RPC_URL = None  # None 表示使用默认 RPC，也可以手动指定: "https://your-rpc-url.com"
WALLET_ADDRESS = "0xYourWalletAddressHere".lower()

# Telegram（可选）
TG_BOT_TOKEN = ""           # 例如：123456:ABCDEF
TG_CHAT_ID = ""             # 例如：-1002932618669
TG_THREAD_ID = 250          # 可选：线程 ID
CHECK_INTERVAL = 300        # 秒（默认每5分钟检查一次）

# 心跳包（默认关闭）
ENABLE_HEARTBEAT = False
HEARTBEAT_URL = "http://localhost:3000/heartbeat"
SERVICE_NAME = "Pancake LP Monitor"
SERVICE_ID = "lp-monitor-public"

# ================== 状态记录 ==================
last_status = {}
total_requests = 0
success_requests = 0
start_time = time.time()
inspector = None

# ================== 初始化链上查询器 ==================
def init_inspector():
    global inspector
    try:
        inspector = PancakeLPOwnerInspector(chain_id=CHAIN_ID, rpc_url=RPC_URL)
        rpc_used = RPC_URL if RPC_URL else "默认 RPC"
        print(f"✅ 已连接到链上，使用 RPC: {rpc_used}")
    except Exception as e:
        print(f"❌ 初始化链上查询器失败: {e}")
        sys.exit(1)

# ================== 从链上查询 LP 头寸 ==================
def fetch_positions(wallet: str):
    global total_requests, success_requests
    total_requests += 1
    try:
        positions = inspector.list_positions(owner=wallet, include_empty=False)
        success_requests += 1
        return positions
    except Exception as e:
        print(f"❌ 链上查询失败: {e}")
        return []

# ================== Telegram 通知 ==================
def send_tg(msg: str):
    if not TG_BOT_TOKEN or not TG_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "message_thread_id": TG_THREAD_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("⚠️ Telegram 发送失败:", e)

# ================== 可选：心跳上报 ==================
def send_heartbeat():
    uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    payload = {
        "serviceName": SERVICE_NAME,
        "serviceId": SERVICE_ID,
        "heartbeatInterval": CHECK_INTERVAL * 1000,
        "status1": {
            "label": "请求统计",
            "总请求": total_requests,
            "成功率": f"{(success_requests / total_requests * 100):.1f}%" if total_requests else "N/A",
        },
        "status2": {
            "label": "运行信息",
            "钱包": WALLET_ADDRESS,
            "运行时间": uptime,
            "上次更新": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    }
    try:
        r = requests.post(HEARTBEAT_URL, json=payload, timeout=10)
        if r.status_code == 200:
            print(f"💓 心跳成功 ({datetime.now().strftime('%H:%M:%S')})")
        else:
            print("⚠️ 心跳失败:", r.status_code)
    except Exception as e:
        print("❌ 心跳连接错误:", e)

# ================== 主逻辑 ==================
def check_positions():
    global last_status
    positions = fetch_positions(WALLET_ADDRESS)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n=== PancakeSwap LP 状态 @ {now} ===")

    if not positions:
        print("⚠️ 未找到任何 V3 头寸。")
        return

    for pos in positions:
        # 适配新的链上数据结构
        pos_id = str(pos["token_id"])
        pool_addr = pos["pool"]
        tick = int(pos["tick"]["current"])
        low = int(pos["tick"]["lower"])
        up = int(pos["tick"]["upper"])
        liq = float(pos["liquidity"])

        # 获取 token 信息
        token0_symbol = pos["tokens"]["token0"]["symbol"]
        token1_symbol = pos["tokens"]["token1"]["symbol"]
        token0_amount = pos["tokens"]["token0"]["amount"]
        token1_amount = pos["tokens"]["token1"]["amount"]

        in_range = low <= tick <= up
        status = "🟢 IN RANGE" if in_range else "🔴 OUT OF RANGE"
        print(f"{status} | TokenID: {pos_id} | Pool: {pool_addr[:10]}... | {token0_symbol}/{token1_symbol}")
        print(f"  Tick={tick} | Range=[{low},{up}] | LQ={liq:.2e}")
        print(f"  {token0_symbol}: {token0_amount} | {token1_symbol}: {token1_amount}")

        prev = last_status.get(pos_id)
        if prev is None:
            last_status[pos_id] = in_range
            continue
        if prev != in_range:
            last_status[pos_id] = in_range
            direction = "恢复在区间 🟢" if in_range else "离开区间 🔴"
            msg = (
                f"<b>PancakeSwap LP 状态变动</b>\n"
                f"时间：<code>{now}</code>\n"
                f"头寸 TokenID：<code>{pos_id}</code>\n"
                f"交易对：<code>{token0_symbol}/{token1_symbol}</code>\n"
                f"池子地址：<code>{pool_addr}</code>\n"
                f"当前Tick：<code>{tick}</code>\n"
                f"区间：[{low}, {up}]\n"
                f"Token0: {token0_amount} {token0_symbol}\n"
                f"Token1: {token1_amount} {token1_symbol}\n"
                f"状态：{direction}"
            )
            send_tg(msg)

# ================== 主循环 ==================
if __name__ == "__main__":
    print("🚀 PancakeSwap LP 监控器已启动（使用链上数据）")
    print(f"📍 监控钱包: {WALLET_ADDRESS}")
    print(f"⛓️ 链 ID: {CHAIN_ID}")
    print(f"⏱️ 检查间隔: {CHECK_INTERVAL} 秒")

    # 初始化链上查询器
    init_inspector()

    while True:
        check_positions()
        if ENABLE_HEARTBEAT:
            send_heartbeat()
        time.sleep(CHECK_INTERVAL)
