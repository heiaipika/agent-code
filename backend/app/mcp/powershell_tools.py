import subprocess
import time
import psutil
import os
import pyautogui
from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP()

def run_powershell_command(command: str, capture_output: bool = True):
    """execute PowerShell command"""
    try:
        cmd = ["powershell", "-Command", command]
        if capture_output:
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        else:
            result = subprocess.run(cmd, shell=True)
            return "", "", result.returncode
    except Exception as e:
        return "", str(e), 1

def get_powershell_processes():
    """get all PowerShell processes"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'powershell' in proc.info['name'].lower():
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': proc.info['cmdline']
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes

def activate_powershell_window():
    """activate PowerShell window"""
    try:
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        windows = pyautogui.getWindowsWithTitle('Windows PowerShell')
        if not windows:
            windows = pyautogui.getWindowsWithTitle('PowerShell')
        
        if windows:
            window = windows[0]
            window.activate()
            time.sleep(0.5)
            return True
        else:
            pyautogui.hotkey('alt', 'tab')
            time.sleep(0.5)
            return False
    except Exception as e:
        print(f"Failed to activate PowerShell window: {e}")
        return False


@mcp.tool(name="get_powershell_processes", description="Get all PowerShell process information")
def get_all_powershell_processes() -> str:
    """Get list of all running PowerShell processes"""
    try:
        processes = get_powershell_processes()
        if not processes:
            return "No PowerShell processes currently running"

        result = "PowerShell Process List:\n"
        for proc in processes:
            result += f"PID: {proc['pid']}, Name: {proc['name']}\n"
        return result
    except Exception as e:
        return f"Failed to get PowerShell processes: {str(e)}"

@mcp.tool(name="close_powershell", description="close all PowerShell processes")
def close_all_powershell() -> str:
    """close all PowerShell processes"""
    try:
        processes = get_powershell_processes()
        
        if not processes:
            return "can't find PowerShell process to close"
        
        closed_count = 0
        for proc_info in processes:
            try:
                proc = psutil.Process(proc_info['pid'])
                proc.terminate()
                closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return f"successfully closed {closed_count} PowerShell processes"
    except Exception as e:
        return f"Failed to close PowerShell processes: {str(e)}"

@mcp.tool(name="open_powershell", description="Open new PowerShell window")
def open_new_powershell(working_directory:
    Annotated[str, Field(description="Optional working directory, empty for current directory", examples="C:\\Users")] = "") -> str:
    """Open new PowerShell window"""
    try:
        if working_directory and os.path.exists(working_directory):
            # Open PowerShell in specified directory
            command = f'Start-Process powershell -WorkingDirectory "{working_directory}"'
        else:
            # Open PowerShell in current directory
            command = 'Start-Process powershell'

        stdout, stderr, returncode = run_powershell_command(command, capture_output=False)

        if returncode != 0 and stderr:
            return f"Failed to open PowerShell: {stderr}"

        time.sleep(2)  # Wait for window to open
        processes = get_powershell_processes()
        return f"PowerShell opened, current running processes: {len(processes)}"
    except Exception as e:
        return f"close PowerShell process failed: {str(e)}"

@mcp.tool(name="run_powershell_script", description="Send commands to PowerShell window via pyautogui")
def run_powershell_script(script: 
    Annotated[str, Field(description="Script command to execute in PowerShell window", examples="Get-Location")]) -> str:
    """Send command to active PowerShell window via pyautogui"""
    try:
        print("-" * 50)
        print("run_powershell_script (pyautogui):")
        print(script)
        print("-" * 50)
        
        processes = get_powershell_processes()
        if not processes:
            return "can't find running PowerShell process,please open PowerShell window first."
        
        if not activate_powershell_window():
            return "can't activate PowerShell window,please ensure PowerShell window is open and visible."
        
        pyautogui.hotkey('ctrl', 'c') 
        time.sleep(0.2)
        
        pyautogui.press('end')
        time.sleep(0.1)
        
        pyautogui.write(script, interval=0.02)
        time.sleep(0.3)
        
        pyautogui.press('enter')
        
        return f"command has been sent to PowerShell window: {script}"
    except Exception as e:
        return f"send PowerShell command failed:{str(e)}"

if __name__ == '__main__':
    mcp.run(transport="stdio")

