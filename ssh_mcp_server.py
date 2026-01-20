#!/usr/bin/env python3
"""
SSH MCP Server - Secure Remote Command Execution
==============================================
This MCP server allows you to securely run commands on a remote Linux server via SSH.
It only executes commands that match a predefined allowlist.

Installation:
    pip install fastmcp

Usage:
    export SSH_HOST="1.2.3.4"
    export SSH_USER="ai-runner"
    export SSH_KEY="$HOME/.ssh/ai_runner"
    python ssh_mcp_server.py
"""

import os
import re
import subprocess
import json
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ssh-tools")

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# Only commands matching these regex patterns can be executed.
# You can expand or restrict this list based on your needs.
ALLOWED_COMMANDS = [
    # Systemd services
    r"^systemctl (status|restart|stop|start|enable|disable|is-active|is-enabled) [a-zA-Z0-9_.@-]+$",
    
    # Log viewing
    r"^journalctl -u [a-zA-Z0-9_.@-]+ -n \d+$",
    r"^journalctl -u [a-zA-Z0-9_.@-]+ --since .+$",
    r"^tail -n \d+ /var/log/[a-zA-Z0-9_./\-]+$",
    
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
    r"^curl -I https?://[a-zA-Z0-9._/:-]+$",
    r"^curl https?://[a-zA-Z0-9._/:-]+$",
    
    # File system (Read-only)
    r"^ls -lah /[a-zA-Z0-9_./\-]+$",
    r"^cat /[a-zA-Z0-9_./\-]+$",
    r"^head -n \d+ /[a-zA-Z0-9_./\-]+$",
    r"^find /[a-zA-Z0-9_./\-]+ -type f -name .+$",
    
    # Git operations (Read-only)
    r"^git -C /[a-zA-Z0-9_./\-]+ status$",
    r"^git -C /[a-zA-Z0-9_./\-]+ log -n \d+$",
    r"^git -C /[a-zA-Z0-9_./\-]+ diff$",
    r"^git -C /[a-zA-Z0-9_./\-]+ branch$",
    
    # Secure write operations (Example - use with caution!)
    # r"^echo .+ > /tmp/[a-zA-Z0-9_.-]+$",
    
    # Custom application commands (Example)
    # r"^/opt/myapp/bin/status\.sh$",
    # r"^pm2 (list|status|logs .+ --lines \d+)$",
]

# SSH connection info (read from environment variables)
SSH_HOST = os.environ.get("SSH_HOST", "")
SSH_USER = os.environ.get("SSH_USER", "ai-runner")
SSH_KEY = os.environ.get("SSH_KEY", os.path.expanduser("~/.ssh/ai_runner"))
SSH_PORT = os.environ.get("SSH_PORT", "22")

# Timeout duration (seconds)
COMMAND_TIMEOUT = int(os.environ.get("COMMAND_TIMEOUT", "30"))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_allowed(cmd: str) -> bool:
    """
    Checks if the command is in the allowlist.
    """
    cmd = cmd.strip()
    return any(re.match(pattern, cmd) for pattern in ALLOWED_COMMANDS)


def validate_config() -> Optional[str]:
    """
    Validates the SSH configuration.
    Returns an error message if invalid, otherwise None.
    """
    if not SSH_HOST:
        return "SSH_HOST environment variable is not defined!"
    
    if not os.path.exists(SSH_KEY):
        return f"SSH key file not found: {SSH_KEY}"
    
    # Check key file permissions (should be 600)
    stat_info = os.stat(SSH_KEY)
    if stat_info.st_mode & 0o777 != 0o600:
        return f"SSH key file permissions are not secure! Run 'chmod 600 {SSH_KEY}'."
    
    return None


# ============================================================================
# MCP TOOLS
# ============================================================================

@mcp.tool()
def ssh_exec(command: str) -> str:
    """
    Executes an allowed command on the remote server via SSH.
    
    Args:
        command: Command to execute (must be in allowlist)
        
    Returns:
        Command output or error message
        
    Security:
        - Only commands matching regex patterns in ALLOWED_COMMANDS will run.
        - Timeout protection is active.
        - Uses SSH key authentication.
    """
    # Validate configuration
    config_error = validate_config()
    if config_error:
        return f"❌ CONFIG ERROR: {config_error}"
    
    command = command.strip()
    
    # Allowlist check
    if not is_allowed(command):
        return f"❌ DENIED: Command is not in the allowlist!\n\nCommand: {command}\n\nUse the 'ssh_list_allowed' tool to see permitted commands."
    
    # Prepare SSH command
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY,
        "-p", SSH_PORT,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=10",
        f"{SSH_USER}@{SSH_HOST}",
        command,
    ]
    
    try:
        # Execute command
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            timeout=COMMAND_TIMEOUT,
            text=True
        )
        
        output = f"✅ Command: {command}\n"
        output += f"Host: {SSH_USER}@{SSH_HOST}\n"
        output += f"Exit Code: {result.returncode}\n\n"
        
        if result.stdout:
            output += "=== STDOUT ===\n"
            output += result.stdout
        
        if result.stderr:
            output += "\n=== STDERR ===\n"
            output += result.stderr
        
        return output
        
    except subprocess.TimeoutExpired:
        return f"❌ TIMEOUT: Command failed to complete within {COMMAND_TIMEOUT} seconds!\n\nCommand: {command}"
        
    except subprocess.CalledProcessError as e:
        return f"❌ ERROR: Command failed!\n\nCommand: {command}\nExit Code: {e.returncode}\n\n{e.stderr}"
        
    except Exception as e:
        return f"❌ EXCEPTION: {type(e).__name__}: {str(e)}\n\nCommand: {command}"


