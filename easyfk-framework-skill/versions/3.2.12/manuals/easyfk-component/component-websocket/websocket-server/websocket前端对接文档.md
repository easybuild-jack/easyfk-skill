# EasyFK WebSocket Server 前端对接文档

## 1. 连接信息

### 1.1 基本连接

| 项目 | 说明 |
|------|------|
| 协议 | `ws://`（未开启 SSL）或 `wss://`（开启 SSL） |
| 默认端口 | `8081`（Netty 独立端口，非应用主端口） |
| 默认路径 | `/ws`（服务端校验路径，忽略查询参数与末尾斜杠；路径不匹配返回 404 `PATH_NOT_FOUND`） |
| 完整地址示例 | `ws://192.168.1.100:8081/ws` |

### 1.2 连接参数

连接时需要传递以下参数，支持通过 **请求头** 或 **URL 查询参数** 两种方式传递：

| 参数名 | 请求头 Key | 是否必填 | 说明 |
|--------|-----------|---------|------|
| Token | `Access-Token` | 视配置 | JWT 认证令牌，可带 `Bearer ` 前缀。`mustLogin=true` 时必填 |
| 客户端ID | `Client-ID` | 鉴权时必填 | 客户端唯一标识，最长 128 字符。开启鉴权时不传返回 400 `CLIENT_ID_MISSING`；未开启鉴权且不传时服务端生成一次性随机 ID（每次连接都不同） |
| 客户端类型 | `Client-Type` | 否 | 客户端类型标识，默认 `APP`，最长 32 字符。可选值：`APP` / `PC` / `BMS` |
| 随机数 | `Request-Nonce` | 仅鉴权时 | 随机字符串，开启接口鉴权时必填，每次必须全新 |
| 时间戳 | `Timestamp` | 仅鉴权时 | 当前毫秒时间戳，与服务器时间偏差不得超过 300 秒（默认） |
| 签名 | `Reset-Sign` | 仅鉴权时 | HMAC-SHA256 签名，开启接口鉴权时必填 |

> **注意**: 同一参数同时在请求头和查询参数中出现时，请求头优先。建议始终传稳定的 `Client-ID`（每个设备/标签页一个）。

### 1.3 连接示例

#### 方式一：URL 查询参数（推荐用于浏览器环境）

