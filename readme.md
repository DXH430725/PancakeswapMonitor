# 🥞 PancakeSwap V3 LP Monitor

一个轻量级的 PancakeSwap V3 LP 状态监控脚本，可查询钱包持有的流动性头寸是否在区间内，并支持可选的 Telegram 通知与心跳上报。

> **🆕 最新更新：** 现在使用链上数据直接查询，实现**零延迟**实时监控！

---

## 🚀 功能特性

- ✅ **直接从链上获取数据** - 通过 Web3 直接查询智能合约，无延迟
- ✅ **实时状态更新** - 不依赖 The Graph 索引器，获取最新链上状态
- ✅ 自动判断是否 "IN RANGE / OUT OF RANGE"
- ✅ 显示详细的 Token 数量和交易对信息
- ✅ 可选 Telegram 通知
- ✅ 可选心跳包上报 `/heartbeat` 接口（默认关闭）
- ✅ 支持 BSC Mainnet 和 Testnet

---

## 🧩 安装依赖

```bash
pip install requests web3 eth-typing
```

---

## ⚙️ 配置说明

### 1. `pancake.py` - 私有配置版本

包含完整的配置信息，适合个人使用：

```python
# 链配置
CHAIN_ID = 56  # BSC Mainnet
RPC_URL = "https://binance.llamarpc.com/"
WALLET_ADDRESS = "0xYourWalletAddress"

# Telegram 配置
TG_BOT_TOKEN = "your-bot-token"
TG_CHAT_ID = "your-chat-id"
TG_THREAD_ID = 250

# 心跳包配置
HEARTBEAT_URL = "http://localhost:3000/heartbeat"
SERVICE_NAME = "Pancake LP Monitor"
SERVICE_ID = "dxh-pancake-lp-001"

# 检查间隔（秒）
CHECK_INTERVAL = 300
```

### 2. `pancake_lp_monitor_public.py` - 公开模板版本

适合分享和二次开发，需要用户自行配置：

```python
# 链配置
CHAIN_ID = 56  # BSC Mainnet (56) 或 BSC Testnet (97)
RPC_URL = None  # None 使用默认 RPC，或指定自定义 RPC
WALLET_ADDRESS = "0xYourWalletAddressHere"

# Telegram（可选）
TG_BOT_TOKEN = ""
TG_CHAT_ID = ""
TG_THREAD_ID = 250

# 心跳包（可选，默认关闭）
ENABLE_HEARTBEAT = False
```

---

## 🔧 RPC 配置

程序支持以下 RPC 配置方式（优先级从高到低）：

1. **代码中指定** - `RPC_URL = "https://your-rpc-url.com"`
2. **环境变量** - `PANCAKE_RPC_56=https://your-rpc-url.com`
3. **默认 RPC** - 使用内置的公共 RPC（可能有速率限制）

### 推荐的 BSC RPC 节点：

- `https://binance.llamarpc.com/`
- `https://bsc-dataseed.binance.org/`
- `https://bsc-dataseed1.defibit.io/`
- 或使用你自己的私有节点

---

## 📖 使用方法

### 1. 修改配置

编辑 `pancake.py` 或 `pancake_lp_monitor_public.py`，填入你的钱包地址和其他配置。

### 2. 运行监控

```bash
# 私有版本
python pancake.py

# 公开模板版本
python pancake_lp_monitor_public.py
```

### 3. 测试链上连接

```bash
python test_onchain.py
```

---

## 📊 输出示例

```
🚀 PancakeSwap LP 区间监控启动中（使用链上数据）...
📍 监控钱包: 0xaa5b8f7a2b69ef958b296ca0a070222612d055f6
⛓️ 链: BSC Mainnet (Chain ID: 56)
🔗 RPC: https://binance.llamarpc.com/
✅ 已连接到链上 RPC: https://binance.llamarpc.com/

=== PancakeSwap LP 状态 @ 2025-11-05 15:30:00 ===
🟢 IN RANGE | TokenID: 12345 | Pool: 0x1234567... | WBNB/USDT
  Tick=12345 | Range=[12000,13000] | LQ=1.23e+06
  WBNB: 1.234 | USDT: 456.789
```

---

## 🔔 Telegram 通知

当 LP 状态变化时（进入或离开区间），会自动发送 Telegram 通知：

```
PancakeSwap LP 状态变动
时间：2025-11-05 15:30:00
头寸 TokenID：12345
交易对：WBNB/USDT
池子地址：0x1234567...
当前Tick：12345
区间：[12000, 13000]
Token0: 1.234 WBNB
Token1: 456.789 USDT
状态：离开区间 🔴
```

---

## 🏗️ 项目结构

```
pancakeMonitor/
├── onchain/
│   ├── pancake_lp_detector.py    # 链上数据查询核心模块
│   └── pancake_constants.py      # 合约地址和 ABI 配置
├── pancake.py                     # 私有配置版本
├── pancake_lp_monitor_public.py  # 公开模板版本
├── test_onchain.py                # 测试脚本
└── readme.md                      # 说明文档
```

---

## 🔍 技术实现

### 旧版本（已弃用）
- 使用 The Graph GraphQL API 查询数据
- 存在索引延迟（几秒到几分钟）
- 依赖第三方索引服务

### 新版本（当前）
- 直接通过 Web3 查询链上合约：
  - `NonfungiblePositionManager` - 获取 LP NFT 信息
  - `PancakeV3Factory` - 获取池子地址
  - `Pool.slot0()` - 获取当前价格和 tick
- **零延迟**，实时获取最新状态
- 不依赖任何索引服务

### 核心合约

**BSC Mainnet (Chain ID: 56):**
- Factory: `0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865`
- Position Manager: `0x46A15B0b27311cedF172AB29E4f4766fbE7F4364`

**BSC Testnet (Chain ID: 97):**
- Factory: `0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865`
- Position Manager: `0x427bF5b37357632377eCbEC9de3626C71A5396c1`

---

## ❓ 常见问题

### Q: 为什么改用链上数据？
A: The Graph 索引器存在延迟，无法实时反映链上状态变化。直接查询链上数据可以实现零延迟监控。

### Q: 需要支付 Gas 费吗？
A: 不需要。程序只进行链上读取操作（view/pure 函数调用），完全免费。

### Q: 支持哪些链？
A: 目前支持 BSC Mainnet (56) 和 BSC Testnet (97)。可以通过修改 `onchain/pancake_constants.py` 添加其他链。

### Q: RPC 有速率限制怎么办？
A: 建议使用付费的 RPC 服务（如 Ankr、QuickNode、Alchemy）或自建节点。

### Q: 可以监控多个钱包吗？
A: 可以。修改代码，在循环中对多个钱包地址调用 `check_positions()` 即可。

---

## 📝 更新日志

### v2.0 (2025-11-05)
- 🎉 **重大更新：切换到链上数据获取**
- ✅ 移除对 The Graph API 的依赖
- ✅ 实现零延迟实时监控
- ✅ 增加 Token 数量和交易对信息显示
- ✅ 改进错误处理和日志输出
- ✅ 修复 Windows 控制台编码问题

### v1.0 (之前版本)
- 基于 The Graph GraphQL API
- 基础的区间监控功能
- Telegram 通知支持

---

## 📄 许可证

MIT License

---

## 👤 作者

DXH430

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
