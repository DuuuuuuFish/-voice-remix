# 声音复刻

基于 Next.js、FastAPI 与 CosyVoice2 的多语言零样本声音克隆平台交付版。该目录是从原始项目复制出的独立交付副本，后续整理、脚本、文档与发布准备工作仅在此目录内完成，原项目保持不变。

## 1. 项目简介

用户上传 5 到 30 秒参考音频后，可以创建说话人音色，并生成中文、英文、日文、韩文、法文、德文、西班牙文语音。当前版本保留原始业务链路，包括上传、音色创建、语音生成、历史记录、播放器试听和音频下载。

## 2. 功能介绍

- 上传参考音频
- 创建音色
- 语音生成
- 多语言生成
- Voice Mixing
- Emotion Control
- 历史记录
- 播放器试听
- 下载音频
- 音色管理

## 3. 技术架构

- 前端：Next.js 15 + TypeScript
- 后端：FastAPI + Python
- 语音模型：CosyVoice2
- 数据库：SQLite（默认）/ PostgreSQL（可扩展）
- 文件存储：本地存储

## 4. 目录结构

```text
声音复刻/
├─ backend/
├─ frontend/
├─ scripts/
├─ docs/
├─ .gitignore
├─ .env.example
├─ README.md
├─ install.bat
├─ start.bat
├─ stop.bat
└─ launch_voice_clone.bat
```

## 5. 安装步骤

1. 安装 Python 3.10+
2. 安装 Node.js 20+
3. 双击 `install.bat`

安装脚本会：
- 检查 Python
- 检查 Node.js
- 安装后端依赖
- 安装前端依赖
- 创建必要目录
- 初始化数据库

## 6. 启动步骤

双击：

```text
start.bat
```

它会：
- 启动后端
- 启动前端
- 等待服务就绪
- 自动打开浏览器首页

停止服务请双击：

```text
stop.bat
```

## 7. 常见问题

### 上传 m4a 失败

当前版本优先使用系统 ffmpeg。若系统未安装 ffmpeg，会退回 PyAV 解码。若仍失败，请优先确认音频文件本身可播放。

### 生成时自动断句

当前版本已支持用户手动控制断句：在文本框中换行，每一行都会作为单独片段生成。

### 页面打不开

确认：
- 前端端口默认 `3000`
- 后端端口默认 `8000`
- 未被其他程序占用

## 8. Windows 部署

推荐直接使用：
- `install.bat`
- `start.bat`
- `stop.bat`

自动启动请参考：
- [docs/auto-start.md](./docs/auto-start.md)

## 9. GitHub 发布

发布前请确认：
- 不提交 `.env`
- 不提交 `node_modules`
- 不提交 `.venv`
- 不提交本地日志、数据库、模型缓存与生成音频

本仓库已经提供 `.gitignore` 规则用于过滤这些内容。

## 10. 后续扩展说明

可继续扩展：
- MinIO / S3 存储
- PostgreSQL 生产配置
- Windows Service 自动运行
- 转写后台任务监控
- 更多语言和情绪控制能力

## 当前默认环境变量

参考根目录 `.env.example`：

- `API_HOST`
- `API_PORT`
- `FRONTEND_PORT`
- `DATABASE_URL`
- `VOICE_ENGINE`
- `MODEL_PATH`
- `WHISPER_MODEL_PATH`
- `STORAGE_PATH`
- `NEXT_PUBLIC_API_BASE_URL`

即使没有 `.env`，项目也会使用合理默认值启动。

## 安装结果说明

`install.bat` 完成后：
- `backend/.venv` 会创建成功
- 前端依赖会被安装
- `backend/storage` 会初始化
- 数据库文件会在首次初始化时创建

## 自动启动方式

### 方案 A：NSSM（推荐）

示例脚本：
- [scripts/setup_autostart_nssm.example.bat](./scripts/setup_autostart_nssm.example.bat)

### 方案 B：Windows Startup

示例脚本：
- [scripts/setup_startup_folder.example.bat](./scripts/setup_startup_folder.example.bat)

两种方案都只保留示例脚本和说明，不包含任何本机写死路径。
