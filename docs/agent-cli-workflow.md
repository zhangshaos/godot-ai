# Agent 使用 godot-ai CLI 操作 Godot Editor 协作规范

本文档面向通过 shell / DevSpace 调用 `godot-ai` 的自动化开发 Agent。目标是让 Agent 在没有直接 MCP tool binding 的情况下，通过 one-shot CLI 安全查询、创建、修改、删除 Godot Editor 中的场景、节点和资源，并形成可审查、可回滚、可验证的协作闭环。

具体工具参数和当前清单以 `docs/TOOLS.md`、`godot-ai tools --json` 与实际 tool schema 为准。

## 1. 标准链路

```text
Agent
→ shell / DevSpace.bash
→ godot-ai CLI
→ shared FastMCP backend
→ WebSocket
→ Godot Editor Plugin
→ Godot Editor
```

CLI 约定：

- `godot-ai status --json` 只探测 backend，不启动；
- `godot-ai tools --json` 自动 start-or-adopt backend，并列出 tools；
- `godot-ai call <tool> --args '<json>'` 自动 start-or-adopt backend 并调用 tool；
- stdout 只输出 JSON；日志和错误走 stderr；成功 exit code 为 `0`，失败为非 `0`。

Windows 跨仓库调用推荐使用 godot-ai 自己虚拟环境中的绝对路径，例如：

```text
D:/path/to/godot-ai/.venv/Scripts/godot-ai.exe
```

其它仓库不需要各自安装 Python 环境，也不必把 godot-ai 加入全局 PATH。

## 2. 总体工作流

Agent 操作 Godot Editor 时遵循：

```text
确认目标 Editor / Session
→ 先读后写
→ 最小范围修改
→ 优先 Godot-aware tool
→ 显式保存需要落盘的 Scene
→ MCP 回读
→ Git diff / status 验证
```

不得因为 CLI 可写，就跳过目标项目原有架构、命名、资源和 review 规则。

## 3. Session 与 Scene 安全

写操作前至少调用：

```bash
godot-ai call editor_state --args '{}'
```

确认 `project_name`、`current_scene`、`readiness` 和运行状态。

如果可能同时打开多个 Godot Editor，先执行：

```bash
godot-ai call session_manage --args '{"op":"list","params":{}}'
```

之后显式传入 `session_id`。对于 `<domain>_manage`，`session_id` 与 `op`、`params` 同级，不放进 `params`。

只要 tool 支持 `scene_file` guard，场景写操作应传入预期场景路径。这样用户在操作过程中切换 Scene 时，写入会以 `EDITED_SCENE_MISMATCH` 失败，而不是误改新 Scene。

## 4. 查询规范

优先读取 Godot Editor 的实际状态，而不是只从 `.tscn/.tres` 文本猜测 Editor 状态。

常用读取入口：

```text
editor_state
scene_get_hierarchy
node_get_properties
node_find
logs_read
editor_screenshot
scene_manage(op="get_roots")
resource_manage(op="search" / "get_info" / "load")
filesystem_manage(op="search" / "read_text")
script_manage(op="read" / "find_symbols")
```

推荐顺序：

1. `editor_state` 确认项目和场景；
2. `scene_get_hierarchy` 获取节点真实路径；
3. `node_get_properties` 确认 Inspector 属性准确名称和类型；
4. 再执行写操作。

设置属性前不要猜 Godot 属性名；先通过 `node_get_properties` 或 ClassDB 相关 tool 获取事实。

## 5. 创建与修改

### Scene / Node

优先使用：

```text
scene_manage(op="create")
node_create
node_set_property
node_manage(op="rename" / "move" / "reparent")
node_manage(op="add_to_group" / "remove_from_group")
script_attach
script_manage(op="detach")
```

创建后使用 tool 返回的真实路径继续操作，不自己推测 Godot 最终命名。

### Resource

优先使用对应领域 tool：

```text
resource_manage
theme_manage
material_manage
animation_create / animation_manage
particle_manage
camera_manage
audio_manage
tilemap_manage
tileset_manage
gridmap_manage
csg_manage
```

Theme、Material、Animation 等资源不要优先通过手写 `.tres` 文本修改。专用 tool 可以保留 Godot 类型转换、UndoRedo、资源引用和 EditorFileSystem 一致性。

### Script / 通用文件

`script_create` 和 `filesystem_manage(op="write_text")` 可以直接落盘，但通常不可 Undo。能通过更高层 Godot tool 完成时，不优先使用通用文件写入。

## 6. 删除规范与当前边界

当前可以删除或移除多类 Editor 对象，例如：

```text
node_manage(op="delete")
script_manage(op="detach")
animation_manage(op="delete")
autoload_manage(op="remove")
input_map_manage(op="remove_action")
```

删除前先读取并确认目标路径、类型和所属 Scene。

当前 `filesystem_manage` / `resource_manage` 尚没有对任意 `.tscn/.tres/res://` 文件都成立的 generic delete-file 操作。因此如果任务要求删除资源文件本身：

