#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PancakeSwap V3 LP 监控器 (Public Edition)
Author: DXH430
"""

import requests
import time
from datetime import datetime

# ================== 用户配置 ==================
GRAPH_URL = "https://gateway.thegraph.com/api/subgraphs/id/A1BC1hzDsK4NTeXBpKQnDBphngpYZAwDUF7dEBfa3jHK"
API_KEY = ""  # ❌ 默认留空，请在环境变量或手动填写
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

# ================== GraphQL 查询 ==================
def fetch_positions(wallet: str):
    global total_requests, success_requests
    total_requests += 1

    query = (
        '{ positions(where:{account:"' + wallet +
        '"} first:50 orderBy:id orderDirection:asc subgraphError:allow)'
        '{id liquidity tickLower{index} tickUpper{index} pool{id tick}} }'
    )

    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    try:
        res = requests.post(GRAPH_URL, headers=headers, json={"query": query}, timeout=20)
        if res.status_code == 200:
            success_requests += 1
        else:
            print(f"⚠️ HTTP {res.status_code}: {res.text[:200]}")
            return []
        data = res.json()
        if "errors" in data:
            print("⚠️ GraphQL 错误:", data["errors"])
            return []
        return data.get("data", {}).get("positions", [])
    except Exception as e:
        print(f"❌ 请求失败: {e}")
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
        pos_id = pos["id"]
        pool = pos["pool"]
        tick = int(pool["tick"])
        low = int(pos["tickLower"]["index"])
        up = int(pos["tickUpper"]["index"])
        liq = float(pos["liquidity"])
        in_range = low <= tick <= up
        status = "🟢 IN RANGE" if in_range else "🔴 OUT OF RANGE"
        print(f"{status} | Pool: {pool['id'][:10]}... | Tick={tick} | Range=[{low},{up}] | LQ={liq:.2e}")

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
                f"头寸ID：<code>{pos_id}</code>\n"
                f"池子ID：<code>{pool['id']}</code>\n"
                f"当前Tick：<code>{tick}</code>\n"
                f"区间：[{low}, {up}]\n"
                f"状态：{direction}"
            )
            send_tg(msg)

# ================== 主循环 ==================
if __name__ == "__main__":
    print("🚀 PancakeSwap LP 监控器已启动")
    while True:
        check_positions()
        if ENABLE_HEARTBEAT:
            send_heartbeat()
        time.sleep(CHECK_INTERVAL)
