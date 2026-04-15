# ElymBot Plugin v2 — Agent Development Guide

> **Audience**: AI coding agents (Copilot, Cursor, Claude, etc.)
> **Goal**: Enable an agent to develop a fully functional ElymBot plugin from scratch,
> without access to the host application source code.
> **Host version**: ≥ 0.4.0 · **Protocol**: v2 · **Runtime**: QuickJS (ES Module)

---

## TABLE OF CONTENTS

1. [ARCHITECTURE OVERVIEW](#1-architecture-overview)
2. [FILE STRUCTURE (MANDATORY)](#2-file-structure)
3. [manifest.json SPEC](#3-manifestjson)
4. [android-plugin.json SPEC](#4-android-pluginjson)
5. [BOOTSTRAP ENTRY POINT](#5-bootstrap-entry-point)
6. [hostApi REFERENCE](#6-hostapi-reference)
7. [HANDLER & HOOK REGISTRATION](#7-handler--hook-registration)
8. [EVENT OBJECT SHAPES](#8-event-object-shapes)
9. [LLM PIPELINE HOOKS](#9-llm-pipeline-hooks)
10. [CONFIGURATION SYSTEM](#10-configuration-system)
11. [ATTACHMENTS & ASSETS](#11-attachments--assets)
12. [COMPLETE EXAMPLES](#12-complete-examples)
13. [COMMON PITFALLS](#13-common-pitfalls)
14. [CHECKLIST BEFORE DELIVERY](#14-checklist)

---

## 1. ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────┐
│  ElymBot Host App (Android / Kotlin)            │
│                                                 │
│  ┌──────────────┐   ┌────────────────────────┐  │
│  │ Plugin Loader │──▶│ QuickJS Engine          │  │
│  │              │   │  (ES Module sandbox)    │  │
│  │  reads:      │   │  ┌──────────────────┐   │  │
│  │  manifest    │   │  │ bootstrap.js      │   │  │
│  │  android-    │   │  │  export default   │   │  │
│  │  plugin.json │   │  │  async function   │   │  │
│  │  _conf_      │   │  │  bootstrap(       │   │  │
│  │  schema.json │   │  │    hostApi) {...}  │   │  │
│  │  settings-   │   │  └──────────────────┘   │  │
│  │  schema.json │   └────────────────────────┘  │
│  └──────────────┘                               │
│                                                 │
│  Platforms: QQ (OneBot), App-internal chat       │
└─────────────────────────────────────────────────┘
```

**Key facts:**
- Plugins run inside a QuickJS sandbox — **no Node.js APIs** (no `fs`, `path`, `require`, `process`).
- Only ES module imports from files **within** the `runtime/` directory tree are allowed.
- All interaction with the host goes through the `hostApi` object passed to `bootstrap()`.
- The plugin is **event-driven**: you register handlers/hooks, then the host calls them.
- Plugin code is **synchronous** within a single QuickJS thread. Hooks run sequentially by priority.

---

## 2. FILE STRUCTURE

```
my-plugin/                     ← plugin root directory
├── manifest.json              ← REQUIRED: identity & metadata
├── android-plugin.json        ← REQUIRED: runtime & config contract
├── _conf_schema.json          ← OPTIONAL: config field definitions
├── runtime/
│   ├── bootstrap.js           ← REQUIRED: entry point
│   └── *.js                   ← OPTIONAL: additional ES modules
├── schemas/
│   └── settings-schema.json   ← OPTIONAL: settings UI definition
└── assets/                    ← OPTIONAL: images, audio, etc.
    └── ...
```

**Rules:**
- `manifest.json` and `android-plugin.json` MUST be at the plugin root.
- `runtime/bootstrap.js` is the default entry file (configurable in android-plugin.json).
- All JS files use ES module syntax (`import`/`export`), NOT CommonJS.
- Asset paths in code are relative to the plugin root (NOT relative to `runtime/`).

---

## 3. manifest.json

Every field documented. Copy-paste and fill in your values.

```json
{
  "pluginId": "com.yourname.plugin-name",
  "version": "1.0.0",
  "protocolVersion": 2,
  "author": "Your Name",
  "title": "Plugin Display Name",
  "description": "One-line description of the plugin",
  "permissions": [],
  "minHostVersion": "0.4.0",
  "maxHostVersion": "",
  "sourceType": "GIT",
  "sourceUrl": "https://github.com/yourname/plugin-repo.git",
  "entrySummary": "Brief summary of capabilities",
  "riskLevel": "LOW"
}
```

| Field | Type | Req | Constraint |
|-------|------|-----|------------|
| `pluginId` | string | ✅ | Globally unique. Use reverse-domain: `com.author.name` |
| `version` | string | ✅ | Semantic versioning `X.Y.Z` |
| `protocolVersion` | number | ✅ | **Must be `2`**. v1 is deprecated. |
| `author` | string | ✅ | Author display name |
| `title` | string | ✅ | UI display name |
| `description` | string | ✅ | Short description |
| `permissions` | string[] | ✅ | Currently unused, set `[]` |
| `minHostVersion` | string | ✅ | Minimum host version, e.g. `"0.4.0"` |
| `maxHostVersion` | string | ❌ | Empty string = no upper bound |
| `sourceType` | string | ❌ | `"GIT"` or `"LOCAL_FILE"` |
| `sourceUrl` | string | ❌ | Git repo URL when sourceType is GIT |
| `entrySummary` | string | ❌ | Capability summary |
| `riskLevel` | string | ❌ | `"LOW"` / `"MEDIUM"` / `"HIGH"` |


---

## 4. android-plugin.json

```json
{
  "protocolVersion": 2,
  "runtime": {
    "kind": "js_quickjs",
    "bootstrap": "runtime/bootstrap.js",
    "apiVersion": 1
  },
  "config": {
    "staticSchema": "_conf_schema.json",
    "settingsSchema": "schemas/settings-schema.json"
  }
}
```

| Field | Value | Note |
|-------|-------|------|
| `protocolVersion` | `2` | Fixed |
| `runtime.kind` | `"js_quickjs"` | Fixed. Only QuickJS is supported. |
| `runtime.bootstrap` | `"runtime/bootstrap.js"` | Relative to plugin root |
| `runtime.apiVersion` | `1` | Current API version |
| `config.staticSchema` | `"_conf_schema.json"` | Empty string `""` if no config |
| `config.settingsSchema` | `"schemas/settings-schema.json"` | Empty string `""` if no settings UI |

---

## 5. BOOTSTRAP ENTRY POINT

The entry file **MUST** export a default async function named `bootstrap`:

```javascript
export default async function bootstrap(hostApi) {
  // All registration happens here.
  // hostApi is the ONLY interface to the host.
  
  hostApi.registerCommandHandler({ ... });
  hostApi.registerLlmHook({ ... });
  // etc.
}
```

**Hard requirements:**
1. `export default` — must be a default export
2. `async function` — must be async
3. Function name must be `bootstrap`
4. Single parameter: `hostApi`
5. All handler registration must happen during this call (not deferred/async-later)

**Module imports** — only from sibling files:
```javascript
import { myHelper } from "./utils.js";  // OK — relative to runtime/
import { foo } from "./sub/bar.js";     // OK — subdirectory
// import fs from "fs";                 // FORBIDDEN — no Node.js
// const x = require("./x");            // FORBIDDEN — no CommonJS
```

---

## 6. hostApi REFERENCE

All methods available on the `hostApi` object:

### Registration Methods

| Method | Purpose |
|--------|---------|
| `registerCommandHandler(descriptor)` | Register a slash command (e.g., `/hello`) |
| `registerMessageHandler(descriptor)` | Register a pre-command message observer |
| `registerRegexHandler(descriptor)` | Register a regex pattern matcher |
| `registerLlmHook(descriptor)` | Register an LLM pipeline hook |
| `registerLifecycleHandler(descriptor)` | Register lifecycle hook |
| `registerTool(descriptor, handler)` | Register LLM function-calling tool |
| `registerToolLifecycleHook(descriptor)` | Register tool lifecycle hook |

### Lifecycle Shortcuts

| Method | Equivalent |
|--------|-----------|
| `onPluginLoaded(d)` | `registerLifecycleHandler({ hook: "on_plugin_loaded", ...d })` |
| `onPluginUnloaded(d)` | `registerLifecycleHandler({ hook: "on_plugin_unloaded", ...d })` |
| `onPluginError(d)` | `registerLifecycleHandler({ hook: "on_plugin_error", ...d })` |

### Utility Methods

#### `log(level, message, metadata?)`
```javascript
hostApi.log("INFO", "Hello");
hostApi.log("ERROR", "Oops", { detail: "stack..." });
// level: "VERBOSE" | "DEBUG" | "INFO" | "WARN" | "ERROR"
```

#### `getPluginMetadata()` → object
```javascript
const meta = hostApi.getPluginMetadata();
// { pluginId, installedVersion, runtimeKind, runtimeApiVersion, runtimeBootstrap }
```

#### `getSettings()` → object
```javascript
const settings = hostApi.getSettings() || {};
const val = settings.my_key ?? "default";
```
Returns saved config values from `_conf_schema.json`. Returns `{}` if nothing saved yet.
**Always provide defaults with `??` or `||`.**

Aliases: `readSettings()`, `getPluginSettings()`, `getConfig()` — all identical.

---

## 7. HANDLER & HOOK REGISTRATION

Every registration descriptor shares a common base:

```javascript
{
  key: "pluginId.unique-key",  // REQUIRED: globally unique registration key
  priority: 0,                 // OPTIONAL: lower = runs first. Default 0. Range: 0-200
  filters: [],                 // OPTIONAL: leave empty
  metadata: {},                // OPTIONAL: arbitrary key-value metadata
  handler(event) { ... },      // REQUIRED: the callback function
}
```

### 7.1 Command Handler

```javascript
hostApi.registerCommandHandler({
  key: "my-plugin.greet",
  command: "hello",            // user types /hello
  aliases: ["hi", "greet"],    // also triggers on /hi, /greet
  groupPath: [],               // leave empty for top-level commands
  priority: 0,
  filters: [],
  metadata: { description: "Say hello" },
  handler(event) {
    const name = event.remainingText || "World";
    event.replyResult({
      text: `Hello, ${name}!`,
      attachments: [],         // optional
    });
  },
});
```

### 7.2 Message Handler

Fires **before** command matching. Good for logging or preprocessing.

```javascript
hostApi.registerMessageHandler({
  key: "my-plugin.logger",
  priority: 0,
  filters: [],
  metadata: {},
  handler(event) {
    hostApi.log("INFO", `Message: ${event.rawText}`);
    // event.stopPropagation() — blocks subsequent handlers + command matching
  },
});
```

### 7.3 Regex Handler

```javascript
hostApi.registerRegexHandler({
  key: "my-plugin.pattern",
  pattern: "^echo[：:]\\s*(.+)",   // regex STRING, not RegExp object
  flags: "i",                      // regex flags as string
  priority: 0,
  filters: [],
  metadata: {},
  handler(event) {
    const captured = event.groups[0]; // first capture group
    hostApi.log("INFO", `Matched: ${captured}`);
    event.stopPropagation();
  },
});
```

### 7.4 Lifecycle Handlers

```javascript
hostApi.onPluginLoaded({
  key: "my-plugin.loaded",
  handler() { hostApi.log("INFO", "Plugin loaded"); },
});

hostApi.onPluginUnloaded({
  key: "my-plugin.unloaded",
  handler() { hostApi.log("INFO", "Plugin unloaded"); },
});

hostApi.onPluginError({
  key: "my-plugin.error",
  handler(payload) { hostApi.log("ERROR", "Error", payload || {}); },
});
```

---

## 8. EVENT OBJECT SHAPES

### 8.1 Command Event (handler of registerCommandHandler)

```typescript
interface CommandEvent {
  // Common fields (shared with all event types)
  eventId: string;                  // unique event ID
  platformAdapterType: string;      // e.g., "qq", "app_chat"
  messageType: string;              // message type identifier
  conversationId: string;           // conversation/group ID
  senderId: string;                 // sender user ID
  timestampEpochMillis: number;     // epoch milliseconds
  rawText: string;                  // original message text
  workingText: string;              // preprocessed text
  normalizedMentions: string[];     // @mention list
  extras: object;                   // platform-specific extras
  stage: "Command";                 // always "Command"
  
  // Command-specific fields
  commandPath: string[];            // matched command path
  args: string[];                   // parsed arguments array
  matchedAlias: string;             // which command/alias was matched
  remainingText: string;            // text after command name
  invocationText: string;           // full trigger text

  // Methods
  replyResult(payload): void;       // reply with text + optional attachments
  replyText(text): void;            // reply with plain text
  stopPropagation(): void;          // block subsequent handlers
  
  // Aliases (all equivalent):
  // sendResult / reply / respond → replyResult
  // sendText / respondText → replyText
}
```

**replyResult payload formats:**
```javascript
// Format 1: plain string
event.replyResult("Hello!");

// Format 2: object with attachments
event.replyResult({
  text: "Here's an image:",
  attachments: [
    { source: "assets/photo.jpg", mimeType: "image/jpeg" },
  ],
});
```

### 8.2 Message Event (handler of registerMessageHandler)

Same common fields as CommandEvent, but `stage` = `"AdapterMessage"`.
No command-specific fields (no `args`, `commandPath`, etc.).
Has `stopPropagation()` but no `replyResult`/`replyText`.

### 8.3 Regex Event (handler of registerRegexHandler)

Common fields + regex-specific:
```typescript
{
  stage: "Regex";
  patternKey: string;       // the key of matched handler
  matchedText: string;      // full regex match
  groups: string[];         // capture groups: groups[0] = first ()
  namedGroups: object;      // named captures (?<name>...)
  
  stopPropagation(): void;  // available
  // NO replyResult/replyText
}
```

---

## 9. LLM PIPELINE HOOKS

The LLM pipeline processes AI chat messages through 5 sequential stages.
Register hooks with `hostApi.registerLlmHook({ hook, key, priority, handler })`.

### Pipeline Flow

```
User message
  │
  ▼
[on_waiting_llm_request]  ← observe: request is queued
  │
  ▼
[on_llm_request]          ← MUTABLE: modify the LLM request
  │
  ▼
  LLM Provider (OpenAI, etc.)
  │
  ▼
[on_llm_response]         ← observe: raw LLM response
  │
  ▼
[on_decorating_result]    ← MUTABLE: modify text/attachments before send
  │
  ▼
  Message sent to user
  │
  ▼
[after_message_sent]      ← post-send: can send followup messages
```

### 9.1 on_waiting_llm_request

```javascript
hostApi.registerLlmHook({
  hook: "on_waiting_llm_request",
  key: "my-plugin.waiting",
  priority: 100,
  metadata: {},
  handler(payload) {
    // payload is a flat object containing event fields
    // Read-only observation point
  },
});
```

### 9.2 on_llm_request — MUTABLE

```javascript
handler(payload) {
  const { event, request } = payload;
  
  // request readable properties:
  //   requestId, conversationId, messageIds, llmInputSnapshot,
  //   availableProviderIds, availableModelIdsByProvider,
  //   selectedProviderId, selectedModelId,
  //   systemPrompt, messages, temperature, topP, maxTokens,
  //   streamingEnabled, metadata

  // Mutation methods:
  request.appendSystemPrompt("Additional instructions...");
  request.replaceSystemPrompt("Replace entire system prompt");
  
  // Direct property assignment also works:
  // request.temperature = 0.7;
  // request.selectedProviderId = "other-provider";
}
```

### 9.3 on_llm_response — Read-Only

```javascript
handler(payload) {
  const { event, response } = payload;
  
  // response properties:
  //   requestId, providerId, modelId, text, markdown,
  //   finishReason, metadata,
  //   usage: { promptTokens, completionTokens, totalTokens,
  //            inputCostMicros, outputCostMicros, currencyCode },
  //   toolCalls: [{ toolName, arguments, metadata }]
}
```

### 9.4 on_decorating_result — MUTABLE ⭐ Most Common

Modify the final reply before it's sent to the user.

```javascript
handler(payload) {
  const { event, result } = payload;
  
  // result readable properties:
  //   requestId, conversationId, text, markdown,
  //   attachments: [{ uri, mimeType }],
  //   attachmentMutationIntent, shouldSend, isStopped

  // Text mutation:
  result.appendText("\n— appended by plugin");
  result.replaceText("completely replaced");
  result.clearText();

  // Attachment mutation:
  result.appendAttachment({ uri: "assets/img.png", mimeType: "image/png" });
  result.replaceAttachments([{ uri: "assets/a.jpg", mimeType: "image/jpeg" }]);
  result.clearAttachments();

  // Flow control:
  result.setShouldSend(false);    // prevent sending
  result.stop();                  // prevent subsequent hooks
}
```

### 9.5 after_message_sent — Post-Send + Followup ⭐

```javascript
handler(payload) {
  const { event, view } = payload;
  
  // view read-only properties:
  //   requestId, conversationId, sendAttemptId,
  //   platformAdapterType, platformInstanceKey,
  //   sentAtEpochMs, deliveryStatus, receiptIds,
  //   deliveredEntries: [{ entryId, entryType, textPreview, attachmentCount }],
  //   deliveredEntryCount,
  //   usage: { promptTokens, completionTokens, totalTokens, ... }

  // Followup send capability:
  //   view.canSendFollowup  — boolean, true on QQ platform, false on app_chat
  //   view.sendFollowup(text, attachments) — send an additional message

  if (view.canSendFollowup && typeof view.sendFollowup === "function") {
    const result = view.sendFollowup("Followup text", [
      { uri: "assets/extra.png", mimeType: "image/png" },
    ]);
    // result: { success: boolean, receiptIds: string[], errorSummary: string }
  }
}
```

**`sendFollowup` key facts:**
- Only available when `view.canSendFollowup === true` (external platforms like QQ)
- Sends a completely new message to the same conversation
- Attachment URIs follow the same resolution rules as command replies
- Returns send result with success/error info

---

## 10. CONFIGURATION SYSTEM

Two independent files serve different purposes:

| File | Purpose | Agent action |
|------|---------|-------------|
| `_conf_schema.json` | Define config fields + defaults | Create if plugin needs user settings |
| `schemas/settings-schema.json` | Define settings UI layout | Create if you want a settings screen |

### 10.1 _conf_schema.json

Each top-level key is a config field:

```json
{
  "field_key": {
    "type": "string",
    "description": "Human-readable description",
    "hint": "Detailed tooltip text",
    "default": "default value",
    "section": "group-id"
  }
}
```

**Supported `type` values:**

| type | JS typeof | Default example | Notes |
|------|-----------|----------------|-------|
| `"string"` | string | `"hello"` | Single-line text |
| `"text"` | string | `""` | Multi-line text |
| `"bool"` | boolean | `true` | Toggle switch |
| `"int"` | number | `42` | Integer |
| `"float"` | number | `3.14` | Float |
| `"number"` | number | `3` | Alias for `"float"`, **recommended** |

**Reading in code:**
```javascript
const settings = hostApi.getSettings() || {};
const value = settings.field_key ?? defaultValue;
// ALWAYS use ?? or || for defaults. First run = empty {}.
```

### 10.2 schemas/settings-schema.json

Controls the host app's settings UI rendering:

```json
{
  "title": "Plugin Settings",
  "sections": [
    {
      "sectionId": "general",
      "title": "General",
      "fields": [
        {
          "fieldType": "text_input",
          "fieldId": "field_key",
          "label": "Display Label",
          "placeholder": "Hint text",
          "defaultValue": "default"
        },
        {
          "fieldType": "toggle",
          "fieldId": "enable_feature",
          "label": "Enable Feature",
          "defaultValue": true
        },
        {
          "fieldType": "select",
          "fieldId": "mode",
          "label": "Mode",
          "defaultValue": "auto",
          "options": [
            { "value": "auto", "label": "Auto" },
            { "value": "manual", "label": "Manual" }
          ]
        }
      ]
    }
  ]
}
```

**Supported fieldType values:**

| fieldType | Renders as | defaultValue type |
|-----------|-----------|-------------------|
| `text_input` | Text input box | string |
| `toggle` | On/off switch | boolean |
| `select` | Dropdown menu | string (matching option.value) |

**Rules:**
- `fieldId` in settings-schema.json should match keys in `_conf_schema.json`
- Both files are optional and independent
- Recommend providing both for a complete experience

---

## 11. ATTACHMENTS & ASSETS

### Asset directory
Place static files under `assets/` in the plugin root:
```
my-plugin/
└── assets/
    ├── welcome.png
    └── sounds/
        └── ding.mp3
```

### URI resolution rules

| URI format | Behavior | Example |
|-----------|----------|---------|
| Relative path | Auto-resolved to `pluginRoot/path` | `"assets/img.png"` |
| Absolute path | Used as-is | `"/sdcard/photo.jpg"` |
| `http://` / `https://` | Network resource | `"https://example.com/img.png"` |
| `file://` | Used as-is | `"file:///sdcard/photo.jpg"` |
| `content://` | Android content provider | `"content://media/..."` |
| `base64:` | Inline base64 data | `"base64:iVBOR..."` |
| `plugin://` | Plugin protocol | `"plugin://..."` |

**Best practice**: Always use relative paths. The host resolves them correctly regardless of install location.

### Attachment object fields

```javascript
{
  source: "assets/photo.jpg",   // REQUIRED (highest priority)
  // Aliases (fallback order): uri > assetPath > path
  mimeType: "image/jpeg",       // OPTIONAL but recommended
  label: "Photo caption",       // OPTIONAL display text
  // Aliases: altText, fileName
}
```

### Where attachments are used

1. **Command handler** — `event.replyResult({ text, attachments })`
2. **on_decorating_result hook** — `result.appendAttachment({ uri, mimeType })`
   - Note: in hooks, field name is `uri` not `source`
3. **after_message_sent hook** — `view.sendFollowup(text, [{ uri, mimeType }])`
   - Uses `uri` field name

### Common MIME types

| Type | mimeType |
|------|----------|
| JPEG | `image/jpeg` |
| PNG | `image/png` |
| GIF | `image/gif` |
| WebP | `image/webp` |
| MP3 | `audio/mpeg` |
| MP4 | `video/mp4` |

---

## 12. COMPLETE EXAMPLES

### Example A: Minimal command-only plugin

A plugin that responds to `/ping` with "pong!".

**File: manifest.json**
```json
{
  "name": "ping-plugin",
  "description": "Responds to /ping with pong!",
  "version": "1.0.0",
  "author": "you",
  "entryPoint": "runtime/bootstrap.js",
  "protocolVersion": 2,
  "sourceType": "GIT",
  "sourceUrl": "https://github.com/you/ping-plugin.git"
}
```

**File: android-plugin.json**
```json
{
  "runtime": "js_quickjs",
  "minHostVersion": "1.0.0"
}
```

**File: runtime/bootstrap.js**
```javascript
export function activate(hostApi) {
  hostApi.registerCommand("ping", "Test ping command", (event) => {
    event.replyResult({ text: "pong!" });
  });
}
```

That's it. Three files, fully functional plugin.

---

### Example B: LLM decorator with config

A plugin that prepends a custom prefix to all LLM responses with configurable behavior.

**File: manifest.json**
```json
{
  "name": "reply-decorator",
  "description": "Adds custom prefix to LLM responses",
  "version": "1.0.0",
  "author": "you",
  "entryPoint": "runtime/bootstrap.js",
  "protocolVersion": 2
}
```

**File: android-plugin.json**
```json
{
  "runtime": "js_quickjs",
  "minHostVersion": "1.0.0"
}
```

**File: _conf_schema.json**
```json
{
  "prefix": {
    "type": "string",
    "description": "Prefix added before LLM responses",
    "default": "[Bot] "
  },
  "enabled": {
    "type": "bool",
    "description": "Enable prefix",
    "default": true
  }
}
```

**File: schemas/settings-schema.json**
```json
{
  "title": "Reply Decorator Settings",
  "sections": [
    {
      "sectionId": "general",
      "title": "General",
      "fields": [
        {
          "fieldType": "toggle",
          "fieldId": "enabled",
          "label": "Enable prefix",
          "defaultValue": true
        },
        {
          "fieldType": "text_input",
          "fieldId": "prefix",
          "label": "Response prefix",
          "placeholder": "[Bot] ",
          "defaultValue": "[Bot] "
        }
      ]
    }
  ]
}
```

**File: runtime/bootstrap.js**
```javascript
export function activate(hostApi) {
  hostApi.onDecoratingResult((result) => {
    const settings = hostApi.getSettings() || {};
    const enabled = settings.enabled ?? true;
    const prefix = settings.prefix ?? "[Bot] ";
    if (!enabled) return;

    const original = result.getText();
    result.setText(prefix + original);
  });
}
```

---

### Example C: Followup sender with asset image

A plugin that sends a welcome image after each LLM response.

**File: manifest.json**
```json
{
  "name": "welcome-followup",
  "description": "Sends a welcome image after each reply",
  "version": "1.0.0",
  "author": "you",
  "entryPoint": "runtime/bootstrap.js",
  "protocolVersion": 2
}
```

**File: android-plugin.json**
```json
{
  "runtime": "js_quickjs",
  "minHostVersion": "1.0.0"
}
```

**File: runtime/bootstrap.js**
```javascript
export function activate(hostApi) {
  hostApi.afterMessageSent((view) => {
    if (!view.canSendFollowup) return;
    view.sendFollowup("Thanks for chatting!", [
      { uri: "assets/welcome.png", mimeType: "image/png" }
    ]);
  });
}
```

**File: assets/welcome.png**
(Place image file here)

---

### Example D: Mixed command + LLM hook + config

A "word counter" plugin that provides `/wordcount` command and appends word count to every LLM response.

**File: manifest.json**
```json
{
  "name": "word-counter",
  "description": "Counts words in LLM responses",
  "version": "1.0.0",
  "author": "you",
  "entryPoint": "runtime/bootstrap.js",
  "protocolVersion": 2
}
```

**File: android-plugin.json**
```json
{ "runtime": "js_quickjs", "minHostVersion": "1.0.0" }
```

**File: _conf_schema.json**
```json
{
  "show_count": {
    "type": "bool",
    "description": "Append word count to responses",
    "default": true
  },
  "count_format": {
    "type": "string",
    "description": "Format string ({count} = word count)",
    "default": "\n\n---\nWord count: {count}"
  }
}
```

**File: runtime/bootstrap.js**
```javascript
function countWords(text) {
  if (!text) return 0;
  return text.trim().split(/\s+/).filter(w => w.length > 0).length;
}

export function activate(hostApi) {
  // Command: count words in user's message
  hostApi.registerCommand("wordcount", "Count words in your message", (event) => {
    const text = event.args || "";
    const count = countWords(text);
    event.replyResult({ text: `Word count: ${count}` });
  });

  // Hook: append word count to every LLM response
  hostApi.onDecoratingResult((result) => {
    const settings = hostApi.getSettings() || {};
    if (!(settings.show_count ?? true)) return;

    const format = settings.count_format ?? "\n\n---\nWord count: {count}";
    const text = result.getText();
    const count = countWords(text);
    result.setText(text + format.replace("{count}", String(count)));
  });
}
```

---

## 13. COMMON PITFALLS

| # | Pitfall | Why it breaks | Fix |
|---|---------|--------------|-----|
| 1 | Using `require()` or `module.exports` | QuickJS sandbox uses ES modules only | Use `import`/`export` syntax |
| 2 | Using Node.js APIs (`fs`, `path`, `Buffer`, `process`) | Sandbox is NOT Node.js | Use only hostApi and standard JS |
| 3 | Not providing `??` defaults when reading settings | First run returns `{}` | Always: `settings.key ?? defaultValue` |
| 4 | Duplicate keys between `_conf_schema.json` and `settings-schema.json` fieldIds | Host may freeze or crash | Ensure keys are consistent but not duplicated across files |
| 5 | Putting `bootstrap.js` in root instead of `runtime/` | Host won't find entry point | entryPoint in manifest must match actual path |
| 6 | Registering handlers outside `activate()` | hostApi not available yet | All registrations go inside `activate()` |
| 7 | Returning async/Promise from handlers | QuickJS may not await them properly | Keep handlers synchronous |
| 8 | Forgetting `protocolVersion: 2` in manifest | Falls back to legacy protocol | Always include `"protocolVersion": 2` |
| 9 | Using absolute paths for assets | Breaks on different devices | Use relative paths from plugin root |
| 10 | Modifying read-only event fields | Silently ignored, no effect | Only modify fields documented as mutable |
| 11 | Missing `android-plugin.json` | Plugin won't load on Android host | Always include with `"runtime": "js_quickjs"` |
| 12 | JSON with trailing commas or comments | Parse error, plugin fails to load | Use strict JSON (no comments, no trailing commas) |
| 13 | Using `view.sendFollowup` without checking `canSendFollowup` | Runtime error | Always guard: `if (view.canSendFollowup)` |

---

## 14. PRE-DELIVERY CHECKLIST

Before delivering a plugin to the user, verify every item:

```
[ ] manifest.json exists and is valid JSON
[ ] manifest.json has: name, description, version, author, entryPoint, protocolVersion (2)
[ ] android-plugin.json exists with runtime: "js_quickjs"
[ ] runtime/bootstrap.js exists at the path specified by entryPoint
[ ] bootstrap.js exports function activate(hostApi)
[ ] All handler registrations are INSIDE activate()
[ ] No Node.js APIs used (no require, fs, path, Buffer, process, etc.)
[ ] Only ES module syntax (import/export), no CommonJS
[ ] All handlers are synchronous (no async/await)
[ ] If _conf_schema.json exists: valid JSON, all fields have type + default
[ ] If settings-schema.json exists: valid JSON, all fieldIds match _conf_schema keys
[ ] Settings reads use ?? or || for defaults
[ ] Asset paths are relative (from plugin root)
[ ] Attachment objects use correct field name (source for commands, uri for hooks)
[ ] sendFollowup calls are guarded by canSendFollowup check
[ ] No trailing commas or comments in any JSON file
[ ] All files use UTF-8 encoding
```

---

## 15. API QUICK REFERENCE CARD

```
hostApi.registerCommand(name, description, handler)
  handler(event) → event.replyResult({ text, attachments })
                 → event.args (string after command)

hostApi.registerMessageHandler(handler)
  handler(event) → event.replyResult({ text, attachments })
                 → event.text (full message text)

hostApi.registerRegexHandler(pattern, handler)
  handler(event) → event.replyResult({ text, attachments })
                 → event.match (regex match array)

hostApi.onWaitingLlmRequest(handler)
  handler(context) → context.senderName, context.messageText (read-only)

hostApi.onLlmRequest(handler)
  handler(request) → request.getPrompt() / request.setPrompt(str)
                   → request.getSystemPrompt() / request.setSystemPrompt(str)

hostApi.onLlmResponse(handler)
  handler(response) → response.getText() (read-only)

hostApi.onDecoratingResult(handler)
  handler(result) → result.getText() / result.setText(str)
                  → result.appendAttachment({ uri, mimeType })

hostApi.afterMessageSent(handler)
  handler(view) → view.canSendFollowup (boolean)
               → view.sendFollowup(text, attachments?)
               → view.finalText (string, read-only)

hostApi.getSettings() → object | {}
hostApi.log(message)  → void (debug log)
```

---

*End of document. This guide is self-contained. An agent should be able to create a fully functional plugin using only the information above.*
