# Home Data Lab

A complete data analytics platform running on Raspberry Pi cluster for electricity market analysis.

## 🎯 Overview

This project provides a complete infrastructure for collecting, storing, and analyzing electricity market data from European markets using a k3s Kubernetes cluster running on Raspberry Pi 4B devices.

### Features

- **Automated k3s Cluster Setup**: Deploy Kubernetes on 4 Raspberry Pi 4B nodes (1 master, 3 workers)
- **Data Scraping**: Automated collection of electricity market data from:
  - ENTSO-E Transparency Platform (day-ahead prices, load, generation)
  - EPEX Spot markets (via ENTSO-E API)
- **Jupyter Notebooks**: Interactive data analysis and visualization
- **Containerized Workloads**: All services run in Kubernetes for scalability and reliability

## 📋 Prerequisites

### Hardware
- 4x Raspberry Pi 4B (4GB+ RAM recommended)
- 4x MicroSD cards (32GB+)
- Network switch and Ethernet cables
- Power supplies

### Software
- Raspberry Pi OS Lite (64-bit)
- SSH access to all Raspberry Pis
- Ansible (for automated deployment)

### API Keys
- ENTSO-E API key (free registration at https://transparency.entsoe.eu/)

## 🚀 Quick Start

### 1. Set Up k3s Cluster

**Option A: Automated with Ansible (Recommended)**

```bash
cd ansible
# Update inventory.yml with your Raspberry Pi IP addresses
nano inventory.yml
# Run the playbook
ansible-playbook -i inventory.yml playbook-k3s-setup.yml
```

**Option B: Manual Installation**

```bash
# On master node
./k3s-setup/install-k3s-master.sh

# On each worker node (use token from master)
K3S_URL=https://master-ip:6443 K3S_TOKEN=your-token ./k3s-setup/install-k3s-worker.sh
```

See [docs/K3S_SETUP.md](docs/K3S_SETUP.md) for detailed instructions.

### 2. Deploy Data Scrapers

```bash
# Configure API credentials
cd data-scrapers
cp config.env.example config.env
nano config.env  # Add your ENTSO-E API key

# Build and deploy
docker build -t data-scraper:latest .
kubectl apply -f ../k3s-setup/data-scraper-deployment.yaml

# Create secret with your API key
kubectl create secret generic scraper-secrets \
  --from-literal=entsoe-api-key=YOUR_API_KEY \
  --namespace=data-lab
```

See [docs/DATA_SCRAPING.md](docs/DATA_SCRAPING.md) for detailed instructions.

### 3. Set Up Jupyter Notebooks

```bash
# Deploy Jupyter
kubectl apply -f k3s-setup/jupyter-deployment.yaml

# Access at http://<raspberry-pi-ip>:30888
# Get token from logs:
kubectl logs -n data-lab -l app=jupyter-notebook | grep token
```

See [docs/JUPYTER_SETUP.md](docs/JUPYTER_SETUP.md) for detailed instructions.

## 📊 Available Notebooks

1. **01_entsoe_data_analysis.ipynb**: ENTSO-E data exploration
   - Day-ahead prices
   - Load patterns
   - Generation by type

2. **02_epex_spot_analysis.ipynb**: EPEX Spot market analysis
   - Multi-market comparison
   - Price spreads
   - Market coupling

3. **03_combined_analysis.ipynb**: Advanced analysis
   - Price-load relationships
   - Renewable impact
   - Cross-market dynamics

## 🗂️ Project Structure

```
home-data-lab/
├── ansible/                    # Ansible automation
│   ├── inventory.yml          # Cluster inventory
│   └── playbook-k3s-setup.yml # k3s installation playbook
├── data-scrapers/             # Data collection
│   ├── entsoe_scraper.py      # ENTSO-E scraper
│   ├── epex_spot_scraper.py   # EPEX Spot scraper
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Container image
│   └── config.env.example     # Configuration template
├── k3s-setup/                 # Kubernetes setup
│   ├── install-k3s-master.sh  # Master node installer
│   ├── install-k3s-worker.sh  # Worker node installer
│   ├── data-scraper-deployment.yaml  # Scraper k8s manifests
│   └── jupyter-deployment.yaml       # Jupyter k8s manifests
├── notebooks/                 # Jupyter notebooks
│   ├── 01_entsoe_data_analysis.ipynb
│   ├── 02_epex_spot_analysis.ipynb
│   └── 03_combined_analysis.ipynb
└── docs/                      # Documentation
    ├── K3S_SETUP.md
    ├── DATA_SCRAPING.md
    └── JUPYTER_SETUP.md
```

## 🔧 Configuration

### Network Configuration

Set static IPs for your Raspberry Pis (recommended):
- Master: `192.168.1.10`
- Worker 1: `192.168.1.11`
- Worker 2: `192.168.1.12`
- Worker 3: `192.168.1.13`

### Data Scraping Schedule

Default: Every 6 hours. Modify in `k3s-setup/data-scraper-deployment.yaml`:
```yaml
schedule: "0 */6 * * *"  # Cron format
```

### Supported Markets

The scrapers support all ENTSO-E countries:
- Germany (DE), France (FR), UK (GB), Italy (IT), Spain (ES)
- Netherlands (NL), Belgium (BE), Austria (AT), Switzerland (CH)
- Poland (PL), Denmark (DK), Sweden (SE), Norway (NO)
- And more...

## 📈 Monitoring

Check cluster status:
```bash
kubectl get nodes
kubectl get pods -n data-lab
kubectl get cronjobs -n data-lab
```

View scraper logs:
```bash
kubectl logs -n data-lab -l app=scraper-service
```

Check data collection:
```bash
kubectl exec -n data-lab -it <scraper-pod> -- ls -lh /data
```

## 🛠️ Troubleshooting

See detailed troubleshooting guides in:
- [docs/K3S_SETUP.md](docs/K3S_SETUP.md#troubleshooting)
- [docs/DATA_SCRAPING.md](docs/DATA_SCRAPING.md#troubleshooting)
- [docs/JUPYTER_SETUP.md](docs/JUPYTER_SETUP.md#troubleshooting)

## 📚 Resources

### k3s
- [k3s Documentation](https://docs.k3s.io/)
- [Raspberry Pi k3s Guide](https://docs.k3s.io/installation/requirements)

### Data Sources
- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
- [EPEX Spot](https://www.epexspot.com/)
- [entsoe-py Library](https://github.com/EnergieID/entsoe-py)

### Analysis Tools
- [Jupyter Documentation](https://jupyter.org/documentation)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- ENTSO-E for providing transparent electricity market data
- The k3s project for lightweight Kubernetes
- The Raspberry Pi community
