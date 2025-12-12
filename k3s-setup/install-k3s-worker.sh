#!/bin/bash
# Script to install k3s on worker nodes (Raspberry PI 4B)
# This script should be run on each worker Raspberry PI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing k3s worker node...${NC}"

# Check if running on ARM architecture
if [[ $(uname -m) != "aarch64" && $(uname -m) != "armv7l" ]]; then
    echo -e "${YELLOW}Warning: This script is designed for Raspberry PI (ARM architecture)${NC}"
fi

# Check for required environment variables
if [ -z "$K3S_URL" ]; then
    echo -e "${RED}Error: K3S_URL environment variable is not set${NC}"
    echo "Usage: K3S_URL=https://master-ip:6443 K3S_TOKEN=your-token ./install-k3s-worker.sh"
    exit 1
fi

if [ -z "$K3S_TOKEN" ]; then
    echo -e "${RED}Error: K3S_TOKEN environment variable is not set${NC}"
    echo "Usage: K3S_URL=https://master-ip:6443 K3S_TOKEN=your-token ./install-k3s-worker.sh"
    exit 1
fi

# Get worker node name (or use hostname)
WORKER_NAME="${K3S_NODE_NAME:-rpi-worker-$(hostname)}"

echo -e "${GREEN}Connecting to master: ${K3S_URL}${NC}"
echo -e "${GREEN}Worker node name: ${WORKER_NAME}${NC}"

# Update system
echo -e "${GREEN}Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Enable cgroups (required for k3s on Raspberry PI)
echo -e "${GREEN}Enabling cgroups...${NC}"
if ! grep -q "cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory" /boot/firmware/cmdline.txt 2>/dev/null && \
   ! grep -q "cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory" /boot/cmdline.txt 2>/dev/null; then
    
    # Check which boot config file exists
    if [ -f /boot/firmware/cmdline.txt ]; then
        CMDLINE_FILE="/boot/firmware/cmdline.txt"
    elif [ -f /boot/cmdline.txt ]; then
        CMDLINE_FILE="/boot/cmdline.txt"
    else
        echo -e "${RED}Could not find cmdline.txt file${NC}"
        exit 1
    fi
    
    sudo cp $CMDLINE_FILE ${CMDLINE_FILE}.backup
    sudo sed -i '$ s/$/ cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory/' $CMDLINE_FILE
    echo -e "${YELLOW}Cgroups enabled. A reboot will be required after installation.${NC}"
fi

# Install k3s as agent (worker node)
echo -e "${GREEN}Installing k3s agent...${NC}"
curl -sfL https://get.k3s.io | K3S_URL=$K3S_URL K3S_TOKEN=$K3S_TOKEN sh -s - agent \
    --node-name "$WORKER_NAME"

# Wait for k3s to be ready
echo -e "${GREEN}Waiting for k3s agent to be ready...${NC}"
sleep 10

echo -e "${GREEN}k3s worker node installed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. If this is the first installation, reboot the system: ${GREEN}sudo reboot${NC}"
echo -e "2. Check cluster status from master node: ${GREEN}kubectl get nodes${NC}"
echo ""
echo -e "${GREEN}Installation complete!${NC}"
