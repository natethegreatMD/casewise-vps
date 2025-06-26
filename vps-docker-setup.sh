#!/bin/bash

# VPS Docker Setup Script for Ubuntu 22.04
# IP: 143.244.154.89
# This script installs Docker CE and Docker Compose v2 plugin

set -e  # Exit on any error

echo "=============================================="
echo "Starting Docker CE and Docker Compose v2 Setup"
echo "=============================================="

# Step 1: Update package index and install prerequisites
echo "Step 1: Updating package index and installing prerequisites..."
apt-get update -y
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

echo "✓ Prerequisites installed successfully"

# Step 2: Add Docker's official GPG key
echo "Step 2: Adding Docker's official GPG key..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "✓ Docker GPG key added successfully"

# Step 3: Add Docker repository
echo "Step 3: Adding Docker repository..."
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "✓ Docker repository added successfully"

# Step 4: Update package index again
echo "Step 4: Updating package index with Docker repository..."
apt-get update -y

echo "✓ Package index updated successfully"

# Step 5: Install Docker CE, CLI, containerd, and Docker Compose plugin
echo "Step 5: Installing Docker CE, CLI, containerd, and Docker Compose plugin..."
apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

echo "✓ Docker CE and Docker Compose v2 plugin installed successfully"

# Step 6: Enable Docker service to start on boot
echo "Step 6: Enabling Docker service to start on boot..."
systemctl enable docker
systemctl start docker

echo "✓ Docker service enabled and started successfully"

# Step 7: Add users to docker group
echo "Step 7: Adding users to docker group..."

# Check if root user exists and add to docker group
if id "root" &>/dev/null; then
    usermod -aG docker root
    echo "✓ Added root user to docker group"
else
    echo "⚠ Root user not found (this shouldn't happen)"
fi

# Check if ubuntu user exists and add to docker group
if id "ubuntu" &>/dev/null; then
    usermod -aG docker ubuntu
    echo "✓ Added ubuntu user to docker group"
else
    echo "⚠ Ubuntu user not found - skipping"
fi

echo "✓ User group configuration completed"

# Step 8: Verify Docker installation
echo "Step 8: Verifying Docker installation..."

# Test Docker version
DOCKER_VERSION=$(docker --version)
echo "Docker version: $DOCKER_VERSION"

# Test Docker Compose version (v2 plugin)
COMPOSE_VERSION=$(docker compose version)
echo "Docker Compose version: $COMPOSE_VERSION"

# Test Docker with hello-world
echo "Running Docker hello-world test..."
docker run --rm hello-world > /dev/null 2>&1

echo "✓ Docker installation verified successfully"

# Step 9: Test Docker Compose functionality
echo "Step 9: Testing Docker Compose functionality..."

# Create a simple test docker-compose.yml
cat > /tmp/test-compose.yml << EOF
version: '3.8'
services:
  test:
    image: hello-world
EOF

# Test docker compose command
docker compose -f /tmp/test-compose.yml up --rm test > /dev/null 2>&1

# Clean up test file
rm /tmp/test-compose.yml

echo "✓ Docker Compose v2 plugin verified successfully"

# Step 10: Display final status
echo "=============================================="
echo "Docker Setup Complete!"
echo "=============================================="
echo "Docker CE Version: $(docker --version)"
echo "Docker Compose Version: $(docker compose version)"
echo "Docker Service Status: $(systemctl is-active docker)"
echo "Docker Service Enabled: $(systemctl is-enabled docker)"

echo ""
echo "Users in docker group:"
getent group docker

echo ""
echo "✅ All setup completed successfully!"
echo "✅ Docker CE is installed and running"
echo "✅ Docker Compose v2 plugin is installed and working"
echo "✅ Docker service will start automatically on boot"
echo "✅ Root and ubuntu users added to docker group"

echo ""
echo "Next steps:"
echo "1. Log out and back in (or run 'newgrp docker') to refresh group membership"
echo "2. Clone your CasewiseMD repository"
echo "3. Run your Docker Compose setup"

echo ""
echo "Ready for CasewiseMD deployment! 🚀" 