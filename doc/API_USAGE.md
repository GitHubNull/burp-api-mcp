# API 使用教程

本教程介绍如何使用 MCP 工具查询 Burp Suite Montoya API 文档。

---

## 📋 可用工具一览

| 工具名 | 功能 | 使用场景 |
|--------|------|----------|
| `search_api` | 搜索 API | 不知道具体接口名，模糊搜索 |
| `get_interface` | 获取接口详情 | 查看接口的所有方法和继承关系 |
| `list_interfaces` | 列出接口 | 查看某个包下的所有接口 |
| `get_method_signature` | 获取方法签名 | 查看方法的参数和返回值 |
| `get_package_info` | 获取包信息 | 了解包结构和包含的接口 |

---

## 🔍 工具详细说明

### 1. search_api - 搜索 API

**功能**: 在接口、方法、包中搜索关键词

**参数**:
- `query` (必需): 搜索关键词
- `type` (可选): 搜索类型，`interface`/`method`/`package`/`all`
- `limit` (可选): 返回结果数量上限，默认 10

**使用示例**:

```json
{
  "name": "search_api",
  "arguments": {
    "query": "HttpRequest",
    "type": "interface",
    "limit": 5
  }
}
```

**返回结果示例**:
```
**Interface**: `burp.api.montoya.http.message.requests.HttpRequest`
Provides methods to access and modify HTTP requests.

**Interface**: `burp.api.montoya.http.message.requests.HttpRequest.Builder`
Builder for HttpRequest instances.
```

**实用场景**:
- 忘记接口全名，只记得部分关键词
- 想找到所有与"request"相关的接口
- 查找包含特定方法的接口

---

### 2. get_interface - 获取接口详情

**功能**: 获取指定接口的完整信息，包括所有方法、继承关系、文档

**参数**:
- `name` (必需): 接口名（可以是简单名或全限定名）

**使用示例**:

```json
{
  "name": "get_interface",
  "arguments": {
    "name": "HttpRequest"
  }
}
```

**返回内容**:
- 接口描述
- Javadoc 注释
- 继承的接口
- 所有方法列表（包括方法签名和描述）

**实用场景**:
- 开发扩展时需要了解接口的所有方法
- 查看接口的继承层次
- 阅读接口的详细文档

---

### 3. list_interfaces - 列出接口

**功能**: 列出所有接口，可按包名筛选

**参数**:
- `package` (可选): 包名筛选
- `limit` (可选): 返回数量上限，默认 50

**使用示例**:

**列出所有接口**:
```json
{
  "name": "list_interfaces",
  "arguments": {
    "limit": 20
  }
}
```

**列出特定包下的接口**:
```json
{
  "name": "list_interfaces",
  "arguments": {
    "package": "burp.api.montoya.http",
    "limit": 20
  }
}
```

**实用场景**:
- 浏览 API 结构
- 查看某个模块包含哪些接口
- 快速了解 API 的组织方式

---

### 4. get_method_signature - 获取方法签名

**功能**: 获取指定方法的详细签名，包括参数、返回值、异常

**参数**:
- `interface` (必需): 接口名
- `method` (必需): 方法名

**使用示例**:

```json
{
  "name": "get_method_signature",
  "arguments": {
    "interface": "HttpRequest",
    "method": "withBody"
  }
}
```

**返回内容**:
- 方法签名
- 参数列表（类型和描述）
- 返回类型
- 可能抛出的异常
- 完整 Javadoc

**实用场景**:
- 编写代码时需要知道方法的确切参数
- 了解方法的返回值类型
- 查看方法可能抛出的异常

---

### 5. get_package_info - 获取包信息

**功能**: 获取包的详细信息，包括包内所有接口

**参数**:
- `name` (必需): 包名

**使用示例**:

```json
{
  "name": "get_package_info",
  "arguments": {
    "name": "burp.api.montoya.http"
  }
}
```

**实用场景**:
- 了解某个包的组织结构
- 查看包内有哪些可用接口

---

