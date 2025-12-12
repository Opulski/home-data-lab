# K3s Cluster Setup on Raspberry Pi 4B

This guide explains how to set up a k3s cluster on 4 Raspberry Pi 4B nodes.

## Overview

k3s is a lightweight Kubernetes distribution perfect for edge computing, IoT, and ARM devices like Raspberry Pi. This setup creates a cluster with 1 master node and 3 worker nodes.

## Prerequisites

### Hardware
- 4x Raspberry Pi 4B (4GB+ RAM recommended)
- 4x MicroSD cards (32GB+ recommended)
- Network switch or router
- Ethernet cables (recommended over WiFi)
- Power supplies for all Raspberry Pis

### Software
- Raspberry Pi OS Lite (64-bit) on all nodes
- SSH enabled on all nodes
- Static IP addresses configured (recommended)

## Network Configuration

It's recommended to assign static IP addresses to your Raspberry Pis. Example configuration:

- Master Node: `192.168.1.10`
- Worker Node 1: `192.168.1.11`
- Worker Node 2: `192.168.1.12`
- Worker Node 3: `192.168.1.13`

## Setup Methods

You can set up the cluster using either:
1. **Ansible Playbook** (Recommended for automation)
2. **Manual Installation** (Using shell scripts)

### Method 1: Automated Setup with Ansible

#### Prerequisites
- Ansible installed on your control machine
- SSH key-based authentication set up to all Raspberry Pis

#### Steps

1. **Update the inventory file** with your Raspberry Pi IP addresses:
   ```bash
   cd ansible
   nano inventory.yml
   ```
   
   Update the `ansible_host` values to match your Raspberry Pi IP addresses.

2. **Run the Ansible playbook**:
   ```bash
   ansible-playbook -i inventory.yml playbook-k3s-setup.yml
   ```

The playbook will:
- Update all systems
- Enable cgroups (required for k3s on Raspberry Pi)
- Install k3s on the master node
- Install k3s agents on worker nodes
- Verify the cluster is ready

#### Accessing the Cluster

After the playbook completes, SSH into the master node and run:
```bash
sudo kubectl get nodes
```

You should see all 4 nodes in `Ready` state.

### Method 2: Manual Installation

#### Step 1: Prepare All Nodes

On **all** Raspberry Pis, ensure they are updated:
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### Step 2: Install Master Node

On the **master node** (e.g., `192.168.1.10`):

1. Copy the installation script:
   ```bash
   scp k3s-setup/install-k3s-master.sh pi@192.168.1.10:~/
   ```

2. SSH into the master node and run:
   ```bash
   chmod +x install-k3s-master.sh
   ./install-k3s-master.sh
   ```

3. The script will output the node token and URL needed for worker nodes. Save these values.

4. If this is the first installation, reboot:
   ```bash
   sudo reboot
   ```

5. After reboot, verify the master is running:
   ```bash
   sudo systemctl status k3s
   kubectl get nodes
   ```

#### Step 3: Install Worker Nodes

On **each worker node** (e.g., `192.168.1.11`, `.12`, `.13`):

1. Copy the installation script:
   ```bash
   scp k3s-setup/install-k3s-worker.sh pi@192.168.1.11:~/
   ```

2. SSH into the worker node and run:
   ```bash
   chmod +x install-k3s-worker.sh
   K3S_URL=https://192.168.1.10:6443 K3S_TOKEN=your-token-here ./install-k3s-worker.sh
   ```
   
   Replace `your-token-here` with the token from the master node.

3. If this is the first installation, reboot:
   ```bash
   sudo reboot
   ```

4. Repeat for all worker nodes.

#### Step 4: Verify the Cluster

From the master node, check that all nodes are ready:
```bash
kubectl get nodes -o wide
```

Expected output:
```
NAME            STATUS   ROLES                  AGE   VERSION
rpi-master      Ready    control-plane,master   5m    v1.27.x+k3s1
rpi-worker-1    Ready    <none>                 3m    v1.27.x+k3s1
rpi-worker-2    Ready    <none>                 3m    v1.27.x+k3s1
rpi-worker-3    Ready    <none>                 3m    v1.27.x+k3s1
```

## Post-Installation

### Access kubectl from Your Local Machine

Copy the kubeconfig from the master node:
```bash
scp pi@192.168.1.10:/etc/rancher/k3s/k3s.yaml ~/.kube/config-rpi
```

Edit the file and replace `127.0.0.1` with your master node's IP:
```bash
sed -i '' 's/127.0.0.1/192.168.1.10/g' ~/.kube/config-rpi
export KUBECONFIG=~/.kube/config-rpi
kubectl get nodes
```

### Install kubectl (if not already installed)

On Linux/macOS:
```bash
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

## Troubleshooting

### Node Not Ready

If a node shows `NotReady` status:
```bash
# Check k3s service status
sudo systemctl status k3s         # On master
sudo systemctl status k3s-agent   # On worker

# Check logs
sudo journalctl -u k3s -f          # On master
sudo journalctl -u k3s-agent -f    # On worker
```

### cgroups Not Enabled

If you see cgroup-related errors:
```bash
# Check if cgroups are enabled
cat /boot/firmware/cmdline.txt
# or
cat /boot/cmdline.txt

# Should contain: cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory
```

If not present, add them and reboot:
```bash
sudo sed -i '$ s/$/ cgroup_enable=cpuset cgroup_memory=1 cgroup_enable=memory/' /boot/firmware/cmdline.txt
sudo reboot
```

### Network Issues

If nodes can't communicate:
```bash
# Check connectivity from worker to master
ping 192.168.1.10

# Check if port 6443 is accessible
telnet 192.168.1.10 6443
```

### Uninstall k3s

To remove k3s:
```bash
# On master:
/usr/local/bin/k3s-uninstall.sh

# On workers:
/usr/local/bin/k3s-agent-uninstall.sh
```

## Next Steps

Once your cluster is running:
1. Deploy the data scraping infrastructure: [DATA_SCRAPING.md](DATA_SCRAPING.md)
2. Set up Jupyter notebooks: [JUPYTER_SETUP.md](JUPYTER_SETUP.md)
3. Monitor your cluster resources

## Resources

- [k3s Documentation](https://docs.k3s.io/)
- [Raspberry Pi k3s Guide](https://docs.k3s.io/installation/requirements)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
