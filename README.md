# 单词本应用

一个跨平台的单词学习应用，支持PC端（Windows/Linux）和安卓端，可以通过WiFi或蓝牙进行数据同步。

## 功能特性

- **PC端功能**（Python + CustomTkinter）
  - 单词的增删查改操作
  - 自动查询单词释义（中英文）
  - 随机单词卡片模式
  - WiFi/蓝牙数据同步服务器
  - 单词搜索功能

- **安卓端功能**（Python + Kivy）
  - 随机单词卡片学习
  - 单词列表查看
  - WiFi数据同步客户端
  - 离线学习支持

- **数据同步**
  - WiFi网络同步
  - 蓝牙设备同步
  - 本地数据库存储

## 项目结构

```
word_book/
├── pc_app/                 # PC端应用
│   ├── main.py            # 主程序入口
│   ├── gui/               # GUI界面
│   │   └── main_window.py # 主窗口
│   ├── database/          # 数据库操作
│   │   └── database.py    # 数据库管理
│   ├── api/               # 单词查询API
│   │   └── dictionary_api.py # 词典API
│   └── sync/              # 数据同步模块
│       ├── wifi_sync.py   # WiFi同步
│       └── bluetooth_sync.py # 蓝牙同步
├── android_app/           # 安卓端应用
│   ├── main.py            # 主程序
│   ├── sync/              # 同步客户端
│   │   └── sync_client.py
│   └── buildozer.spec     # 安卓打包配置
├── shared/                # 共享模块
│   ├── models.py          # 数据模型
│   └── protocols.py       # 通信协议
└── requirements.txt       # 依赖包
```

## 安装运行

### PC端运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行PC端应用：
```bash
cd pc_app
python main.py
```

### 安卓端打包

1. 安装Buildozer：
```bash
pip install buildozer
```

2. 打包APK：
```bash
cd android_app
buildozer android debug
```

## 使用说明

### PC端使用

1. **添加单词**：在侧边栏点击"添加单词"，输入单词后点击"自动查询"获取翻译
2. **单词列表**：查看、编辑、删除已添加的单词
3. **单词卡**：随机抽取单词进行学习，支持翻面查看详细信息
4. **数据同步**：启动WiFi或蓝牙同步服务，供安卓端连接

### 安卓端使用

1. **同步数据**：点击"同步数据"，输入PC端IP地址进行WiFi同步
2. **单词卡学习**：翻面查看单词详细信息，点击"下一个"切换单词
3. **单词列表**：查看所有已同步的单词

## 技术特点

- **跨平台**：PC端支持Windows和Linux，安卓端可打包成APK
- **本地存储**：数据存储在PC端，无需云服务
- **多种同步**：支持WiFi和蓝牙两种同步方式
- **自动查词**：集成多个词典API进行自动查询
- **学习模式**：随机单词卡片，支持正反面切换

## 依赖说明

- `customtkinter`: PC端现代化GUI界面
- `kivy`: 安卓端跨平台GUI框架
- `sqlite3`: 本地数据库存储
- `requests`: HTTP请求库（用于词典API）
- `pybluez`: 蓝牙通信库
- `plyer`: 移动端平台API访问