1. 先检查对应领域是否已有专用 delete/remove；
2. 有则用专用 tool；
3. 没有则明确报告能力缺口；
4. 按目标仓库规则由用户删除，或优先给 godot-ai 增加安全的文件删除能力。

不要为了绕过缺口重新实现 WebSocket 协议或在每个游戏仓库各写一套 Godot 文件解析器。

## 7. Scene 保存与未保存改动

`node_create`、`node_set_property`、`node_manage` 等通常先修改 Editor 内存状态；需要 `scene_save` 才明确落盘。

Agent 收到明确 Godot 写任务，表示用户授权完成该任务所需的 Editor 修改与保存，但**不等于授权覆盖任务开始前已有的未知未保存改动**。

如果无法判断当前 Scene 是否混有用户先前未保存的独立改动，应先确认这一点，再执行会把当前内存状态整体落盘的 `scene_save`。

不得用 `scene_open(force_reload=true)` 清理现场，因为它会丢弃当前 Scene 的未保存内存修改。

`project_run` 默认可能触发保存。只做 smoke test 且不希望临时 Scene 改动落盘时，使用：

```text
project_run(autosave=False)
```

## 8. Undo 与批处理

优先使用返回 `undoable: true` 的 Editor 写工具。文件写、Scene open/save 等 `undoable: false` 操作需要更保守，并依赖 Git diff 验证。

`batch_execute` 只适合已经明确验证过的一组连续操作。探索未知节点结构、属性名或资源契约时，先单步读取和单步修改，不要把大量猜测写入 batch。

同时注意：`batch_execute.commands[].command` 使用 plugin command name，不是 MCP tool name；映射以 Python handlers 为准。

## 9. 写后验证闭环

任何 Godot 写任务完成后至少执行两层验证。

### Godot 回读

根据改动使用：

```text
scene_get_hierarchy
node_get_properties
resource_manage(op="get_info" / "load")
相关领域 get/list/validate
logs_read
```

确认 Editor 中真实状态符合预期。

### Git / 文件验证

回到目标仓库执行只读检查：

```text
git status --short
git diff --check
git diff -- <目标文件>
```

确认只修改预期文件，没有顺带保存无关 Scene / Resource，也没有产生异常临时资源。

Godot MCP 回读验证 Editor 状态，Git diff 验证磁盘事实；两者不能互相替代。

## 10. 与普通代码工具的分工

推荐职责：

```text
普通代码 / 文档 / 非 Godot 文本
→ 目标仓库原有代码工具（如 DevSpace.edit/write）

SceneTree / Inspector / Godot Resource / Script attach
→ godot-ai CLI

修改后
→ godot-ai 回读 + 目标仓库测试 + Git diff
```

不要因为 `.tscn/.tres` 本质上是文本格式，就默认使用普通文本编辑器绕过 Godot Editor；除非目标仓库明确规定某类资源必须文本生成，或 godot-ai 当前确实缺少等价能力。

## 11. 用户与 Agent 协作职责

用户负责：

- 给出目标行为、界面或资源需求；
- 对布局、美术、手感、动画、音频等主观结果做最终验收；
- review 最终 Git diff；
- 当 Agent 无法判断任务开始前是否已有未保存 Editor 改动时提供该信息。

Agent 负责：

- 自己查询当前 Editor 状态，不要求用户重复描述可读取的信息；
- 自己创建、修改、删除 godot-ai 已支持的 Scene / Node / Resource；
- 自己完成 Inspector 绑定、脚本挂载等可通过 MCP 完成的机械操作；
- 写前确认 session / scene / property；
- 写后保存、回读、检查日志与 Git diff；
- 清楚报告 godot-ai 当前不支持的操作，不假装完成。

## 12. 标准 Scene 修改流程

一次典型修改应接近：

```text
1. editor_state
2. 如有多 Editor：session_manage(list) 并 pin session_id
3. scene_get_hierarchy
4. node_get_properties
5. node_create / node_set_property / node_manage
6. 如需要：完成 Inspector 绑定或 script_attach
7. scene_save
8. scene_get_hierarchy + node_get_properties 回读
9. logs_read
10. git status / git diff / git diff --check
11. 用户做视觉 / 手感实机验收
```

如果中途发现当前 Scene、session 或属性与预期不一致，停止后续写入并重新读取事实，不继续基于旧假设连写。

## 13. 能力缺口处理

发现 godot-ai 缺少目标能力时：

```text
先确认现有 tool / rollup 是否真的没有等价能力
→ 判断缺口是否通用
→ 通用缺口优先回到 godot-ai 补能力
→ 不在业务仓库长期维护绕过 Godot Editor 的临时实现
```

引入 godot-ai 的目标是让 Godot Editor 成为 Agent 可以直接查询和操作的正式开发环境，而不是继续依赖用户人工同步 SceneTree 和 Inspector 状态。
