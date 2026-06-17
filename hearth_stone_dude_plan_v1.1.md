# 炉石传说记牌器 (HearthStone Dude) 实施计划

## 一、python-hslog 项目核心分析

### 1.1 日志读取流程

```
Power.log 文件
    │
    ▼
LogParser.read_line()          ← 逐行读取，正则匹配 TIMESTAMP_RE
    │
    ├─ 解析行格式: "D HH:MM:SS.fffffff Class.Method() - message"
    │
    ▼
PowerHandler / ChoicesHandler / OptionsHandler   ← 三个处理器分发
    │
    ├─ CREATE_GAME      → 创建 PacketTree (一局游戏开始)
    ├─ GameEntity        → 注册游戏实体
    ├─ Player            → 注册玩家 (EntityID, PlayerID, GameAccountId)
    ├─ FULL_ENTITY       → 创建实体 (entity_id, card_id, tags)
    ├─ SHOW_ENTITY       → 卡牌被揭示 (抽牌等)
    ├─ HIDE_ENTITY       → 卡牌隐藏 (zone变化)
    ├─ CHANGE_ENTITY     → 卡牌变形
    ├─ TAG_CHANGE        → 标签变化 (最核心的事件)
    │   ├─ ZONE 变化     → 卡牌移动 (DECK→HAND=抽牌, HAND→PLAY=出牌, PLAY→GRAVEYARD=死亡)
    │   ├─ CONTROLLER    → 控制权变更
    │   ├─ ZONE_POSITION → 手牌/场上位置
    │   ├─ ATTACK/HEALTH → 攻击力/生命值变化
    │   ├─ COST          → 费用变化
    │   └─ ...
    ├─ BLOCK_START/END   → 嵌套块 (PLAY=出牌, ATTACK=攻击, POWER=英雄技能, TRIGGER=触发, DEATHS=死亡...)
    ├─ Choices/SendChoices → 发现/选择卡牌
    ├─ Options/SendOption  → 玩家操作 (出牌目标选择等)
    └─ ...
    │
    ▼
PacketTree                   ← 整局游戏的数据包树
    │
    ▼
EntityTreeExporter.export()  → 导出为 Game 对象
    │
    └─ Game 包含: entities (实体列表), players (玩家), tags (标签字典)
```

### 1.2 关键数据包类型 (packets.py)

| 数据包            | 用途                         | 对记牌器的意义             |
| -------------- | -------------------------- | ------------------- |
| `CreateGame`   | 游戏初始化                      | 识别游戏开始，获取玩家信息       |
| `FullEntity`   | 实体创建 (带 CardID)            | 知道某张卡牌进入了游戏         |
| `ShowEntity`   | 卡牌揭示                       | 知道对方抽到了什么牌 (对方手牌可见) |
| `HideEntity`   | 卡牌隐藏 (zone变化)              | 卡牌回手/洗入牌库等          |
| `ChangeEntity` | 卡牌变形                       | 卡牌变成另一张卡            |
| `TagChange`    | 标签变化                       | **核心**: 跟踪所有状态变化    |
| `Block`        | 嵌套块 (PLAY/ATTACK/TRIGGER等) | 理解事件的上下文和因果关系       |
| `Choices`      | 发现/选择                      | 跟踪发现类卡牌的选择          |
| `Options`      | 可选操作                       | 了解当前可执行的操作          |
| `ShuffleDeck`  | 洗牌                         | 牌库发生变化              |

### 1.3 核心依赖

- `hearthstone` 包: 提供 GameTag, BlockType, Zone, CardType 等枚举和 Game/Player/Card 实体类
- `aniso8601`: 时间戳解析

### 1.4 结果输出形式

- **PacketTree**: 原始解析后的数据包树，包含所有按时间顺序排列的数据包
- **Game 对象**: 通过 `EntityTreeExporter` 导出，模拟了完整的游戏状态，包含所有实体及其当前标签
- **友好玩家导出**: `FriendlyPlayerExporter` 通过分析 SHOW\_ENTITY 来判断哪个玩家是"我方"

***

## 二、记牌器项目设计

### 2.1 项目结构

