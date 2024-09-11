
# `run_multi_sh_kill_script.sh` 使用说明

本项目包含一个 `run_multi_sh_kill_script.sh` 脚本，用于管理多个后台进程的启动与终止。以下是一些常见的使用场景和调用示例。

## 使用示例

### 1. 启动指定端口的脚本（后台运行）
```bash
./run_multi_sh_kill_script.sh 30015 30019
```

### 2. 启动所有配置的端口（后台运行）
```bash
./run_multi_sh_kill_script.sh
```

### 3. 指定日志和输出文件夹（后台运行）
```bash
./run_multi_sh_kill_script.sh 30015 30019 --log_folder custom_logs --output_folder custom_outputs
```

### 4. 查看所有端口的状态
```bash
python multi_sh_kill_script.py --status
```

### 5. 终止特定端口的进程
```bash
python multi_sh_kill_script.py --kill 30015
```

### 6. 终止所有正在运行的进程
```bash
python multi_sh_kill_script.py --kill-all
```

### 7. 停止后台运行的主脚本
```bash
kill $(cat script.pid)
```

### 8. 查看后台运行的输出
```bash
tail -f nohup.out
```

### 9. 在不同的日志文件夹中启动多个实例（后台运行）
```bash
./run_multi_sh_kill_script.sh 30015 30019 --log_folder logs_instance1 --output_folder outputs_instance1
./run_multi_sh_kill_script.sh 30020 30021 --log_folder logs_instance2 --output_folder outputs_instance2
```

### 10. 启动脚本并立即切换到后台
```bash
./run_multi_sh_kill_script.sh 30015 30019 &
```

### 11. 使用特定的 Python 解释器运行

修改 `run_multi_sh_kill_script.sh`：

```bash
#!/bin/bash
nohup /path/to/your/python multi_sh_kill_script.py "$@" > nohup.out 2>&1 &
echo $! > script.pid
echo "Script started with PID $(cat script.pid)"
```

然后正常调用：
```bash
./run_multi_sh_kill_script.sh 30015 30019
```

### 12. 在后台运行并将输出重定向到自定义文件

修改 `run_multi_sh_kill_script.sh`：

```bash
#!/bin/bash
nohup python multi_sh_kill_script.py "$@" > custom_output.log 2>&1 &
echo $! > script.pid
echo "Script started with PID $(cat script.pid)"
```

然后正常调用：
```bash
./run_multi_sh_kill_script.sh 30015 30019
```

### 13. 使用 `nice` 命令调整进程优先级（较低优先级）

修改 `run_multi_sh_kill_script.sh`：

```bash
#!/bin/bash
nohup nice -n 10 python multi_sh_kill_script.py "$@" > nohup.out 2>&1 &
echo $! > script.pid
echo "Script started with PID $(cat script.pid)"
```

然后正常调用：
```bash
./run_multi_sh_kill_script.sh 30015 30019
```

## 注意事项

- `run_multi_sh_kill_script.sh` 启动的脚本会在后台运行，即使关闭终端也不会影响其执行。
- 使用 `kill $(cat script.pid)` 可以停止后台进程，或使用 `multi_sh_kill_script.py` 提供的 `--kill` 和 `--kill-all` 选项来终止进程。
- 通过 `tail -f nohup.out` 可以查看后台运行脚本的实时输出日志。

```markdown
## 其他使用技巧

### 1. 更改端口号范围
如果你需要启动的脚本监听不同的端口号，你可以直接修改调用参数。例如：
```bash
./run_multi_sh_kill_script.sh 30025 30030
```
这将启动监听端口 30025 到 30030 的脚本。

### 2. 自定义日志文件名称
通过修改脚本，将日志文件的输出定向到你想要的自定义日志文件。例如：
```bash
./run_multi_sh_kill_script.sh 30015 30019 --log_folder logs_instance1 --output_folder outputs_instance1
```
将日志和输出文件分别保存在 `logs_instance1` 和 `outputs_instance1` 文件夹中。

### 3. 多实例运行
你可以同时启动多个脚本实例，每个实例在不同的日志文件夹中保存其输出。例如：
```bash
./run_multi_sh_kill_script.sh 30015 30019 --log_folder logs_instance1 --output_folder outputs_instance1
./run_multi_sh_kill_script.sh 30020 30024 --log_folder logs_instance2 --output_folder outputs_instance2
```
这将启动两个实例，分别监听不同的端口范围，且日志和输出文件分别保存到不同的文件夹。

### 4. 调整进程优先级
使用 `nice` 命令可以调整脚本进程的优先级。例如，使用较低的优先级运行脚本：
```bash
nohup nice -n 10 python multi_sh_kill_script.py "$@" > nohup.out 2>&1 &
```
这样可以确保该脚本不会抢占系统过多的资源。

### 5. 手动终止进程
你可以通过以下命令手动终止脚本运行的进程：
```bash
kill $(cat script.pid)
```
如果你想终止所有启动的进程，可以使用 `multi_sh_kill_script.py` 提供的 `--kill-all` 参数：
```bash
python multi_sh_kill_script.py --kill-all
```

### 6. 检查运行状态
如果你想查看哪些端口的脚本仍在运行，可以使用 `--status` 参数：
```bash
python multi_sh_kill_script.py --status
```
这将输出所有当前运行的脚本和它们监听的端口号。

### 7. 查看日志实时输出
你可以使用以下命令实时查看后台脚本的日志输出：
```bash
tail -f nohup.out
```
这将显示 `nohup.out` 中最新的日志信息，帮助你调试和查看运行状态。

## 结语

`run_multi_sh_kill_script.sh` 是一个方便的脚本，适合管理多个 Python 后台进程。你可以通过上述示例快速入门并在各种场景中灵活运用。如果有更多自定义需求，可以根据自己的工作流对脚本进行修改。