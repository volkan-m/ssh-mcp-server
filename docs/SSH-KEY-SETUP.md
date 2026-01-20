# SSH Key Generation and Setup Guide

This guide provides step-by-step instructions on how to create the necessary SSH key for the SSH MCP server and how to install it on your remote server.

## 🔑 Step 1: Create SSH Key (On Your Local Machine)

### Method 1: Ed25519 Key (Recommended - Modern and Secure)

```bash
# Navigate to ~/.ssh/
cd ~/.ssh/

# Generate Ed25519 key
ssh-keygen -t ed25519 -f ~/.ssh/ai_runner -C "ai-runner@mcp-server"
```

**Parameters:**
- `-t ed25519`: Modern and secure key type.
- `-f ~/.ssh/ai_runner`: Filename for the key.
- `-C "ai-runner@mcp-server"`: Comment for the key.

**Prompts:**
```
Enter passphrase (empty for no passphrase): [Press Enter - No passphrase]
Enter same passphrase again: [Press Enter again]
```

⚠️ **Important**: For MCP usage, a key without a passphrase is required (leave it empty).

### Method 2: RSA Key (Alternative)

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/ai_runner -C "ai-runner@mcp-server"
```

**Parameters:**
- `-t rsa`: RSA key type.
- `-b 4096`: 4096-bit key size (more secure).

## 📁 Step 2: Verify Key Files

```bash
# List key files
ls -la ~/.ssh/ai_runner*
```

**Expected Files:**
```
-rw-------  1 user user  464 Jan 20 19:25 /home/user/.ssh/ai_runner        # Private key (SECRET!)
-rw-r--r--  1 user user  102 Jan 20 19:25 /home/user/.ssh/ai_runner.pub    # Public key
```

**Permission Check (Important!):**
```bash
# Private key permissions must be 600
chmod 600 ~/.ssh/ai_runner

# Public key permissions should be 644
chmod 644 ~/.ssh/ai_runner.pub
```

## 👁️ Step 3: View Public Key

```bash
# Show public key content
cat ~/.ssh/ai_runner.pub
```

**Example Output:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGq2... ai-runner@mcp-server
```

📋 **Copy this content** - you will use it when uploading to the server!

## 🚀 Step 4: Upload Public Key to Server

### Method A: Using ssh-copy-id (Easiest)

```bash
# Automatically copy public key to server
ssh-copy-id -i ~/.ssh/ai_runner.pub ai-runner@YOUR_SERVER_IP

# Example:
ssh-copy-id -i ~/.ssh/ai_runner.pub ai-runner@192.168.1.100
```

**Details:**
- **Password**: Enter the password for the `ai-runner` user.
- If successful, you will see a message: "Number of key(s) added: 1".

### Method B: Manual Copy

#### 4B.1. Display and copy the public key
```bash
cat ~/.ssh/ai_runner.pub
```
Select and copy the output.

#### 4B.2. Connect to the server
```bash
ssh root@YOUR_SERVER_IP
```

#### 4B.3. Switch to 'ai-runner' user (or stay as root)
```bash
# Create user if not exists
sudo adduser ai-runner
```

#### 4B.4. Set up SSH directory
```bash
sudo mkdir -p /home/ai-runner/.ssh
sudo touch /home/ai-runner/.ssh/authorized_keys
```

#### 4B.5. Add Public Key to authorized_keys
```bash
sudo nano /home/ai-runner/.ssh/authorized_keys
```
Paste your public key, save and exit.

#### 4B.6. Set final permissions
```bash
sudo chmod 700 /home/ai-runner/.ssh
sudo chmod 600 /home/ai-runner/.ssh/authorized_keys
sudo chown -R ai-runner:ai-runner /home/ai-runner/.ssh
```

## ✅ Step 5: Test the SSH Connection

### Test 1: Simple connection
```bash
ssh -i ~/.ssh/ai_runner ai-runner@YOUR_SERVER_IP
```
If successful, you will log in without a password.

### Test 2: Verbose mode (Debugging)
```bash
ssh -vvv -i ~/.ssh/ai_runner ai-runner@YOUR_SERVER_IP
```

## 🐛 Common Errors and Solutions

### Error: Permission denied (publickey)
**Cause:** Key not uploaded correctly or wrong permissions.
**Solution:** Check `authorized_keys` content and directory permissions as shown in Step 4B.6.

### Error: WARNING: UNPROTECTED PRIVATE KEY FILE!
**Cause:** Private key permissions are too open.
**Solution:** Run `chmod 600 ~/.ssh/ai_runner`.

## 🎯 Summary of Commands

```bash
# 1. Generate Key
ssh-keygen -t ed25519 -f ~/.ssh/ai_runner -C "ai-runner@mcp-server"

# 2. Show Public Key
cat ~/.ssh/ai_runner.pub

# 3. Copy to Server
ssh-copy-id -i ~/.ssh/ai_runner.pub ai-runner@YOUR_SERVER_IP

# 4. Test
ssh -i ~/.ssh/ai_runner ai-runner@YOUR_SERVER_IP

# 5. Start MCP
python ssh_mcp_server.py
```