```
d:\Git\xxkj_2026\hearth_stone–dude/
├── backend/                     # Python 后端
│   ├── __init__.py
│   ├── log_monitor.py           # 日志文件监控 (tail -f 模式)
│   ├── game_state.py            # 游戏状态跟踪 (基于hslog扩展)
│   ├── card_tracker.py          # 记牌器核心逻辑
│   ├── deck_analyzer.py         # 卡组分析 (已出牌/剩余牌)
│   ├── api_server.py            # FastAPI HTTP/WebSocket 服务
│   ├── rag_engine.py            # RAG 引擎 (AI扩展)
│   └── config.py                # 配置文件
├── overlay/                     # 前端覆盖层
│   ├── package.json
│   ├── main.js                  # Electron 主进程
│   ├── preload.js
│   ├── index.html               # 覆盖层 HTML
│   ├── renderer.js              # 渲染进程逻辑
│   └── styles.css               # 覆盖层样式
├── data/                        # 数据目录
│   └── decks/                   # 卡组文档库 (用于RAG embedding)
├── requirements.txt
└── README.md
```

### 2.2 技术选型

| 层级            | 技术                                       | 理由                                                |
| ------------- | ---------------------------------------- | ------------------------------------------------- |
| 后端框架          | Python + FastAPI                         | 轻量、高性能、原生支持 WebSocket                             |
| 日志解析          | 直接引用 hslog (pip install)                 | 复用成熟的解析逻辑，不重复造轮子                                  |
| 前端覆盖层         | Electron + HTML/CSS/JS                   | 成熟的透明窗口方案，`transparent:true` + `alwaysOnTop:true` |
| 覆盖层通信         | WebSocket                                | 实时推送游戏状态到前端                                       |
| RAG/Embedding | chromadb / faiss + sentence-transformers | 本地向量数据库，轻量部署                                      |
| AI推理          | OpenAI API / 本地模型                        | 灵活选择                                              |

### 2.3 记牌器核心功能 (Phase 1)

#### 2.3.1 日志监控 (`log_monitor.py`)

- 自动定位 Power.log 文件路径 (通常在 `%LOCALAPPDATA%/Blizzard/Hearthstone/Logs/`)
- 使用文件 tail 模式实时监控新增日志行
- 调用 `hslog.LogParser` 解析新行
- 通过 WebSocket 推送解析结果到前端

#### 2.3.2 游戏状态跟踪 (`game_state.py`)

基于 `hslog` 的 `EntityTreeExporter` 扩展，维护以下状态:

- **玩家信息**: 用户名、职业 (通过英雄卡牌推断)、先手/后手
- **双方手牌数量**: 通过 `ZONE=HAND` 的 TAG\_CHANGE 跟踪
- **双方牌库剩余**: 初始30张 - 已抽牌数
- **己方手牌详情**: 通过 SHOW\_ENTITY 获取己方手牌的 CardID
- **对方已出牌列表**: 通过 `ZONE=PLAY` 且 `CONTROLLER=对方` 的 TAG\_CHANGE 跟踪
- **双方坟场**: 通过 `ZONE=GRAVEYARD` 跟踪
- **法力水晶**: 当前回合/可用/过载

#### 2.3.3 记牌器核心 (`card_tracker.py`)

- 跟踪每张卡牌的生命周期: 抽到 → 手牌 → 打出 → 战场 → 死亡 → 坟场
- 统计双方已出牌: 按卡牌名称汇总
- 计算对方剩余关键牌: 如 AOE、解牌、核心随从等
- 跟踪发现/生成的卡牌 (非原始卡组中的卡)

#### 2.3.4 前端覆盖层 (`overlay/`)

覆盖层显示:

- **左侧栏**: 对方职业图标、已出牌列表 (按费用排列)
- **右侧栏**: 己方手牌剩余、牌库剩余、坟场卡牌
- **顶部栏**: 双方法力水晶、回合数
- 设计为半透明、可穿透点击 (click-through)

### 2.4 AI 扩展功能 (Phase 2)

#### 2.4.1 AI运行模式决策

**Agent运行模式**: 采用事件驱动（非持续运行）

| 方案   | 优点         | 缺点             | 本项目选择 |
| ---- | ---------- | -------------- | ----- |
| 持续运行 | 实时响应、状态保持  | 资源消耗高、复杂度高     | ❌     |
| 事件驱动 | 资源效率高、逻辑清晰 | 响应有延迟(\~100ms) | ✅     |

**自动触发机制**: 在 `game_state.py` 中实现事件钩子系统，玩家无需手动触发

#### 2.4.2 事件触发时机

当以下关键游戏事件发生时自动触发AI分析：

