# Connecting MCP Server to Antigravity

This guide explains step-by-step how to connect your SSH MCP Server to Google Antigravity.

## 🎯 Configuration Template

Here is the MCP server configuration for Antigravity:

```json
{
  "ssh-tools": {
    "command": "python3",
    "args": ["/ABSOLUTE/PATH/TO/ssh_mcp_server.py"],
    "env": {
      "SSH_HOST": "your-server.com",
      "SSH_USER": "your-user",
      "SSH_KEY": "/home/your-user/.ssh/id_ed25519",
      "SSH_PORT": "22",
      "COMMAND_TIMEOUT": "30"
    }
  }
}
```

📋 **Copy this JSON** - you will use it in Antigravity settings!

## 📝 Step-by-Step Setup

### 1️⃣ Test the MCP Server

First, ensure your MCP server is working locally:

```bash
cd /path/to/ssh-mcp-server
bash start-mcp-server.sh
```

If successful, you should see:
```
✅ Configuration OK
🎯 MCP Server is running...
```

You can now stop the server (Ctrl+C).

### 2️⃣ Open Antigravity Settings

1. Start Google Antigravity.
2. Go to the main dashboard.
3. Click on **Settings (⚙️)**.
4. Locate the **"MCP Servers"** section in the left menu.

### 3️⃣ Add the Server

1. Click on **"Add Server"** or **"Manage MCP Servers"**.
2. If available, choose **"Edit Raw Configuration"** for full control.
3. Paste the JSON configuration from Step 1, making sure to replace the placeholder paths with actual **absolute paths**.

### 5️⃣ Save and Restart

1. Click **"Save"** or **"Apply"**.
2. Fully restart Antigravity to ensure the new MCP server is discovered.

### 6️⃣ Verify the Tools

In the Antigravity chat, ask:
> "What MCP tools are available?"

You should see:
- ✅ `ssh_exec`
- ✅ `ssh_test_connection`
- ✅ `ssh_list_allowed`
- ✅ `ssh_get_config`

## 🎮 Usage Examples

### Example 1: System Status
> "Check the uptime and disk usage on my server."

### Example 2: Service Check
> "What is the status of the nginx service?"

### Example 3: View Logs
> "Show the last 50 lines of the application log."

## 🐛 Troubleshooting

### "MCP Server Failed to Start"
- **Check Python path**: Ensure `command` points to the correct `python3` binary (run `which python3`).
- **Check File path**: Verify the absolute path to `ssh_mcp_server.py`.
- **Dependencies**: Ensure `fastmcp` is installed (`pip install fastmcp`).

### "SSH Connection Failed"
- **Key Check**: Test manual login `ssh -i ~/.ssh/id_ed25519 your-user@your-server.com`.
- **Permissions**: Ensure private key is 600 (`chmod 600 ~/.ssh/id_ed25519`).
- **Public Key**: Verify your public key is in the server's `~/.ssh/authorized_keys`.

## 📚 Related Documentation

- **`QUICKSTART.md`** - General setup guide.
- **`SSH-KEY-SETUP.md`** - SSH key details.
- **`README.md`** - Full project documentation.
