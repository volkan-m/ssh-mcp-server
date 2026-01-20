# SSH MCP Server - Quick Start Guide

## ✅ Completed Steps

- ✅ SSH key created (e.g., `~/.ssh/id_ed25519`)
- ✅ Public key retrieved
- ✅ MCP server configured

## 📝 To-Do List

### 1. Upload Public Key to Server

Your public key location:

```bash
cat ~/.ssh/id_ed25519.pub
```

#### Method A: Automatic (Recommended)

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub your-user@your-server.com
```

Enter your password, and you're set!

#### Method B: Manual

1. Connect to the server:
```bash
ssh your-user@your-server.com
```

2. Add the public key to the `authorized_keys` file:
```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add your public key (replace with the content from 'cat ~/.ssh/id_ed25519.pub')
echo "ssh-ed25519 AAAAC3... your-user@mcp-server" >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
```

3. Log out:
```bash
exit
```

### 2. Test the Connection

```bash
ssh -i ~/.ssh/id_ed25519 your-user@your-server.com
```

If you can connect without a password, it's successful! ✅

### 3. Start the MCP Server

#### The Easy Way (Startup Script)

```bash
# Generalize the path as needed
cd /path/to/ssh-mcp-server
bash start-mcp-server.sh
```

#### The Manual Way

```bash
cd /path/to/ssh-mcp-server

export SSH_HOST="your-server.com"
export SSH_USER="your-user"
export SSH_KEY="$HOME/.ssh/id_ed25519"

python3 ssh_mcp_server.py
```

If successful, you will see something like:

```
🚀 Starting SSH MCP Server...
📡 Target: your-user@your-server.com:22
🔑 Key: /home/user/.ssh/id_ed25519
⏱️  Timeout: 30s
🛡️  Allowlist: 30 patterns
------------------------------------------------------------
✅ Configuration OK
🎯 MCP Server is running...
```

## 🎮 Connecting to Cursor/Antigravity

### Cursor IDE

Edit your `~/.cursor/mcp.json` (or the folder where Cursor stores MCP configurations):

```json
{
  "mcpServers": {
    "ssh-tools": {
      "command": "python3",
      "args": ["/ABSOLUTE/PATH/TO/ssh_mcp_server.py"],
      "env": {
        "SSH_HOST": "your-server.com",
        "SSH_USER": "your-user",
        "SSH_KEY": "/home/user/.ssh/id_ed25519",
        "SSH_PORT": "22",
        "COMMAND_TIMEOUT": "30"
      }
    }
  }
}
```

Restart Cursor.

### Google Antigravity

Navigate to Settings → MCP Servers → Add Server:

```json
{
  "ssh-tools": {
    "command": "python3",
    "args": ["/ABSOLUTE/PATH/TO/ssh_mcp_server.py"],
    "env": {
      "SSH_HOST": "your-server.com",
      "SSH_USER": "your-user",
      "SSH_KEY": "/home/user/.ssh/id_ed25519",
      "SSH_PORT": "22",
      "COMMAND_TIMEOUT": "30"
    }
  }
}
```

## 🛠️ Available MCP Tools

Once the MCP server is running, your AI agent can use these tools:

1. **`ssh_exec`** - Execute a command on the server
   ```python
   ssh_exec("systemctl status nginx")
   ```

2. **`ssh_list_allowed`** - List permitted commands
   ```python
   ssh_list_allowed()
   ```

3. **`ssh_test_connection`** - Test the SSH connection
   ```python
   ssh_test_connection()
   ```

4. **`ssh_get_config`** - Show active configuration
   ```python
   ssh_get_config()
   ```

## 📚 Related Documentation

- **`README.md`** - Full project documentation
- **`SSH-KEY-SETUP.md`** - Detailed SSH key guide
- **`config-examples/`** - Configuration examples

## 🆘 Troubleshooting

### "Permission denied" error

```bash
# Check permissions on the private key
ls -la ~/.ssh/id_ed25519
# Should be: -rw------- (600)

# Fix:
chmod 600 ~/.ssh/id_ed25519
```

### "fastmcp not found" error

```bash
pip install fastmcp
```

### SSH connection issues

```bash
# Test with verbose output
ssh -vvv -i ~/.ssh/id_ed25519 your-user@your-server.com
```
