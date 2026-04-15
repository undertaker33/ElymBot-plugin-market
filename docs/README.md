# ElymBot 插件 v2 开发文档

> 适用于 `protocolVersion: 2` · 运行时 `js_quickjs` · Host ≥ 0.4.0

欢迎来到 ElymBot 插件开发指南！当前指南面向想开发 ElymBot 插件的开发者。使用本指南需要具备以下基础知识：

1. 具有一定的QuickJS脚本经验。
2. 具有Git、GitHub的使用经验。

并准备最小环境：

1. ElymBot 宿主应用：用于导入、启用、运行和调试插件。
2. 一个可用的文本编辑器
3. 一个zip压缩工具
4. GitHub账号和本地git环境

推荐使用vibe coding开发(codex/Claude code/cursor等)，告诉你的智能体助手：

```
请先阅读AGENT-PLUGIN-DEV-GUIDE.md，并严格按照其中的约束开发插件。

要求：
1. 先以文档为唯一执行基线理解当前插件契约、模板使用方式、宿主能力边界和打包规则。
2. 用户只描述插件功能时，由你自行完成需求拆解、模板复制、代码实现、配置设计、资源整理和打包准备。
3. 第一次执行前，如果还没有模板本地路径，先向我索取模板本地路径。
4. 不允许修改宿主代码来适配插件。
5. 如果宿主当前不支持某项核心能力，先说明限制，再给出可行的降级方案。
6. 输出结果必须是可导入、可运行、可分发的 Android Native 外部插件目录。
```

记得下载[AGENT-PLUGIN-DEV-GUIDE.md]()后告诉你的agent它存放在哪

## 文档索引

| 文件 | 内容 |
|------|------|
| [01-快速开始.md](01-快速开始.md) | 从零到可运行插件的最短路径 |
| [02-包结构与描述文件.md](02-包结构与描述文件.md) | 目录布局、manifest.json、android-plugin.json |
| [03-Host-API参考.md](03-Host-API参考.md) | `hostApi` 上所有可用方法和工具函数 |
| [04-处理器与钩子.md](04-处理器与钩子.md) | 命令 / 消息 / 正则 / LLM 钩子 / 生命周期 的注册与事件对象 |
| [05-配置与设置.md](05-配置与设置.md) | `_conf_schema.json` 和 `settings-schema.json` 的格式 |
| [06-资源与附件.md](06-资源与附件.md) | 图片/文件附件的路径规则与回复方式 |

## 模板插件

`helloworld` 模板是一个最小可导入、可执行、可配置的模板插件：

- **Git 仓库**: https://github.com/undertaker33/helloworld.git

覆盖了命令处理、正则匹配、LLM 钩子、生命周期、配置读取五种能力，可直接导入 ElymBot 运行。
