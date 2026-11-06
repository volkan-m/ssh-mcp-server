#!/usr/bin/env python3
"""
SSH MCP Server - Secure Remote Command Execution
==============================================
"""

import os
import re
import paramiko
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ssh-tools")

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

ALLOWED_COMMANDS = [
    # Systemd services
    r"^systemctl (status|restart|stop|start|enable|disable|is-active|is-enabled)( [a-zA-Z0-9_.@-]+)?$",
    
    # Log viewing
    r"^journalctl -u [a-zA-Z0-9_.@-]+ -n \d+$",
    r"^journalctl -u [a-zA-Z0-9_.@-]+ --since .+$",
    r"^journalctl -n \d+( --no-pager)?$",
    r"^tail -n \d+ /[a-zA-Z0-9_./\-]+$",
    
    # System status
    r"^df -h$",
    r"^free -h$",
    r"^uptime$",
    r"^top -bn1$",
    r"^htop -n 1 --no-color$",
    r"^vmstat$",
    r"^iostat$",
    
    # Docker/Container management
    r"^docker ps( -a)?$",
    r"^docker logs [a-zA-Z0-9_.-]+ --tail \d+$",
    r"^docker stats --no-stream$",
    r"^docker-compose -f [a-zA-Z0-9_./\-]+ ps$",
    r"^docker-compose -f [a-zA-Z0-9_./\-]+ (up|down|restart)( -d)?$",
    r"^docker (restart|stop|start|inspect)( .*)? [a-zA-Z0-9_.-]+$",
    
    # Process management
    r"^ps aux \| grep [a-zA-Z0-9_.-]+$",
    r"^pgrep -l [a-zA-Z0-9_.-]+$",
    
    # Network
    r"^netstat -tuln$",
    r"^ss -tuln$",
    r"^ip a$",
    r"^ip route$",
    r"^curl -I https?://[a-zA-Z0-9._/:-]+$",
    r"^curl https?://[a-zA-Z0-9._/:-]+$",
    
    # File system (Read-only)
    r"^ls -lah( /[a-zA-Z0-9_./\-]+)?$",
    r"^cat /[a-zA-Z0-9_./\-]+$",
    r"^head -n \d+ /[a-zA-Z0-9_./\-]+$",
    r"^find /[a-zA-Z0-9_./\-]+ -type f -name .+$",
    
    # Git operations (Read-only)
    r"^git -C /[a-zA-Z0-9_./\-]+ status$",
    r"^git -C /[a-zA-Z0-9_./\-]+ log -n \d+$",
    r"^git -C /[a-zA-Z0-9_./\-]+ diff$",
    r"^git -C /[a-zA-Z0-9_./\-]+ branch$",

    # UFW Firewall management
    r"^ufw status( numbered| verbose)?$",
    r"^ufw allow \d+/(tcp|udp)$",
    r"^ufw allow from [\d./]+ to any port \d+ proto (tcp|udp)$",
    r"^ufw deny \d+/(tcp|udp)$",
    r"^ufw delete allow \d+/(tcp|udp)$",
    r"^ufw reload$",

    # General info
    r"^echo 'SSH Connection OK' && uname -a$",
    r"^uname -a$",
    r"^hostname$",
]

# SSH connection info (read from environment variables)
SSH_HOST = os.environ.get("SSH_HOST", "")
SSH_USER = os.environ.get("SSH_USER", "root")
SSH_KEY = os.environ.get("SSH_KEY", os.path.expanduser("~/.ssh/ai_runner"))
SSH_PASSWORD = os.environ.get("SSH_PASSWORD", "")
SSH_PORT = os.environ.get("SSH_PORT", "22")
COMMAND_TIMEOUT = int(os.environ.get("COMMAND_TIMEOUT", "30"))

def is_allowed(cmd: str) -> bool:
    cmd = cmd.strip()
    return any(re.match(pattern, cmd) for pattern in ALLOWED_COMMANDS)

def validate_config() -> Optional[str]:
    if not SSH_HOST:
        return "SSH_HOST environment variable is not defined!"
    if not SSH_PASSWORD and not os.path.exists(SSH_KEY):
        return f"Neither SSH_PASSWORD nor valid SSH_KEY ({SSH_KEY}) is provided!"
    return None

def execute_ssh_command(command: str) -> tuple[int, str, str]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    connect_kwargs = {
        "hostname": SSH_HOST,
        "port": int(SSH_PORT),
        "username": SSH_USER,
        "timeout": 15,
    }
    if SSH_PASSWORD:
        connect_kwargs["password"] = SSH_PASSWORD
    elif os.path.exists(SSH_KEY):
        connect_kwargs["key_filename"] = SSH_KEY
        
    client.connect(**connect_kwargs)
    stdin, stdout, stderr = client.exec_command(command, timeout=COMMAND_TIMEOUT)
    exit_code = stdout.channel.recv_exit_status()
    out_str = stdout.read().decode('utf-8', errors='replace')
    err_str = stderr.read().decode('utf-8', errors='replace')
    client.close()
    return exit_code, out_str, err_str

@mcp.tool()
def ssh_exec(command: str) -> str:
    config_error = validate_config()
    if config_error:
        return f"❌ CONFIG ERROR: {config_error}"
    
    command = command.strip()
    if not is_allowed(command):
        return f"❌ DENIED: Command is not in the allowlist!\n\nCommand: {command}"
    
    try:
        exit_code, stdout, stderr = execute_ssh_command(command)
        output = f"✅ Command: {command}\n"
        output += f"Host: {SSH_USER}@{SSH_HOST}\n"
        output += f"Exit Code: {exit_code}\n\n"
        if stdout:
            output += "=== STDOUT ===\n" + stdout
        if stderr:
            output += "\n=== STDERR ===\n" + stderr
        return output
    except Exception as e:
        return f"❌ EXCEPTION: {type(e).__name__}: {str(e)}"

@mcp.tool()
def ssh_list_allowed() -> str:
    output = "📋 Permitted Command Patterns:\n" + "=" * 60 + "\n\n"
    for i, pattern in enumerate(ALLOWED_COMMANDS, 1):
        output += f"{i:2d}. {pattern}\n"
    output += "\n" + "=" * 60 + "\n"
    return output

@mcp.tool()
def ssh_test_connection() -> str:
    config_error = validate_config()
    if config_error:
        return f"❌ CONFIG ERROR: {config_error}"
    
    try:
        exit_code, stdout, stderr = execute_ssh_command("uname -a && hostname")
        if exit_code == 0:
            output = "✅ SSH CONNECTION SUCCESSFUL!\n\n"
            output += f"Host: {SSH_HOST}:{SSH_PORT}\n"
            output += f"User: {SSH_USER}\n\n"
            output += "Server Info:\n" + stdout
            return output
        else:
            return f"❌ CONNECTION FAILED!\n\nExit Code: {exit_code}\n\n{stderr}"
    except Exception as e:
        return f"❌ EXCEPTION: {type(e).__name__}: {str(e)}"

@mcp.tool()
def ssh_get_config() -> str:
    output = "⚙️  SSH MCP Server Configuration:\n" + "=" * 60 + "\n\n"
    output += f"SSH_HOST: {SSH_HOST}\n"
    output += f"SSH_USER: {SSH_USER}\n"
    output += f"SSH_PORT: {SSH_PORT}\n"
    output += f"SSH_PASSWORD: {'******' if SSH_PASSWORD else 'None'}\n"
    output += f"SSH_KEY: {SSH_KEY if os.path.exists(SSH_KEY) else 'None'}\n"
    return output

if __name__ == "__main__":
    mcp.run()
