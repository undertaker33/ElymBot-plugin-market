# 03 — Host API 参考

`bootstrap(hostApi)` 的 `hostApi` 对象提供以下方法。

---

## 注册方法

### `registerCommandHandler(descriptor)`

注册一个斜杠命令。详见 [04-处理器与钩子](04-处理器与钩子.md#命令处理器)。

### `registerMessageHandler(descriptor)`

注册一个通用消息处理器，在命令匹配前触发。详见 [04-处理器与钩子](04-处理器与钩子.md#消息处理器)。

### `registerRegexHandler(descriptor)`

注册一个正则匹配处理器。详见 [04-处理器与钩子](04-处理器与钩子.md#正则处理器)。

### `registerLlmHook(descriptor)`

注册一个 LLM 流水线钩子。详见 [04-处理器与钩子](04-处理器与钩子.md#llm-钩子)。

### `registerLifecycleHandler(descriptor)`

注册生命周期钩子，支持 `hook` 值：
- `"on_plugin_loaded"`
- `"on_plugin_unloaded"`
- `"on_plugin_error"`

### `registerTool(descriptor, handler)`

注册一个 LLM Function Calling 工具（Phase 5）。

### `registerToolLifecycleHook(descriptor)`

注册工具生命周期钩子（Phase 5）。

---

## 快捷方法

| 方法 | 等价于 |
|------|--------|
| `onPluginLoaded(descriptor)` | `registerLifecycleHandler({ hook: "on_plugin_loaded", ...descriptor })` |
| `onPluginUnloaded(descriptor)` | `registerLifecycleHandler({ hook: "on_plugin_unloaded", ...descriptor })` |
| `onPluginError(descriptor)` | `registerLifecycleHandler({ hook: "on_plugin_error", ...descriptor })` |

---

## 工具方法

### `log(level, message, metadata?)`

写入宿主日志。

```javascript
hostApi.log("INFO",  "普通信息");
hostApi.log("WARN",  "警告");
hostApi.log("ERROR", "出错了", { detail: "..." });
```

`level` 可选值：`"VERBOSE"` / `"DEBUG"` / `"INFO"` / `"WARN"` / `"ERROR"`

### `getPluginMetadata()`

返回当前插件的元数据对象：

```javascript
const meta = hostApi.getPluginMetadata();
// meta.pluginId            — 插件 ID（来自 manifest.json）
// meta.installedVersion    — 安装版本
// meta.runtimeKind         — "js_quickjs"
// meta.runtimeApiVersion   — 1
// meta.runtimeBootstrap    — "runtime/bootstrap.js"
```

### `getSettings()` / `readSettings()` / `getPluginSettings()` / `getConfig()`

这四个方法等价，返回当前已保存的配置值（对应 `_conf_schema.json` 中定义的键）。

```javascript
const settings = hostApi.getSettings() || {};
const prefix = settings.greeting_prefix ?? "默认值";
```

> **注意**：首次运行时用户可能尚未保存配置，返回值可能为空对象 `{}`。务必提供默认值。

---

## 事件级 API（非 hostApi 上的方法）

以下 API 不在 `hostApi` 上，而是通过钩子 payload 中的对象暴露。

### `view.sendFollowup(text, attachments)` — 补发消息

在 `after_message_sent` 钩子的 `view` 对象上可用。用于在主消息发送后，再额外发送一条消息（如图片、补充内容）。

```javascript
hostApi.registerLlmHook({
  hook: "after_message_sent",
  key: "my-plugin.followup",
  priority: 100,
  metadata: {},
  handler(payload) {
    const { event, view } = payload;

    // 先检查是否支持补发
    if (!view.canSendFollowup || typeof view.sendFollowup !== "function") {
      return;
    }

    // 发送补发消息
    const result = view.sendFollowup("这是补发的文本", [
      { uri: "assets/extra.png", mimeType: "image/png" },
    ]);

    // result: { success: boolean, receiptIds: string[], errorSummary: string }
  },
});
```

**参数：**
- `text` (string) — 补发消息的文本内容，可为空字符串
- `attachments` (array) — 附件数组，每个元素为 `{ uri, mimeType? }`，格式与命令回复的附件一致

**返回值：**
- `{ success, receiptIds, errorSummary }` — 与主消息的发送结果格式相同

**注意事项：**
- `view.canSendFollowup` 为 `true` 时才可调用（在应用内聊天等无外部平台的场景下为 `false`）
- QQ 平台下可用，补发消息会通过 OneBot WebSocket 原路送出
- 附件的 `uri` 支持相对路径（自动解析到插件根目录）、绝对路径、`http(s)://` 等