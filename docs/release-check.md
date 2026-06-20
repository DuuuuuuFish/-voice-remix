# 发布前检查

## 扫描范围

- TODO
- FIXME
- pass
- NotImplementedError
- 调试打印
- 临时日志
- 本地依赖
- 个人路径

## 当前处理原则

- 第三方模型源码中的 `NotImplementedError`、`pass` 不直接删除，避免破坏上游逻辑
- 当前交付目录不保留 `.venv`、`node_modules`、`.next`、数据库、上传文件、生成音频
- 本机路径不写入启动脚本和 README

## 已知保留项

- `backend/app/db/base.py` 中 `pass`：SQLAlchemy DeclarativeBase 空类实现
- `backend/app/schemas/history.py` 中 `pass`：类型继承占位
- `backend/app/services/voice_engine.py` 中 `NotImplementedError`：抽象基类定义
