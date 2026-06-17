# 炉石传说记牌器 (HearthStone Dude)

一个基于 python-hslog 的炉石传说记牌器，提供实时游戏状态跟踪、AI 卡组分析和透明覆盖层显示。

## 项目结构

```
hearth_stone_dude/
├── backend/                 # Python 后端
│   ├── __init__.py
│   ├── config.py           # 配置文件
│   ├── log_monitor.py      # 日志监控模块
│   ├── game_state.py       # 游戏状态跟踪
│   ├── card_tracker.py     # 卡牌跟踪核心逻辑
│   ├── deck_analyzer.py    # 卡组分析和匹配
│   ├── rag_engine.py       # RAG 引擎和 AI 集成
│   └── api_server.py       # FastAPI 服务
├── overlay/                # Electron 前端覆盖层
│   ├── package.json
│   ├── main.js            # Electron 主进程
│   ├── index.html         # 覆盖层界面
│   ├── renderer.js        # 渲染进程逻辑
│   └── styles.css         # 样式文件
├── data/                   # 数据目录
│   └── decks/             # 卡组数据
├── python-hslog/          # 日志解析库
├── requirements.txt       # Python 依赖
└── README.md
```

## 技术栈

- **后端**: Python + FastAPI + WebSocket
- **日志解析**: python-hslog
- **前端**: Electron + HTML/CSS/JavaScript
- **文件监控**: watchdog
- **AI 集成**: Kimi (Moonshot) API

## 安装步骤

### 1. 快速启动（Windows 用户推荐）

项目提供了便捷的批处理脚本，一键完成环境配置：

```bash
cd e:\Project\CardMaster\hearth_stone_dude
setup.bat
```

安装完成后，可以直接使用：
- `start_backend.bat` - 启动后端服务
- `start_overlay.bat` - 启动前端覆盖层

### 2. Python 虚拟环境设置（推荐）

**强烈建议使用虚拟环境**以避免污染全局 Python 环境：

#### Windows (PowerShell):
```bash
cd e:\Project\CardMaster\hearth_stone_dude

# 创建虚拟环境（将在项目目录下创建 venv 文件夹）
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 注意：如果执行策略限制，需要先运行：
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Windows (CMD):
```bash
cd e:\Project\CardMaster\hearth_stone_dude
python -m venv venv
venv\Scripts\activate.bat
```

#### Linux/Mac:
```bash
cd hearth_stone_dude
python3 -m venv venv
source venv/bin/activate
```

### 3. 后端依赖安装

确保已激活虚拟环境，然后：

```bash
pip install -r requirements.txt
```

**注意**：虚拟环境的所有依赖都安装在项目目录下的 `venv` 文件夹中，不会影响系统 Python 环境。

### 4. 前端安装

确保已安装 Node.js 和 npm，然后：

```bash
cd overlay
npm install
```

## 使用方法

### 1. 配置 Kimi API Key（可选）

如需使用 AI 功能，请在 `backend/config.py` 中配置 Kimi API Key：

```python
KIMI_API_KEY = "sk-kimi-xxxxxxxxxxxxxxxx"
ENABLE_AI = True
```

### 2. 启动后端服务

**使用脚本（推荐）**：
```bash
start_backend.bat
```

**或手动启动**：
```bash
cd e:\Project\CardMaster\hearth_stone_dude
.\venv\Scripts\Activate.ps1  # PowerShell
# 或
venv\Scripts\activate.bat    # CMD

python -m backend.api_server
```

后端服务将在 `http://localhost:8000` 启动。

### 3. 启动前端覆盖层

**使用脚本（推荐）**：
```bash
start_overlay.bat
```

**或手动启动**：
```bash
cd e:\Project\CardMaster\hearth_stone_dude\overlay
npm start
```

### 4. 开始游戏

启动炉石传说游戏，记牌器将自动：
- 监控 Power.log 文件
- 解析游戏数据
- 通过覆盖层显示实时信息

### 虚拟环境说明

- **虚拟环境位置**：`e:\Project\CardMaster\hearth_stone_dude\venv`
- **占用空间**：约 200-500MB，具体取决于依赖包数量
- **删除环境**：直接删除 `venv` 文件夹即可完全清理
- **重新创建**：随时可以重新创建虚拟环境，不会影响代码
- **磁盘占用**：如果项目在 E 盘，虚拟环境也会在 E 盘，不会占用 C 盘空间

## 功能特性

### Phase 1: 核心记牌功能

- ✅ 自动定位并监控 Power.log 文件
- ✅ 实时解析炉石传说游戏日志
- ✅ 跟踪双方手牌数量
- ✅ 跟踪双方牌库剩余卡牌数
- ✅ 显示对手已出卡牌
- ✅ 显示我方手牌信息
- ✅ 透明覆盖层窗口，支持点击穿透
- ✅ WebSocket 实时数据推送
- ✅ HTTP API 查询当前状态

### Phase 2: AI 增强功能

- ✅ 卡组识别与匹配
- ✅ 对手卡组推测
- ✅ 剩余关键卡牌预警
- ✅ Kimi AI 集成
- ✅ 智能出牌建议
- ✅ 局势分析与策略建议
- ✅ 事件驱动的 AI 触发

## API 接口

### WebSocket 连接

```
ws://localhost:8000/ws
```

实时推送游戏状态更新，包含 AI 分析数据。

### HTTP 状态查询

```
GET http://localhost:8000/api/status
```

返回当前游戏状态的 JSON 数据。

## 配置

日志文件路径默认位置（Windows）：
```
%LOCALAPPDATA%\Blizzard\Hearthstone\Logs\Power.log
```

如需修改路径或 AI 设置，请编辑 `backend/config.py`。

## 注意事项

1. 确保炉石传说已启用日志记录
2. 首次使用建议先启动后端再启动前端
3. 覆盖层窗口默认位于屏幕右侧，可在 `overlay/main.js` 中调整位置
4. AI 功能需要网络连接和有效的 Kimi API Key
5. 可通过 `ENABLE_AI` 开关控制 AI 功能的启用/禁用

## 许可证

MIT License