- 当对手打出数据库中记录的卡组关键牌时，触发敌方卡组推测
- 我方回合开始抽牌结束后，分析出牌建议
- 我方即将执行选择时（例如”发现“、”抉择“等需要玩家选择的情况），分析选择建议

#### 2.4.3 RAG 卡组文档库 (`rag_engine.py`)

- 收集当前社区活跃卡组数据 (可从 HSReplay、d0nkey 等网站爬取或手动整理)
- 使用 `sentence-transformers` 做 embedding
- 存入 `chromadb` 向量数据库
- 卡组文档包含: 职业、卡组名、核心卡牌列表、节奏点、弱点、打法策略

#### 2.4.4 LangChain 使用策略

**Phase 1（基础版）**: 不使用LangChain

- 功能：RAG检索卡组匹配 + 简单规则引擎
- 理由：逻辑简单，直接调用 `chromadb` + `sentence-transformers` 即可
- 代码复杂度低，易于维护

**Phase 2（进阶版）**: 根据需求决定是否引入LangChain

- 功能：复杂战术分析、多步推理、动态提示工程
- 推荐组合：`langchain-core` + `langchain-chroma` + `langchain-openai/ollama`
- 引入时机：当需要多轮对话记忆、工具调用链、Agent状态机时

#### 2.4.5 卡组推断

- Agent 根据对方职业 + 已出牌列表，在 RAG 库中检索最匹配的卡组
- 输出: 卡组名称、置信度、剩余关键牌、需要注意的节奏点
- 通过 WebSocket **自动推送**到前端显示，无需玩家手动触发

***

## 三、实施步骤

### Step 1: 项目初始化

- 创建 `hearth_stone–dude` 目录结构
- 编写 `requirements.txt` (hslog, fastapi, uvicorn, websockets, watchdog)
- 编写 `setup.py` / `pyproject.toml`

### Step 2: 日志监控与解析

- 实现 `log_monitor.py`: 使用 `watchdog` 监控 Power.log 文件变化
- 实现 `game_state.py`: 继承 `hslog` 的导出器，实时维护游戏状态
- 测试: 使用 hslog 自带的测试日志文件验证

### Step 3: 记牌器核心逻辑

- 实现 `card_tracker.py`: 跟踪手牌、牌库、战场、坟场
- 实现 `deck_analyzer.py`: 分析已出牌/剩余牌统计
- 单元测试

### Step 4: API 服务

- 实现 `api_server.py`: FastAPI + WebSocket
- 端点: `/ws` (WebSocket, 实时推送游戏状态)
- 端点: `/api/status` (HTTP, 当前游戏状态快照)

### Step 5: 前端覆盖层

- 初始化 Electron 项目
- 实现透明覆盖层窗口 (alwaysOnTop, transparent, click-through 部分区域)
- 实现 WebSocket 客户端连接后端
- 实现 UI 组件: 手牌计数、牌库计数、已出牌列表、法力水晶
- 样式: 半透明深色背景、炉石风格

### Step 6: AI 扩展 (Phase 2)

- 收集/整理卡组数据
- 实现 `rag_engine.py` (embedding + 向量检索)
- 实现卡组推断逻辑
- 前端增加 AI 建议显示区域

***

## 四、关键决策与假设

1. **引用 hslog 的方式**: 直接 `pip install hslog` 作为依赖，通过 `from hslog import LogParser` 使用其解析能力，然后通过自定义 Exporter 扩展游戏状态跟踪
2. **Power.log 路径**: 默认为 `%LOCALAPPDATA%\Blizzard\Hearthstone\Logs\Power.log`，提供配置项覆盖
3. **前端覆盖层**: 使用 Electron，窗口设置为 `alwaysOnTop: true`, `transparent: true`, `frame: false`, 部分区域 `setIgnoreMouseEvents(true)` 实现点击穿透
4. **覆盖层定位**: 默认在屏幕右侧，用户可拖拽调整位置
5. **卡组数据来源**: 初期手动整理几个主流卡组作为示例，后续可扩展自动爬取

***

## 五、验证步骤

1. 启动后端: `python -m backend.api_server`
2. 启动前端: `cd overlay && npm start`
3. 启动炉石传说，进入一场游戏
4. 验证覆盖层显示: 双方手牌数、牌库剩余、法力水晶
5. 验证出牌跟踪: 对方每出一张牌，覆盖层更新
6. 验证 WebSocket 实时性: 延迟 < 500ms

