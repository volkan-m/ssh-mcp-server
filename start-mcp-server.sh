#!/bin/bash
#
# SSH MCP Server Startup Script
# ================================
# This script starts the MCP server with the correct environment variables.
#
# Usage:
#   bash start-mcp-server.sh
#

set -e

echo "=================================================="
echo "Starting SSH MCP Server"
echo "=================================================="
echo ""

# Configuration - Set your environment variables here
export SSH_HOST="your.server.ip"
export SSH_USER="ai-runner"
export SSH_KEY="$HOME/.ssh/ai_runner"
export SSH_PORT="22"
export COMMAND_TIMEOUT="30"

echo "📋 Configuration:"
echo "  Host: $SSH_HOST"
echo "  User: $SSH_USER"
echo "  Key: $SSH_KEY"
echo "  Port: $SSH_PORT"
echo "  Timeout: ${COMMAND_TIMEOUT}s"
echo ""

# Key file check
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ ERROR: SSH key file not found: $SSH_KEY"
    echo ""
    echo "To create an SSH key:"
    echo "  ssh-keygen -t ed25519 -f ~/.ssh/ai_runner -C 'ai-runner@mcp-server'"
    exit 1
fi

# Key permissions check
KEY_PERMS=$(stat -c %a "$SSH_KEY" 2>/dev/null || stat -f %A "$SSH_KEY" 2>/dev/null || echo "unknown")
if [ "$KEY_PERMS" != "600" ] && [ "$KEY_PERMS" != "unknown" ]; then
    echo "⚠️  WARNING: SSH key permissions are not ideal (current: $KEY_PERMS)"
    echo "  Fixing permissions..."
    chmod 600 "$SSH_KEY"
    echo "✅ Permissions set to 600"
    echo ""
fi

# Python check
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ ERROR: Python not found!"
    exit 1
fi

# Determine Python command (Venv check)
if [ -f "./venv/bin/python3" ]; then
    PYTHON_CMD="./venv/bin/python3"
elif [ -f "./venv/bin/python" ]; then
    PYTHON_CMD="./venv/bin/python"
else
    PYTHON_CMD="python3"
    if ! command -v python3 &> /dev/null; then
        PYTHON_CMD="python"
    fi
fi

echo "🐍 Python: $PYTHON_CMD"
echo ""

# fastmcp check
echo "📦 Checking dependencies..."
if ! $PYTHON_CMD -c "import mcp.server.fastmcp" 2>/dev/null; then
    echo "⚠️  fastmcp is not installed!"
    if [ -f "./venv/bin/pip" ]; then
        echo "  Installing in venv..."
        ./venv/bin/pip install fastmcp
    else
        echo "  Installing..."
        pip install fastmcp
    fi
    echo "✅ fastmcp installed"
else
    echo "✅ fastmcp is installed"
fi
echo ""

# SSH connection test (optional)
read -p "🔌 Do you want to test the SSH connection? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Testing connection..."
    if ssh -i "$SSH_KEY" -p "$SSH_PORT" -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new "$SSH_USER@$SSH_HOST" "echo '✅ SSH connection successful!' && uname -a" 2>/dev/null; then
        echo ""
    else
        echo "⚠️  SSH connection failed!"
        echo ""
        echo "To upload your public key to the server:"
        echo "  ssh-copy-id -i $SSH_KEY.pub $SSH_USER@$SSH_HOST"
        echo ""
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Start MCP Server
echo "=================================================="
echo "🚀 Starting MCP Server..."
echo "=================================================="
echo ""
echo "To exit: Ctrl+C"
echo ""

cd "$(dirname "$0")"
$PYTHON_CMD ssh_mcp_server.py
