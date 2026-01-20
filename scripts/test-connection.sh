#!/bin/bash
#
# SSH Connection Test Script
# ==========================
# Tests if the MCP server configuration is working.
#
# Usage:
#   bash test-connection.sh
#

set -e

echo "=================================================="
echo "SSH MCP Server - Connection Test"
echo "=================================================="
echo ""

# Check environment variables
if [ -z "$SSH_HOST" ]; then
    echo "❌ ERROR: SSH_HOST environment variable is not defined!"
    echo ""
    echo "Please set them using:"
    echo "  export SSH_HOST='your.server.ip'"
    echo "  export SSH_USER='ai-runner'"
    echo "  export SSH_KEY='\$HOME/.ssh/ai_runner'"
    exit 1
fi

SSH_USER="${SSH_USER:-ai-runner}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/ai_runner}"
SSH_PORT="${SSH_PORT:-22}"

echo "📋 Configuration:"
echo "  Host: $SSH_HOST"
echo "  User: $SSH_USER"
echo "  Key: $SSH_KEY"
echo "  Port: $SSH_PORT"
echo ""

# Does the key file exist?
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ ERROR: SSH key file not found: $SSH_KEY"
    exit 1
fi

# Are the key permissions correct?
KEY_PERMS=$(stat -c %a "$SSH_KEY" 2>/dev/null || stat -f %A "$SSH_KEY")
if [ "$KEY_PERMS" != "600" ]; then
    echo "⚠️  WARNING: SSH key permissions are not ideal (current: $KEY_PERMS, should be: 600)"
    echo "  To fix: chmod 600 $SSH_KEY"
    echo ""
fi

# Test SSH connection
echo "🔌 Testing SSH connection..."
if ssh -i "$SSH_KEY" -p "$SSH_PORT" -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new "$SSH_USER@$SSH_HOST" "echo 'SSH OK' && uname -a"; then
    echo ""
    echo "✅ SUCCESS! SSH connection is working."
else
    echo ""
    echo "❌ FAILED! Could not establish SSH connection."
    echo ""
    echo "Try verbose mode for detailed error info:"
    echo "  ssh -vvv -i $SSH_KEY -p $SSH_PORT $USERNAME@$SSH_HOST"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ All checks passed!"
echo "=================================================="
echo ""
echo "To start the MCP server:"
echo "  python ssh_mcp_server.py"
echo ""
