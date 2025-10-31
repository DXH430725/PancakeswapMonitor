# 🥞 PancakeSwap V3 LP Monitor (Public Edition)

一个轻量级的 PancakeSwap V3 LP 状态监控脚本，可查询钱包持有的流动性头寸是否在区间内，并支持可选的 Telegram 通知与心跳上报。

---

## 🚀 功能特性

- ✅ 通过 The Graph 子图接口获取 LP 状态  
- ✅ 自动判断是否 “IN RANGE / OUT OF RANGE”  
- ✅ 可选 Telegram 通知  
- ✅ 可选心跳包上报 `/heartbeat` 接口（默认关闭）  
- ✅ 轻量无依赖，跨平台可运行  

---

## 🧩 安装依赖

```bash
pip install requests