## 💡 实用查询场景

### 场景 1：开发 HTTP 处理器扩展

**目标**: 开发一个 HTTP 请求处理器

**查询步骤**:

1. **搜索相关接口**:
   ```json
   {
     "name": "search_api",
     "arguments": {
       "query": "HttpHandler",
       "type": "interface"
     }
   }
   ```

2. **获取接口详情**:
   ```json
   {
     "name": "get_interface",
     "arguments": {
       "name": "HttpHandler"
     }
   }
   ```

3. **查看方法签名**:
   ```json
   {
     "name": "get_method_signature",
     "arguments": {
       "interface": "HttpHandler",
       "method": "handleHttpRequestToBeSent"
     }
   }
   ```

### 场景 2：了解 Repeater 功能

**目标**: 了解 Repeater 工具的 API

**查询步骤**:

1. **列出 repeater 包下的接口**:
   ```json
   {
     "name": "list_interfaces",
     "arguments": {
       "package": "burp.api.montoya.repeater"
     }
   }
   ```

2. **获取 Repeater 接口详情**:
   ```json
   {
     "name": "get_interface",
     "arguments": {
       "name": "Repeater"
     }
   }
   ```

### 场景 3：查找特定功能的方法

**目标**: 查找如何修改 HTTP 请求体

**查询步骤**:

1. **搜索"body"相关方法**:
   ```json
   {
     "name": "search_api",
     "arguments": {
       "query": "body",
       "type": "method",
       "limit": 10
     }
   }
   ```

2. **查看 HttpRequest 的 withBody 方法**:
   ```json
   {
     "name": "get_method_signature",
     "arguments": {
       "interface": "HttpRequest",
       "method": "withBody"
     }
   }
   ```

---

## 📊 API 结构速查

### 主要包结构

```
burp.api.montoya/
├── ai/              # AI 集成
├── burpsuite/       # Burp Suite 控制
├── collaborator/    # Burp Collaborator
├── comparer/        # Comparer 工具
├── core/            # 核心类型
├── decoder/         # Decoder 工具
├── extension/       # 扩展管理
├── http/            # HTTP 功能
│   ├── handler/     # HTTP 处理器
│   ├── message/     # 请求/响应
│   └── sessions/    # 会话管理
├── intruder/        # Intruder 工具
├── logging/         # 日志
├── organizer/       # Organizer 工具
├── persistence/     # 数据持久化
├── proxy/           # Proxy 工具
├── repeater/        # Repeater 工具
├── scanner/         # Scanner 工具
├── scope/           # 范围管理
├── sitemap/         # 站点地图
├── ui/              # UI 集成
├── utilities/       # 工具函数
└── websocket/       # WebSocket 支持
```

### 核心接口

- **`MontoyaApi`**: API 入口点
- **`Http`**: HTTP 请求发送
- **`Proxy`**: 代理功能
- **`Repeater`**: Repeater 工具
- **`Scanner`**: Scanner 工具
- **`Intruder`**: Intruder 工具

---

## 📝 提示词示例

在 MCP 客户端中，你可以这样提问：

### 基础查询
```
请帮我搜索 Burp Suite API 中与 HTTP 请求相关的接口
```

### 获取详情
```
我想了解 HttpRequest 接口的所有方法
```

### 方法查询
```
HttpRequest 接口中 withBody 方法需要什么参数？
```

### 包浏览
```
burp.api.montoya.http 包下有哪些接口？
```

---

## 🔗 相关文档

- [快速上手指南](QUICKSTART.md)
- [MCP 客户端配置](MCP_CLIENT_SETUP.md)
- [故障排除指南](TROUBLESHOOTING.md)

---

## 💬 查询技巧

1. **使用模糊搜索**: 不确定具体名称时，使用 `search_api`
2. **从包开始**: 了解模块结构时，先用 `list_interfaces`
3. **深入细节**: 需要具体方法信息时，使用 `get_method_signature`
4. **查看继承**: 使用 `get_interface` 了解接口的继承关系