```javascript
// 基础连接（无认证）
const ws = new WebSocket('ws://localhost:8081/ws?Client-ID=my-client-123&Client-Type=PC');

// 带 Token 认证
const ws = new WebSocket('ws://localhost:8081/ws?Access-Token=eyJhbGciOi...&Client-ID=my-client-123&Client-Type=PC');

// 开启鉴权时（Client-ID 必填，签名见第 5 节）
const nonce = crypto.randomUUID();
const ts = Date.now();
const sign = await generateSign('PC', 'my-client-123', nonce, ts, null, secretKey);
const qs = new URLSearchParams({ 'Client-ID': 'my-client-123', 'Client-Type': 'PC',
    'Request-Nonce': nonce, 'Timestamp': String(ts), 'Reset-Sign': sign });
const ws = new WebSocket(`ws://localhost:8081/ws?${qs}`);
```

#### 方式二：自定义请求头（需要使用支持自定义 Header 的 WebSocket 客户端库）

```javascript
// 使用支持自定义 Header 的库（如 ws 库 in Node.js）
const WebSocket = require('ws');
const ws = new WebSocket('ws://localhost:8081/ws', {
    headers: {
        'Client-ID': 'my-client-123',
        'Client-Type': 'PC',
        'Access-Token': 'eyJhbGciOi...'
    }
});
```

> **提示**: 浏览器原生 `WebSocket` API 不支持自定义请求头，建议浏览器端使用 URL 查询参数方式。

---

## 2. 连接生命周期

### 2.1 连接建立

连接成功后，服务端会自动发送一条欢迎消息：

```json
{
    "success": true,
    "message": "欢迎连接到WebSocket服务器",
    "data": null,
    "timestamp": "2026-03-01T08:00:00Z"
}
```

### 2.2 连接拒绝

如果连接被拒绝（认证失败、签名错误等），服务端返回 HTTP 错误响应：

```json
{
    "success": false,
    "code": "AUTH_TOKEN_INVALID",
    "message": "Invalid or expired access token",
    "timestamp": 1709280000000
}
```

**常见错误码**:

| 错误码 | HTTP 状态码 | 说明 |
|--------|-----------|------|
| `AUTH_TOKEN_MISSING` | 401 | Token 缺失（mustLogin=true 时） |
| `AUTH_TOKEN_INVALID` | 401 | Token 验证失败或已过期 |
| `AUTH_USER_MISSING` | 401 | mustLogin=true 时 Token 有效但取不到用户数据 |
| `TIMESTAMP_INVALID` | 401 | 开启鉴权时 `Timestamp` 缺失、非法或与服务器时间偏差超过允许值（默认300秒） |
| `SIGN_INVALID` | 401 | 接口签名验证失败 |
| `NONCE_REUSED` | 401 | nonce 在防重放窗口（默认600秒）内重复使用，每次请求必须生成全新 nonce |
| `ORIGIN_NOT_ALLOWED` | 403 | 请求的 Origin 不在服务端允许的跨域来源白名单中 |
| `PATH_NOT_FOUND` | 404 | 连接路径与服务端配置的 `path` 不一致 |
| `INVALID_REQUEST` | 400 | 无效的 HTTP 请求 |
| `CLIENT_ID_MISSING` | 400 | 开启鉴权时未传 `Client-ID` |
| `INVALID_CLIENT_ID` | 400 | `Client-ID` 超过 128 字符 |
| `INVALID_CLIENT_TYPE` | 400 | `Client-Type` 超过 32 字符 |
| `MISSING_SESSION_ID` | 500 | 会话ID生成失败（服务端认证拦截器配置问题） |
| `CONNECTION_FAILED` | 500 | 连接建立失败 |
| `HANDSHAKE_ERROR` | 500 | 握手过程异常 |
| `INTERCEPTOR_ERROR` | 500 | 服务端拦截器执行异常 |

此外，HTTP 响应头中也包含错误信息：
- `X-Error-Code`: 业务错误码
- `X-Error-Message`: 错误描述

### 2.3 连接保持（心跳）

服务端每隔 **30秒**（默认配置）向客户端发送心跳 Ping 消息：

```json
{
    "channel": "heartbeat",
    "category": null,
    "data": {
        "type": "ping",
        "timestamp": 1709280030000
    },
    "timestamp": "2026-03-01T08:00:30Z"
}
```

**前端必须响应心跳**，发送 Pong 消息保持连接活跃：

```json
{
    "eventType": "pong"
}
```

> **重要**: 如果客户端在 **30分钟**（默认 `sessionTimeoutSeconds=1800`）内未发送任何消息（包括 Pong），服务端将主动关闭连接。

### 2.4 帧类型约束

- 只接受**文本帧**，内容必须是第 3.1 节格式的 JSON 对象。无法解析的文本（非 JSON、数组、`null` 等）会收到 `{"success":false,"message":"消息格式错误：必须是符合协议的JSON对象"}`，连接保持。
- 分片发送的文本消息由服务端聚合后处理；聚合后超过 `maxFrameSize`（默认 64KB）时服务端关闭连接。
- **二进制帧不支持**：服务端发送关闭码 `1003`（reason `Binary frames are not supported`）并关闭连接。

---

## 3. 消息格式

### 3.1 客户端发送消息格式 (WsUserOptParam)

所有客户端发送的消息均为 JSON 格式：

```json
{
    "eventType": "事件类型",
    "eventData": { "key1": "value1" },
    "nonce": "随机数（开启鉴权时需要）",
    "timestamp": 1709280000000,
    "sign": "签名（开启鉴权时需要）"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `eventType` | String | 是 | 事件类型标识 |
| `eventData` | Object | 否 | 事件携带的业务数据 |
| `nonce` | String | 仅鉴权时 | 随机字符串 |
| `timestamp` | Number | 仅鉴权时 | 当前毫秒时间戳 |
| `sign` | String | 仅鉴权时 | HMAC-SHA256 签名 |

### 3.2 服务端推送消息格式 (PushMessage)

服务端主动推送的业务数据：

```json
{
    "channel": "频道名称",
    "category": "类别",
    "data": { "key1": "value1" },
    "timestamp": "2026-03-01T08:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `channel` | String | 消息频道（如 `quote`、`order`、`notification`、`heartbeat`） |
| `category` | String | 类别标识（如具体产品ID），可为 null |
| `data` | Object | 推送的业务数据 |
| `timestamp` | String | 推送时间（ISO 8601 格式） |

### 3.3 服务端事件响应格式 (ResponseMessage)

服务端对客户端操作的响应：

```json
{
    "success": true,
    "message": "事件处理成功",
    "data": null,
    "timestamp": "2026-03-01T08:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | Boolean | 操作是否成功 |
| `message` | String | 响应消息描述 |
| `data` | Object | 响应数据（可为 null） |
| `timestamp` | String | 响应时间（ISO 8601 格式） |

### 3.4 消息类型区分

前端收到消息后，可以通过消息结构区分类型：

| 消息类型 | 判断方式 | 说明 |
|---------|---------|------|
| 业务推送 | 包含 `channel` 字段 | 服务端主动推送的业务数据 |
| 心跳 Ping | `channel === "heartbeat"` | 需要回复 Pong |
| 事件响应 | 包含 `success` 字段 | 对客户端操作的处理结果 |

---

## 4. 事件类型详解

### 4.1 心跳响应 (pong)

```json
{
    "eventType": "pong"
}
```

收到心跳 Ping 后必须回复，否则会话超时后将被服务端断开。

### 4.2 检查在线状态 (online)

```json
{
    "eventType": "online"
}
```

**响应**:

```json
{
    "success": true,
    "message": "当前会话处于在线状态！",
    "timestamp": "2026-03-01T08:00:00Z"
}
```

### 4.3 登录状态变化处理

**用户身份只在连接建立（握手）时确定**，连接存续期间身份不可变更，不支持在已有连接上发送 login 事件补充认证。

- 连接时携带有效 `Access-Token` → 会话绑定用户身份，可接收用户级推送
- 连接时未携带 Token → 匿名会话，仅支持广播和频道订阅
- 会话标识（userSessionId）由 `Client-Type` + `Client-ID` + 登录用户共同决定，登录/登出重连后会得到新的会话；前端不需要也不应自行计算它

**用户在 APP 内登录或登出时，客户端必须断开当前 WebSocket 连接，并携带（或去掉）新的 Token 重新建立连接**，重连后需重新发起订阅：

```javascript
// 用户登录成功后
ws.disconnect();
ws.setToken(newJwtToken);
await ws.connect();
// 重新订阅所需频道
await ws.subscribe('quote', 'BTCUSDT');

// 用户登出后
ws.disconnect();
ws.setToken('');
await ws.connect();
```

### 4.4 订阅频道 (subscribe)

订阅特定频道+类别的消息推送：

```json
{
    "eventType": "subscribe",
    "eventData": {
        "channel": "quote",
        "category": "BTCUSDT,ETHUSDT"
    }
}
```

> `category` 支持逗号分隔的多个类别，一次请求可批量订阅。

**成功响应**:

```json
{
    "success": true,
    "message": "事件处理成功",
    "timestamp": "2026-03-01T08:00:00Z"
}
```

### 4.5 取消订阅 (unsubscribe)

```json
{
    "eventType": "unsubscribe",
    "eventData": {
        "channel": "quote",
        "category": "BTCUSDT,ETHUSDT"
    }
}
```

### 4.6 自定义业务事件

除内置事件外，前端可以发送任意自定义事件类型，由后端 `UserEventHandler` 实现处理：

```json
{
    "eventType": "placeOrder",
    "eventData": {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "quantity": "0.1",
        "price": "50000"
    }
}
```

---

## 5. 接口鉴权（可选）

当服务端开启 `enableSecurity=true` 时，客户端在连接和发送非心跳消息时都需要携带签名。

### 5.1 签名算法

使用 **HMAC-SHA256** 算法。

#### 连接阶段签名

```
签名原文 = "ClientType={clientType}&ClientId={clientId}&Nonce={nonce}&Timestamp={timestamp}&Param="
签名结果 = HMAC-SHA256(签名原文, secretKey)  → 转十六进制（服务端大小写不敏感）
```

连接阶段 `Param` 为空字符串；`timestamp` 与查询参数/请求头 `Timestamp` 相同（毫秒十进制字符串）；`clientId` 必须是传入的 `Client-ID`。

#### 消息阶段签名

```
签名原文 = "ClientType={clientType}&ClientId={clientId}&Nonce={nonce}&Timestamp={timestamp}&Param={sortedEventDataJson}"
签名结果 = HMAC-SHA256(签名原文, secretKey)  → 转十六进制
```

`sortedEventDataJson` 是将 `eventData` 的**顶层** key 按 **ASCII 码升序排序** 后序列化为 JSON 字符串，eventData 为空时为空串；`timestamp` 与消息 JSON 中的 `timestamp` 字段相同。

#### 校验规则

1. 时间戳：`|服务器时间 - timestamp|` 不得超过 300 秒（服务端 `security-timestamp-tolerance-seconds`），客户端需保持时钟同步。
2. 签名：服务端以常量时间比较。
3. nonce：签名通过后登记，有效窗口内（默认 600 秒，至少为时间戳偏差的 2 倍）同一 nonce 只能使用一次。

> **安全提示**：浏览器端签名必须把 `secretKey` 下发到前端，任何人都能从页面取出，签名只能防止随意伪造和重放，不能代替 `Access-Token` 做身份认证。

### 5.2 签名示例

#### JavaScript 签名生成

```javascript
async function generateSign(clientType, clientId, nonce, timestamp, eventData, secretKey) {
    // 1. 处理 eventData：按 key 的 ASCII 码排序后序列化
    let param = '';
    if (eventData && Object.keys(eventData).length > 0) {
        const sortedKeys = Object.keys(eventData).sort();
        const sortedObj = {};
        sortedKeys.forEach(key => { sortedObj[key] = eventData[key]; });
        param = JSON.stringify(sortedObj);
    }

    // 2. 构建签名原文
    const signData = `ClientType=${clientType || ''}&ClientId=${clientId || ''}&Nonce=${nonce || ''}`
        + `&Timestamp=${timestamp}&Param=${param}`;

    // 3. HMAC-SHA256 签名
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
        'raw', encoder.encode(secretKey),
        { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
    );
    const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(signData));

    // 4. 转十六进制
    return Array.from(new Uint8Array(signature))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

// 使用示例 - 连接阶段
const nonce = crypto.randomUUID();
const ts = Date.now();
const sign = await generateSign('PC', 'my-client-123', nonce, ts, null, 'your-secret-key');
// 连接参数：Request-Nonce=nonce、Timestamp=ts、Reset-Sign=sign

// 使用示例 - 消息阶段
const eventData = { channel: 'quote', category: 'BTCUSDT' };
const msgNonce = crypto.randomUUID();
const msgTs = Date.now();
const msgSign = await generateSign('PC', 'my-client-123', msgNonce, msgTs, eventData, 'your-secret-key');
ws.send(JSON.stringify({ eventType: 'subscribe', eventData, nonce: msgNonce, timestamp: msgTs, sign: msgSign }));
```

#### 签名验证排查

如果签名验证失败，请检查：
1. `clientType` 和 `clientId` 与连接时传入的一致（开启鉴权时必须传 `Client-ID`）
2. `eventData` 按顶层 key 的 ASCII 码排序后序列化（`a` < `b` < `c`）
3. `nonce` 每次请求使用不同的值
4. 签名原文中的 `Timestamp` 与实际发送的时间戳一致，且客户端时钟与服务器偏差不超过 300 秒
5. `secretKey` 与服务端配置的 `securitySecret` 一致
6. 签名结果为十六进制字符串

---

## 6. 完整前端对接示例

### 6.1 基础版（浏览器原生 WebSocket）

```javascript
class EasyFKWebSocket {
    constructor(url, options = {}) {
        this.url = url;
        this.token = options.token || '';
        this.clientId = options.clientId || this._generateClientId();
        this.clientType = options.clientType || 'PC';
        this.secretKey = options.secretKey || '';
        this.enableSecurity = options.enableSecurity || false;
        this.onMessage = options.onMessage || (() => {});
        this.onConnect = options.onConnect || (() => {});
        this.onDisconnect = options.onDisconnect || (() => {});
        this.onError = options.onError || (() => {});
        this.reconnectInterval = options.reconnectInterval || 3000;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
        
        this._ws = null;
        this._reconnectAttempts = 0;
        this._reconnectTimer = null;
        this._messageHandlers = new Map();
    }

    // ==================== 连接管理 ====================

    async connect() {
        const params = new URLSearchParams();
        params.set('Client-ID', this.clientId);
        params.set('Client-Type', this.clientType);

        if (this.token) {
            params.set('Access-Token', this.token);
        }

        if (this.enableSecurity) {
            const nonce = this._generateNonce();
            const ts = Date.now();
            const sign = await this._generateSign(nonce, ts, null);
            params.set('Request-Nonce', nonce);
            params.set('Timestamp', String(ts));
            params.set('Reset-Sign', sign);
        }

        const connectUrl = `${this.url}?${params.toString()}`;
        this._ws = new WebSocket(connectUrl);
        this._bindEvents();
    }

    disconnect() {
        this._clearReconnectTimer();
        if (this._ws) {
            this._ws.close();
            this._ws = null;
        }
    }

    _bindEvents() {
        this._ws.onopen = () => {
            console.log('[WS] 连接已建立');
            this._reconnectAttempts = 0;
            this.onConnect();
        };

        this._ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                this._handleMessage(msg);
            } catch (e) {
                console.warn('[WS] 消息解析失败:', event.data);
            }
        };

        this._ws.onclose = (event) => {
            console.log('[WS] 连接已关闭:', event.code, event.reason);
            this.onDisconnect(event);
            // 1003：发送了不支持的二进制帧，属于客户端编码错误，重连无意义
            if (event.code !== 1003) {
                this._tryReconnect();
            }
        };

        this._ws.onerror = (error) => {
            console.error('[WS] 连接错误:', error);
            this.onError(error);
        };
    }

    _handleMessage(msg) {
        // 1. 心跳 Ping → 自动回复 Pong
        if (msg.channel === 'heartbeat' && msg.data?.type === 'ping') {
            this._sendPong();
            return;
        }

        // 2. 事件响应（包含 success 字段）
        if (msg.success !== undefined) {
            console.log('[WS] 事件响应:', msg.message, msg.success ? '成功' : '失败');
            // 触发响应回调
            this._messageHandlers.forEach((handler, key) => {
                if (key === '__response__') handler(msg);
            });
            return;
        }

        // 3. 业务推送（包含 channel 字段）
        if (msg.channel) {
            const handlerKey = msg.category ? `${msg.channel}:${msg.category}` : msg.channel;
            
            // 触发精确匹配的处理器
            if (this._messageHandlers.has(handlerKey)) {
                this._messageHandlers.get(handlerKey)(msg);
            }
            // 触发频道级别的处理器
            if (msg.category && this._messageHandlers.has(msg.channel)) {
                this._messageHandlers.get(msg.channel)(msg);
            }
        }

        // 4. 通用回调
        this.onMessage(msg);
    }

    // ==================== 消息发送 ====================

    async send(eventType, eventData = null) {
        if (!this._ws || this._ws.readyState !== WebSocket.OPEN) {
            console.warn('[WS] 连接未就绪，无法发送消息');
            return;
        }

        const msg = { eventType };

        if (eventData) {
            msg.eventData = eventData;
        }

        // 鉴权签名
        if (this.enableSecurity && eventType !== 'pong' && eventType !== 'online') {
            const nonce = this._generateNonce();
            const ts = Date.now();
            const sign = await this._generateSign(nonce, ts, eventData);
            msg.nonce = nonce;
            msg.timestamp = ts;
            msg.sign = sign;
        }

        this._ws.send(JSON.stringify(msg));
    }

    // ==================== 业务操作 ====================

    /** 更新Token（登录/登出后调用，随后需 disconnect + connect 重建连接） */
    setToken(jwtToken) {
        this.token = jwtToken || '';
    }

    /** 订阅频道（支持逗号分隔多个类别） */
    async subscribe(channel, category) {
        await this.send('subscribe', { channel, category });
    }

    /** 取消订阅 */
    async unsubscribe(channel, category) {
        await this.send('unsubscribe', { channel, category });
    }

    /** 检查在线状态 */
    async checkOnline() {
        await this.send('online');
    }

    // ==================== 消息监听 ====================

    /** 注册频道+类别消息处理器 */
    on(channel, category, handler) {
        if (typeof category === 'function') {
            handler = category;
            category = null;
        }
        const key = category ? `${channel}:${category}` : channel;
        this._messageHandlers.set(key, handler);
    }

    /** 注册事件响应处理器 */
    onResponse(handler) {
        this._messageHandlers.set('__response__', handler);
    }

    /** 移除消息处理器 */
    off(channel, category) {
        const key = category ? `${channel}:${category}` : channel;
        this._messageHandlers.delete(key);
    }

    // ==================== 内部方法 ====================

    _sendPong() {
        if (this._ws && this._ws.readyState === WebSocket.OPEN) {
            this._ws.send(JSON.stringify({ eventType: 'pong' }));
        }
    }

    _tryReconnect() {
        if (this._reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[WS] 超过最大重连次数，停止重连');
            return;
        }
        this._reconnectAttempts++;
        const delay = Math.min(this.reconnectInterval * this._reconnectAttempts, 30000);
        console.log(`[WS] ${delay}ms 后尝试第 ${this._reconnectAttempts} 次重连`);
        this._reconnectTimer = setTimeout(() => this.connect(), delay);
    }

    _clearReconnectTimer() {
        if (this._reconnectTimer) {
            clearTimeout(this._reconnectTimer);
            this._reconnectTimer = null;
        }
    }

    _generateClientId() {
        return 'client-' + Date.now() + '-' + Math.random().toString(36).substring(2, 10);
    }

    _generateNonce() {
        return crypto.randomUUID ? crypto.randomUUID() : Date.now() + '-' + Math.random().toString(36).substring(2, 15);
    }

    async _generateSign(nonce, timestamp, eventData) {
        let param = '';
        if (eventData && Object.keys(eventData).length > 0) {
            const sortedKeys = Object.keys(eventData).sort();
            const sortedObj = {};
            sortedKeys.forEach(key => { sortedObj[key] = eventData[key]; });
            param = JSON.stringify(sortedObj);
        }

        const signData = `ClientType=${this.clientType || ''}&ClientId=${this.clientId || ''}&Nonce=${nonce || ''}`
            + `&Timestamp=${timestamp}&Param=${param}`;

        const encoder = new TextEncoder();
        const key = await crypto.subtle.importKey(
            'raw', encoder.encode(this.secretKey),
            { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
        );
        const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(signData));
        return Array.from(new Uint8Array(signature))
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    }
}
```

### 6.2 使用示例

```javascript
// 1. 创建连接
const ws = new EasyFKWebSocket('ws://localhost:8081/ws', {
    clientId: 'browser-001',
    clientType: 'PC',
    token: 'eyJhbGciOi...',        // 可选：JWT Token
    enableSecurity: false,           // 是否启用签名鉴权
    secretKey: 'your-secret-key',    // 鉴权密钥

    onConnect: () => {
        console.log('WebSocket 已连接');

        // 连接成功后订阅频道
        ws.subscribe('quote', 'BTCUSDT,ETHUSDT');
        ws.subscribe('order', 'fill');
    },

    onDisconnect: (event) => {
        console.log('WebSocket 断开:', event.code);
    },

    onMessage: (msg) => {
        console.log('收到消息:', msg);
    }
});

// 2. 注册消息处理器
ws.on('quote', 'BTCUSDT', (msg) => {
    console.log('BTC 报价更新:', msg.data);
    // { channel: "quote", category: "BTCUSDT", data: { price: "50000.00" }, timestamp: "..." }
});

ws.on('quote', 'ETHUSDT', (msg) => {
    console.log('ETH 报价更新:', msg.data);
});

ws.on('order', (msg) => {
    console.log('订单消息:', msg.data);
});

ws.on('notification', (msg) => {
    console.log('系统通知:', msg.data);
    // { channel: "notification", data: { title: "...", content: "...", level: "normal" }, ... }
});

ws.onResponse((msg) => {
    if (!msg.success) {
        console.error('操作失败:', msg.message);
    }
});

// 3. 建立连接
ws.connect();

// 4. 后续操作
// 用户登录后：更新Token并重建连接（重连后需重新订阅）
ws.disconnect();
ws.setToken('new-jwt-token');
ws.connect();

// 取消订阅
ws.unsubscribe('quote', 'ETHUSDT');

// 发送自定义事件
ws.send('placeOrder', {
    symbol: 'BTCUSDT',
    side: 'BUY',
    quantity: '0.1',
    price: '50000'
});

// 检查在线状态
ws.checkOnline();

// 断开连接
// ws.disconnect();
```

### 6.3 Vue 3 集成示例

```javascript
// composables/useWebSocket.js
import { ref, onMounted, onUnmounted } from 'vue';

export function useWebSocket(url, options = {}) {
    const connected = ref(false);
    const lastMessage = ref(null);
    let wsInstance = null;

    function connect() {
        wsInstance = new EasyFKWebSocket(url, {
            ...options,
            onConnect: () => {
                connected.value = true;
                options.onConnect?.();
            },
            onDisconnect: (event) => {
                connected.value = false;
                options.onDisconnect?.(event);
            },
            onMessage: (msg) => {
                lastMessage.value = msg;
                options.onMessage?.(msg);
            }
        });
        wsInstance.connect();
    }

    function disconnect() {
        wsInstance?.disconnect();
        connected.value = false;
    }

    function subscribe(channel, category) {
        wsInstance?.subscribe(channel, category);
    }

    function unsubscribe(channel, category) {
        wsInstance?.unsubscribe(channel, category);
    }

    function send(eventType, eventData) {
        wsInstance?.send(eventType, eventData);
    }

    function on(channel, category, handler) {
        wsInstance?.on(channel, category, handler);
    }

    onMounted(() => connect());
    onUnmounted(() => disconnect());

    return { connected, lastMessage, subscribe, unsubscribe, send, on, disconnect };
}
```

```vue
<!-- components/QuotePanel.vue -->
<template>
  <div>
    <p>连接状态: {{ connected ? '已连接' : '未连接' }}</p>
    <p>BTC 价格: {{ btcPrice }}</p>
    <p>ETH 价格: {{ ethPrice }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useWebSocket } from '@/composables/useWebSocket';

const btcPrice = ref('-');
const ethPrice = ref('-');

const { connected, subscribe, on } = useWebSocket('ws://localhost:8081/ws', {
    clientId: 'vue-app-001',
    clientType: 'PC',
    onConnect: () => {
        subscribe('quote', 'BTCUSDT,ETHUSDT');

        on('quote', 'BTCUSDT', (msg) => {
            btcPrice.value = msg.data.price;
        });
        on('quote', 'ETHUSDT', (msg) => {
            ethPrice.value = msg.data.price;
        });
    }
});
</script>
```

### 6.4 React 集成示例

```javascript
// hooks/useWebSocket.js
import { useRef, useState, useEffect, useCallback } from 'react';

export function useWebSocket(url, options = {}) {
    const [connected, setConnected] = useState(false);
    const wsRef = useRef(null);

    useEffect(() => {
        const ws = new EasyFKWebSocket(url, {
            ...options,
            onConnect: () => {
                setConnected(true);
                options.onConnect?.();
            },
            onDisconnect: () => {
                setConnected(false);
            }
        });
        ws.connect();
        wsRef.current = ws;

        return () => ws.disconnect();
    }, [url]);

    const subscribe = useCallback((channel, category) => {
        wsRef.current?.subscribe(channel, category);
    }, []);

    const unsubscribe = useCallback((channel, category) => {
        wsRef.current?.unsubscribe(channel, category);
    }, []);

    const send = useCallback((eventType, eventData) => {
        wsRef.current?.send(eventType, eventData);
    }, []);

    const on = useCallback((channel, category, handler) => {
        wsRef.current?.on(channel, category, handler);
    }, []);

    return { connected, subscribe, unsubscribe, send, on };
}
```

---

## 7. 服务端推送消息示例

以下为前端可能收到的各类推送消息格式示例：

### 7.1 行情报价推送

```json
{
    "channel": "quote",
    "category": "BTCUSDT",
    "data": {
        "symbol": "BTCUSDT",
        "price": "50000.00",
        "volume": "1234.56",
        "change24h": "+2.35%"
    },
    "timestamp": "2026-03-01T08:00:00Z"
}
```

### 7.2 订单状态推送

```json
{
    "channel": "order",
    "category": "fill",
    "data": {
        "orderId": "ORD-20260301-001",
        "symbol": "BTCUSDT",
        "side": "BUY",
        "status": "FILLED",
        "filledQty": "0.1",
        "filledPrice": "50000.00"
    },
    "timestamp": "2026-03-01T08:01:00Z"
}
```

### 7.3 系统通知推送

```json
{
    "channel": "notification",
    "category": null,
    "data": {
        "title": "系统维护通知",
        "content": "系统将于今晚 22:00-23:00 进行维护升级",
        "level": "important",
        "levelDescription": "重要"
    },
    "timestamp": "2026-03-01T08:02:00Z"
}
```

### 7.4 心跳 Ping 消息

```json
{
    "channel": "heartbeat",
    "category": null,
    "data": {
        "type": "ping",
        "timestamp": 1709280030000
    },
    "timestamp": "2026-03-01T08:00:30Z"
}
```

---

## 8. 常见问题

### Q1: 浏览器原生 WebSocket 不支持自定义请求头怎么办？

使用 URL 查询参数方式传递认证信息：
```javascript
new WebSocket('ws://host:8081/ws?Access-Token=xxx&Client-ID=xxx&Client-Type=PC');
```

### Q2: 连接后如何判断连接是否建立成功？

连接成功后会收到欢迎消息（`success=true, message="欢迎连接到WebSocket服务器"`）。如果连接被拒绝，`onerror` 或 `onclose` 事件会触发。

### Q3: 断线后如何重连？

建议在 `onclose` 事件中实现指数退避重连策略。上方示例代码已内置自动重连逻辑，重连间隔递增，最大30秒，最多重试10次。

### Q4: 如何区分推送消息和操作响应？

- **推送消息**: 包含 `channel` 字段，无 `success` 字段
- **操作响应**: 包含 `success` 字段，无 `channel` 字段

### Q5: 订阅多个类别需要发多次请求吗？

不需要。`category` 支持逗号分隔的多个值，一次订阅请求可同时订阅多个类别：
```json
{ "eventType": "subscribe", "eventData": { "channel": "quote", "category": "BTCUSDT,ETHUSDT,SOLUSDT" } }
```

### Q6: 匿名连接（不传 Token）可以使用吗？

可以，前提是服务端配置 `mustLogin=false`（默认值）。匿名连接可以接收广播消息和订阅频道，但无法使用用户级别的推送功能。用户身份只在连接建立时确定，登录后需携带 Token 断开重连才能绑定用户身份。

### Q7: 一个用户多端登录会互相影响吗？

不会。会话由 `clientType` + `clientId` + 登录用户共同标识。同一用户在 APP、PC、BMS 端可同时在线，各自独立管理连接和订阅；通过 `userId` 推送的消息会同时发送到该用户的所有在线设备。

只有**同一用户（或同为匿名）**使用相同 `Client-Type` + `Client-ID` 重新连接时，才会替换旧连接（旧连接被服务端关闭）。其他用户或匿名连接即使使用相同的 `Client-ID`，也会得到不同的会话，无法顶替已登录会话。

### Q7.1: 为什么连接被关闭码 1003 断开？

客户端发送了二进制帧。服务端只接受 JSON 文本帧，请用 `ws.send(JSON.stringify(...))` 发送。

### Q8: 开启鉴权后，心跳 Pong 也需要签名吗？

不需要。`pong` 和 `online` 事件无需签名，仅业务事件（如 `subscribe`、`unsubscribe`、自定义事件等）需要签名。

### Q9: 签名验证失败常见原因？

1. `clientType` 和 `clientId` 与连接时传入的不一致
2. `eventData` 未按 key 的 ASCII 码排序
3. `secretKey` 与服务端配置不一致
4. `nonce` 为空或重复使用
5. `timestamp` 缺失、未参与签名，或客户端时钟偏差超过 300 秒（握手返回 `TIMESTAMP_INVALID`，消息返回“签名验证失败：时间戳缺失或已过期”）
6. 签名结果未转为十六进制字符串

### Q10: WebSocket 端口与应用主端口的关系？

WebSocket 使用 Netty 独立端口（默认 `8081`），与 Spring Boot 应用主端口（如 `8080`）相互独立。前端连接时请使用 WebSocket 端口。
