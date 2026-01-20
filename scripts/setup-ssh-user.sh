#!/bin/bash
#
# SSH User Setup Script
# ================================
# This script creates the 'ai-runner' user on a remote server and sets up SSH key authentication.
#
# Usage:
#   1. Copy this script to the server or download it via wget/curl.
#   2. Run with root or sudo privileges:
#      sudo bash setup-ssh-user.sh
#

set -e  # Stop on error

echo "=================================================="
echo "SSH MCP Server - User Setup Script"
echo "=================================================="
echo ""

# Username
USERNAME="ai-runner"

# Check if user exists
if id "$USERNAME" &>/dev/null; then
    echo "✅ User '$USERNAME' already exists."
else
    echo "📝 Creating user '$USERNAME'..."
    adduser --disabled-password --gecos "" "$USERNAME"
    echo "✅ User created."
fi

# Create SSH directory
echo "📁 Setting up SSH directory..."
mkdir -p "/home/$USERNAME/.ssh"
chmod 700 "/home/$USERNAME/.ssh"
touch "/home/$USERNAME/.ssh/authorized_keys"
chmod 600 "/home/$USERNAME/.ssh/authorized_keys"
chown -R "$USERNAME:$USERNAME" "/home/$USERNAME/.ssh"
echo "✅ SSH directory ready."

echo ""
echo "=================================================="
echo "✅ Setup Complete!"
echo "=================================================="
echo ""
echo "NEXT STEPS:"
echo ""
echo "1. Create an SSH key on your local machine:"
echo "   ssh-keygen -t ed25519 -f ~/.ssh/ai_runner -C 'ai-runner@mcp'"
echo ""
echo "2. Copy the public key:"
echo "   cat ~/.ssh/ai_runner.pub"
# No longer relevant to explicitly state sudo nano as ssh-copy-id is better, but keeping the manual steps for reference.
echo ""
echo "3. Add the public key to this server:"
echo "   sudo -u $USERNAME sh -c 'echo \"YOUR_PUBLIC_KEY_CONTENT\" >> /home/$USERNAME/.ssh/authorized_keys'"
echo ""
echo "4. Verify permissions:"
echo "   sudo chmod 600 /home/$USERNAME/.ssh/authorized_keys"
echo "   sudo chown $USERNAME:$USERNAME /home/$USERNAME/.ssh/authorized_keys"
echo ""
echo "5. Test the SSH connection from local:"
echo "   ssh -i ~/.ssh/ai_runner $USERNAME@$(hostname -I | awk '{print $1}')"
echo ""
echo "=================================================="
