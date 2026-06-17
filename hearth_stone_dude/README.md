# 炉石传说记牌器 (HearthStone Dude)

一个基于 python-hslog 的炉石传说记牌器，提供实时游戏状态跟踪和透明覆盖层显示。

## 项目结构

```
hearth_stone_dude/
├── backend/                 # Python 后端
│   ├── __init__.py
│   ├── config.py           # 配置文件
│   ├── log_monitor.py      # 日志监控模块
│   ├── game_state.py       # 游戏状态跟踪
│   ├── card_tracker.py     # 卡牌跟踪核心逻辑
│   └── api_server.py       # FastAPI 服务
├── overlay/                # Electron 前端覆盖层
│   ├── package.json
│   ├── main.js            # Electron 主进程
│   ├── index.html         # 覆盖层界面
│   ├── renderer.js        # 渲染进程逻辑
│   └── styles.css         # 样式文件
├── data/                   # 数据目录
│   └── decks/             # 卡组数据
├── requirements.txt       # Python 依赖
└── README.md
```

## 技术栈

- **后端**: Python + FastAPI + WebSocket
- **日志解析**: python-hslog
- **前端**: Electron + HTML/CSS/JavaScript
- **文件监控**: watchdog

## 安装步骤

### 1. 后端安装

确保已安装 Python 3.8+，然后：

```bash
cd hearth_stone_dude
pip install -r requirements.txt
```

### 2. 前端安装

确保已安装 Node.js 和 npm，然后：

```bash
cd overlay
npm install
```

## 使用方法

### 1. 启动后端服务

```bash
cd hearth_stone_dude
python -m backend.api_server
```

后端服务将在 `http://localhost:8000` 启动。

### 2. 启动前端覆盖层

打开新的终端窗口：

```bash
cd hearth_stone_dude/overlay
npm start
```

### 3. 开始游戏

启动炉石传说游戏，记牌器将自动：
- 监控 Power.log 文件
- 解析游戏数据
- 通过覆盖层显示实时信息

## 功能特性

### 已实现功能 (Phase 1)

- ✅ 自动定位并监控 Power.log 文件
- ✅ 实时解析炉石传说游戏日志
- ✅ 跟踪双方手牌数量
- ✅ 跟踪双方牌库剩余卡牌数
- ✅ 显示对手已出卡牌
- ✅ 显示我方手牌信息
- ✅ 透明覆盖层窗口，支持点击穿透
- ✅ WebSocket 实时数据推送
- ✅ HTTP API 查询当前状态

### 计划功能 (Phase 2)

- 📋 卡组匹配与推测
- 📋 AI 出牌建议
- 📋 历史游戏记录
- 📋 卡组数据分析
- 📋 更多游戏状态信息

## API 接口

### WebSocket 连接

```
ws://localhost:8000/ws
```

实时推送游戏状态更新。

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

如需修改路径，请编辑 `backend/config.py`。

## 注意事项

1. 确保炉石传说已启用日志记录
2. 首次使用建议先启动后端再启动前端
3. 覆盖层窗口默认位于屏幕右侧，可在 `overlay/main.js` 中调整位置

## 许可证

MIT License
