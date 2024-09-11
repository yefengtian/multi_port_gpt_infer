import subprocess
import logging
import time
import os
import argparse
import json
import psutil
import signal
from concurrent.futures import ThreadPoolExecutor


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 端口和文件名的字典
PORT_FILE_DICT = {
    "30015": "/Users/darry/workspace/proj/label_tools/33wdata/output_files/output_1.txt",
    "30019": "/Users/darry/workspace/proj/label_tools/33wdata/output_files/output_2.txt"
    # ... 其他端口和文件
}

STATUS_FILE = "port_status.json"
PROCESS_FILE = "port_processes.json"

def setup_logging(log_folder):
    os.makedirs(log_folder, exist_ok=True)
    file_handler = logging.FileHandler(os.path.join(log_folder, 'multi_sh_kill_script.log'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

def run_script(port, script_file, log_folder, output_folder):
    logger.info(f"Starting script for port {port} with file {script_file}")
    
    # 清理旧的状态
    kill_process(port)
    
    command = f"python /Users/darry/workspace/proj/label_tools/sxp_format/template_new.py {port} {script_file} --log_folder {log_folder} --output_folder {output_folder}"
    print(f"Running command: {command}")
    
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    save_process_id(port, process.pid)
    update_status(port, "Running")
    
    return process

def monitor_process(port, process):
    stdout, stderr = process.communicate()
    rc = process.returncode
    
    if stdout:
        logger.info(f"Port {port} stdout: {stdout}")
    if stderr:
        logger.error(f"Port {port} stderr: {stderr}")
    
    if rc == 0:
        status = "Completed"
    elif rc < 0:
        status = f"Terminated (Signal: {-rc})"
    else:
        status = f"Failed (RC: {rc})"
    
    update_status(port, status)
    logger.info(f"Script for port {port} completed with status: {status}")
    
    # 清理进程信息
    remove_process_id(port)
    
    return rc


def update_status(port, status):
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            status_dict = json.load(f)
    else:
        status_dict = {}
    
    status_dict[port] = status
    
    with open(STATUS_FILE, 'w') as f:
        json.dump(status_dict, f)

def get_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_process_id(port, pid):
    if os.path.exists(PROCESS_FILE):
        with open(PROCESS_FILE, 'r') as f:
            process_dict = json.load(f)
    else:
        process_dict = {}
    
    process_dict[port] = pid
    
    with open(PROCESS_FILE, 'w') as f:
        json.dump(process_dict, f)

def remove_process_id(port):
    if os.path.exists(PROCESS_FILE):
        with open(PROCESS_FILE, 'r') as f:
            process_dict = json.load(f)
        if port in process_dict:
            del process_dict[port]
        with open(PROCESS_FILE, 'w') as f:
            json.dump(process_dict, f)

def kill_process(port):
    if os.path.exists(PROCESS_FILE):
        with open(PROCESS_FILE, 'r') as f:
            process_dict = json.load(f)
        
        if port in process_dict:
            pid = process_dict[port]
            try:
                process = psutil.Process(pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
                logger.info(f"Process for port {port} (PID: {pid}) has been terminated.")
                update_status(port, "Terminated")
                remove_process_id(port)
            except psutil.NoSuchProcess:
                logger.info(f"Process for port {port} (PID: {pid}) no longer exists.")
                update_status(port, "Not Running")
                remove_process_id(port)
            except Exception as e:
                logger.error(f"Error killing process for port {port}: {str(e)}")
        else:
            logger.info(f"No running process found for port {port}")
            update_status(port, "Not Running")
    else:
        logger.info("No process information available")

def kill_all_processes():
    if os.path.exists(PROCESS_FILE):
        with open(PROCESS_FILE, 'r') as f:
            process_dict = json.load(f)
        
        for port, pid in process_dict.items():
            try:
                process = psutil.Process(pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
                logger.info(f"Process for port {port} (PID: {pid}) has been terminated.")
                update_status(port, "Terminated")
            except psutil.NoSuchProcess:
                logger.info(f"Process for port {port} (PID: {pid}) no longer exists.")
                update_status(port, "Not Running")
            except Exception as e:
                logger.error(f"Error killing process for port {port}: {str(e)}")
        
        os.remove(PROCESS_FILE)
    else:
        logger.info("No process information available")

def check_process_status():
    if os.path.exists(PROCESS_FILE):
        with open(PROCESS_FILE, 'r') as f:
            process_dict = json.load(f)
        for port, pid in list(process_dict.items()):
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    update_status(port, "Running")
                else:
                    update_status(port, "Not Running")
                    remove_process_id(port)
            except psutil.NoSuchProcess:
                update_status(port, "Not Running")
                remove_process_id(port)

# def main(ports=None, log_folder='logs', output_folder='outputs', kill_ports=None):
#     setup_logging(log_folder)
    
#     if kill_ports:
#         for port in kill_ports:
#             kill_process(port)
#         return

#     check_process_status()  # 检查所有进程的状态

#     if ports is None:
#         ports = list(PORT_FILE_DICT.keys())
    
#     os.makedirs(log_folder, exist_ok=True)
#     os.makedirs(output_folder, exist_ok=True)
    
#     processes = {}
#     for port in ports:
#         if port not in PORT_FILE_DICT:
#             logger.error(f"Invalid port: {port}")
#             continue
        
#         script_file = PORT_FILE_DICT[port]
#         print(f"Starting script for port {port} with file {script_file}")
#         process = run_script(port, script_file, log_folder, output_folder)
#         processes[port] = process
    
#     # 等待所有进程完成
#     with ThreadPoolExecutor(max_workers=len(processes)) as executor:
#         futures = {executor.submit(monitor_process, port, process): port for port, process in processes.items()}
#         for future in futures:
#             port = futures[future]
#             try:
#                 future.result()
#             except Exception as e:
#                 logger.error(f"Error in script for port {port}: {str(e)}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Run scripts for specified ports')
#     parser.add_argument('ports', nargs='*', help='Ports to run scripts for')
#     parser.add_argument('--status', action='store_true', help='Show status of all ports')
#     parser.add_argument('--log_folder', type=str, default='logs', help='Folder to store log files')
#     parser.add_argument('--output_folder', type=str, default='outputs', help='Folder to store output files')
#     parser.add_argument('--kill', nargs='+', help='Kill processes for specified ports')
#     parser.add_argument('--kill-all', action='store_true', help='Kill all running processes')
#     args = parser.parse_args()

#     if args.status:
#         check_process_status()  # 在显示状态之前检查进程状态
#         status = get_status()
#         for port, state in status.items():
#             print(f"Port {port}: {state}")
#     elif args.kill:
#         for port in args.kill:
#             kill_process(port)
#     elif args.kill_all:
#         kill_all_processes()
#     else:
#         main(args.ports, args.log_folder, args.output_folder)

#     print("All operations completed.", flush=True)


def main(ports=None, log_folder='logs', output_folder='outputs', kill_ports=None):
    setup_logging(log_folder)
    
    if kill_ports:
        for port in kill_ports:
            kill_process(port)
        return

    check_process_status()  # 检查所有进程的状态

    if ports is None or len(ports) == 0:
        ports = list(PORT_FILE_DICT.keys())
    
    if len(ports) == 0:
        logger.warning("No ports specified and no ports configured in PORT_FILE_DICT. Nothing to do.")
        return

    os.makedirs(log_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    
    processes = {}
    for port in ports:
        if port not in PORT_FILE_DICT:
            logger.error(f"Invalid port: {port}")
            continue
        
        script_file = PORT_FILE_DICT[port]
        print(f"Starting script for port {port} with file {script_file}")
        process = run_script(port, script_file, log_folder, output_folder)
        processes[port] = process
    
    # 等待所有进程完成
    if processes:
        with ThreadPoolExecutor(max_workers=len(processes)) as executor:
            futures = {executor.submit(monitor_process, port, process): port for port, process in processes.items()}
            for future in futures:
                port = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"Error in script for port {port}: {str(e)}")
    else:
        logger.warning("No valid ports to process.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run scripts for specified ports')
    parser.add_argument('ports', nargs='*', help='Ports to run scripts for')
    parser.add_argument('--status', action='store_true', help='Show status of all ports')
    parser.add_argument('--log_folder', type=str, default='logs', help='Folder to store log files')
    parser.add_argument('--output_folder', type=str, default='outputs', help='Folder to store output files')
    parser.add_argument('--kill', nargs='+', help='Kill processes for specified ports')
    parser.add_argument('--kill-all', action='store_true', help='Kill all running processes')
    args = parser.parse_args()

    if args.status:
        check_process_status()  # 在显示状态之前检查进程状态
        status = get_status()
        for port, state in status.items():
            print(f"Port {port}: {state}")
    elif args.kill:
        for port in args.kill:
            kill_process(port)
    elif args.kill_all:
        kill_all_processes()
    else:
        main(args.ports, args.log_folder, args.output_folder)

    print("All operations completed.", flush=True)