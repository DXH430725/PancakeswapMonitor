服务器将在以下端口启动：
- Web 界面：http://localhost:3000
- 心跳端点：http://localhost:3000/heartbeat
## 心跳包格式

客户端程序需要定期向 `/heartbeat` 端点发送 POST 请求，JSON 格式如下：

```json
{
  "serviceName": "My Service",
  "serviceId": "service-001",
  "heartbeatInterval": 30000,
  "status1": {
    "label": "请求统计",
    "总请求": 12345,
    "成功率": "99.5%",
    "平均延迟": "45ms"
  },
  "status2": {
    "label": "系统信息",
    "CPU使用率": "35%",
    "内存使用": "2.3 GB",
    "运行时间": "24小时"
  },
  "status3": {
    "label": "健康检查",
    "数据库": "已连接",
    "缓存": "正常",
    "队列": "正常"
  }
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `serviceName` | string | 是 | 服务名称 |
| `serviceId` | string | 是 | 服务唯一标识符（同一 ID 的心跳会更新同一服务） |
| `heartbeatInterval` | number | 否 | 心跳间隔（毫秒），默认 30000 |
| `status1` | object | 否 | 自定义状态字段 1，支持 `label` 属性自定义标题 |
| `status2` | object | 否 | 自定义状态字段 2，支持 `label` 属性自定义标题 |
| `status3` | object | 否 | 自定义状态字段 3，支持 `label` 属性自定义标题 |

### 状态字段 (status1/2/3) 详细说明

每个状态字段都是一个对象，支持以下两种用法：

**1. 使用 label 自定义标题（推荐）**

```json
"status1": {
  "label": "请求统计",
  "总请求": 12345,
  "成功率": "99.5%"
}
```

显示效果：
```
请求统计
总请求: 12345
成功率: 99.5%
```

**2. 不使用 label（使用默认标题）**

```json
"status1": {
  "requests": 12345,
  "success_rate": "99.5%"
}
```

显示效果：
```
STATUS 1
requests: 12345
success_rate: 99.5%
```