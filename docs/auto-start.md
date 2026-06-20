# 自动启动方案

## 方案 A：NSSM（推荐）

适用于需要稳定后台启动的 Windows 环境。

1. 安装 [NSSM](https://nssm.cc/).
2. 为后端创建服务：
   - Program: `cmd.exe`
   - Arguments: `/c start.bat`
   - Startup directory: 项目根目录
3. 服务创建后，设置为 `Automatic`.
4. 首次测试成功后再启用开机自启动。

注意：
- 不要把当前电脑的用户名、桌面路径写死进服务配置。
- GitHub 仓库中只保留脚本和说明，不提交实际服务配置文件。

## 方案 B：Windows Startup

适用于个人电脑或轻量使用场景。

1. 在启动文件夹中创建快捷方式：
   - 目标：`launch_voice_clone.bat`
2. 重启后会自动执行 `start.bat`.

常见启动文件夹：
- 当前用户：`shell:startup`
- 全局：`shell:common startup`

注意：
- 仓库中不要提交任何本机启动项或快捷方式文件。
- 只保留脚本与文档说明。
