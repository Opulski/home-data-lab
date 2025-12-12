#!/bin/bash
# Script to install k3s on the master node (Raspberry PI 4B)
# This script should be run on the first Raspberry PI that will act as the master

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing k3s master node...${NC}"

# Check if running on ARM architecture
if [[ $(uname -m) != "aarch64" && $(uname -m) != "armv7l" ]]; then
    echo -e "${YELLOW}Warning: This script is designed for Raspberry PI (ARM architecture)${NC}"
fi

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

# Install k3s as server (master node)
echo -e "${GREEN}Installing k3s server...${NC}"
curl -sfL https://get.k3s.io | sh -s - server \
    --disable traefik \
    --write-kubeconfig-mode 644 \
    --node-name "rpi-master"

# Wait for k3s to be ready
echo -e "${GREEN}Waiting for k3s to be ready...${NC}"
sleep 10

# Get node token for worker nodes
K3S_TOKEN=$(sudo cat /var/lib/rancher/k3s/server/node-token)
K3S_URL="https://$(hostname -I | awk '{print $1}'):6443"

echo -e "${GREEN}k3s master node installed successfully!${NC}"
echo ""
echo -e "${YELLOW}=== Important Information ===${NC}"
echo -e "Master Node Token: ${GREEN}${K3S_TOKEN}${NC}"
echo -e "Master Node URL: ${GREEN}${K3S_URL}${NC}"
echo ""
echo -e "Save these values to join worker nodes to the cluster."
echo -e "You can also find the token at: /var/lib/rancher/k3s/server/node-token"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. If this is the first installation, reboot the system: ${GREEN}sudo reboot${NC}"
echo -e "2. Run the worker installation script on other Raspberry PIs"
echo -e "3. Check cluster status: ${GREEN}kubectl get nodes${NC}"
echo ""

# Create a token file for easy access
sudo sh -c "echo $K3S_TOKEN > /tmp/k3s-token.txt"
sudo sh -c "echo $K3S_URL > /tmp/k3s-url.txt"
sudo chmod 644 /tmp/k3s-token.txt /tmp/k3s-url.txt

echo -e "${GREEN}Installation complete!${NC}"