@mcp.tool()
def ssh_list_allowed() -> str:
    """
    Shows the allowlist of permitted commands.
    
    Returns:
        All regex patterns in the allowlist
    """
    output = "📋 Permitted Command Patterns:\n"
    output += "=" * 60 + "\n\n"
    
    for i, pattern in enumerate(ALLOWED_COMMANDS, 1):
        output += f"{i:2d}. {pattern}\n"
    
    output += "\n" + "=" * 60 + "\n"
    output += f"Total {len(ALLOWED_COMMANDS)} patterns defined.\n"
    output += f"\nNote: These are regex patterns. Your command must match one of these patterns."
    
    return output


@mcp.tool()
def ssh_test_connection() -> str:
    """
    Tests the SSH connection.
    
    Returns:
        Connection status and server information
    """
    # Validate configuration
    config_error = validate_config()
    if config_error:
        return f"❌ CONFIG ERROR: {config_error}"
    
    # Test connection with a simple command
    test_cmd = "echo 'SSH Connection OK' && uname -a"
    
    ssh_cmd = [
        "ssh",
        "-i", SSH_KEY,
        "-p", SSH_PORT,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=10",
        f"{SSH_USER}@{SSH_HOST}",
        test_cmd,
    ]
    
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            timeout=15,
            text=True
        )
        
        if result.returncode == 0:
            output = "✅ SSH CONNECTION SUCCESSFUL!\n\n"
            output += f"Host: {SSH_HOST}:{SSH_PORT}\n"
            output += f"User: {SSH_USER}\n"
            output += f"Key: {SSH_KEY}\n\n"
            output += "Server Info:\n"
            output += result.stdout
            return output
        else:
            return f"❌ CONNECTION FAILED!\n\nExit Code: {result.returncode}\n\n{result.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"❌ TIMEOUT: SSH connection timed out!"
        
    except Exception as e:
        return f"❌ EXCEPTION: {type(e).__name__}: {str(e)}"


@mcp.tool()
def ssh_get_config() -> str:
    """
    Shows the current SSH configuration.
    
    Returns:
        Active configuration details
    """
    output = "⚙️  SSH MCP Server Configuration:\n"
    output += "=" * 60 + "\n\n"
    output += f"SSH_HOST: {SSH_HOST if SSH_HOST else '❌ NOT DEFINED'}\n"
    output += f"SSH_USER: {SSH_USER}\n"
    output += f"SSH_KEY: {SSH_KEY}\n"
    output += f"SSH_PORT: {SSH_PORT}\n"
    output += f"COMMAND_TIMEOUT: {COMMAND_TIMEOUT} seconds\n\n"
    
    # Key file check
    if os.path.exists(SSH_KEY):
        stat_info = os.stat(SSH_KEY)
        perms = oct(stat_info.st_mode)[-3:]
        output += f"✅ SSH Key file exists (permissions: {perms})\n"
        if perms != "600":
            output += f"⚠️  WARNING: Key file permissions are not ideal! Run 'chmod 600 {SSH_KEY}'.\n"
    else:
        output += f"❌ SSH Key file not found!\n"
    
    output += "\n" + "=" * 60 + "\n"
    output += f"{len(ALLOWED_COMMANDS)} command patterns defined in allowlist.\n"
    
    return output


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Startup check
    print("🚀 Starting SSH MCP Server...")
    print(f"📡 Target: {SSH_USER}@{SSH_HOST}:{SSH_PORT}")
    print(f"🔑 Key: {SSH_KEY}")
    print(f"⏱️  Timeout: {COMMAND_TIMEOUT}s")
    print(f"🛡️  Allowlist: {len(ALLOWED_COMMANDS)} patterns")
    print("-" * 60)
    
    config_error = validate_config()
    if config_error:
        print(f"❌ CONFIG ERROR: {config_error}")
        print("\nPlease check your environment variables:")
        print("  export SSH_HOST='your.server.ip'")
        print("  export SSH_USER='ai-runner'")
        print("  export SSH_KEY='$HOME/.ssh/ai_runner'")
        exit(1)
    
    print("✅ Configuration OK")
    print("🎯 MCP Server is running...\n")
    
    mcp.run()
