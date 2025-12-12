# Quick Start Guide

Get your home data lab up and running in 30 minutes!

## Prerequisites Checklist

- [ ] 4x Raspberry Pi 4B with Raspberry Pi OS Lite (64-bit) installed
- [ ] Static IP addresses configured for all Raspberry Pis
- [ ] SSH access to all Raspberry Pis
- [ ] Ansible installed on your control machine
- [ ] ENTSO-E API key (free, get it at https://transparency.entsoe.eu/)

## Step 1: Clone the Repository (2 min)

```bash
git clone https://github.com/Opulski/home-data-lab.git
cd home-data-lab
```

## Step 2: Configure Your Cluster (3 min)

Edit the Ansible inventory with your Raspberry Pi IP addresses:

```bash
nano ansible/inventory.yml
```

Update these lines with your actual IPs:
```yaml
rpi-master:
  ansible_host: 192.168.1.10  # Change to your master PI IP
rpi-worker-1:
  ansible_host: 192.168.1.11  # Change to your worker PI IP
rpi-worker-2:
  ansible_host: 192.168.1.12  # Change to your worker PI IP
rpi-worker-3:
  ansible_host: 192.168.1.13  # Change to your worker PI IP
```

## Step 3: Deploy k3s Cluster (15 min)

Run the Ansible playbook:

```bash
ansible-playbook -i ansible/inventory.yml ansible/playbook-k3s-setup.yml
```

This will:
- ✅ Update all systems
- ✅ Enable cgroups
- ✅ Install k3s on master and workers
- ✅ Configure the cluster
- ✅ Verify all nodes are ready

**Note**: The playbook may reboot your Raspberry Pis if this is the first k3s installation.

## Step 4: Configure kubectl (2 min)

On your control machine:

```bash
# Copy kubeconfig from master node
scp pi@192.168.1.10:/etc/rancher/k3s/k3s.yaml ~/.kube/config-rpi

# Update the server address
sed -i 's/127.0.0.1/192.168.1.10/g' ~/.kube/config-rpi

# Set kubeconfig environment variable
export KUBECONFIG=~/.kube/config-rpi

# Verify cluster is ready
kubectl get nodes
```

You should see all 4 nodes in `Ready` state!

## Step 5: Deploy Data Scrapers (5 min)

### Configure API Key

```bash
cd data-scrapers
cp config.env.example config.env
nano config.env
```

Add your ENTSO-E API key:
```env
ENTSOE_API_KEY=your_actual_api_key_here
```

### Build and Deploy

```bash
# Build Docker image (on a machine with Docker)
docker build -t data-scraper:latest .

# For Raspberry Pi (ARM), use buildx:
docker buildx build --platform linux/arm64 -t data-scraper:latest .

# Load image to k3s cluster
docker save data-scraper:latest | ssh pi@192.168.1.10 'sudo k3s ctr images import -'

# Create namespace and secret
kubectl create namespace data-lab
kubectl create secret generic scraper-secrets \
  --from-literal=entsoe-api-key=YOUR_ACTUAL_API_KEY \
  --namespace=data-lab

# Deploy
kubectl apply -f k3s-setup/data-scraper-deployment.yaml
```

### Verify Scraper

```bash
# Check CronJob is created
kubectl get cronjob -n data-lab

# Trigger a manual scraping job
kubectl create job --from=cronjob/entsoe-scraper manual-scrape-1 -n data-lab

# Watch the job
kubectl get jobs -n data-lab -w

# Check logs
kubectl logs -n data-lab -l job-name=manual-scrape-1
```

## Step 6: Deploy Jupyter (3 min)

```bash
# Deploy Jupyter
kubectl apply -f k3s-setup/jupyter-deployment.yaml

# Wait for pod to be ready
kubectl wait --for=condition=ready pod -l app=jupyter-notebook -n data-lab --timeout=300s

# Get Jupyter token
POD=$(kubectl get pod -n data-lab -l app=jupyter-notebook -o jsonpath='{.items[0].metadata.name}')
kubectl logs $POD -n data-lab | grep token
```

## Step 7: Access Jupyter (1 min)

Open your browser and navigate to:
```
http://192.168.1.10:30888
```

(Replace with any of your Raspberry Pi IPs)

Enter the token from the previous step to log in.

## Step 8: Upload and Run Notebooks

In Jupyter, open a terminal and:

```bash
cd work
git clone https://github.com/Opulski/home-data-lab.git
cd home-data-lab/notebooks
```

Now you can open and run:
- `01_entsoe_data_analysis.ipynb`
- `02_epex_spot_analysis.ipynb`
- `03_combined_analysis.ipynb`

## What's Next?

### View Your Data

```bash
# Check scraped data
kubectl exec -n data-lab -it $POD -- ls -lh /home/jovyan/data
```

### Schedule Regular Scraping

The CronJob is already configured to run every 6 hours. To change the schedule:

```bash
kubectl edit cronjob entsoe-scraper -n data-lab
# Modify the schedule field (cron format)
```

### Monitor Your Cluster

```bash
# View all resources
kubectl get all -n data-lab

# Check node resources
kubectl top nodes

# Check pod resources
kubectl top pods -n data-lab
```

### Add More Countries

Edit `data-scrapers/entsoe_scraper.py` and add more country codes:

```python
# Scrape multiple countries
scraper.scrape_all_data(country_code='DE', days_back=7)
scraper.scrape_all_data(country_code='FR', days_back=7)
scraper.scrape_all_data(country_code='GB', days_back=7)
```

## Troubleshooting

### k3s Installation Failed

```bash
# Check Ansible logs
ansible-playbook -i ansible/inventory.yml ansible/playbook-k3s-setup.yml -vvv

# Manually check a node
ssh pi@192.168.1.10
sudo systemctl status k3s
sudo journalctl -u k3s -f
```

### Scraper Not Running

```bash
# Check CronJob
kubectl describe cronjob entsoe-scraper -n data-lab

# Check if secret exists
kubectl get secret scraper-secrets -n data-lab

# Check pod logs
kubectl logs -n data-lab -l app=scraper-service
```

### Jupyter Not Accessible

```bash
# Check pod status
kubectl get pods -n data-lab

# Check service
kubectl get svc jupyter-notebook-service -n data-lab

# Check logs
kubectl logs -n data-lab -l app=jupyter-notebook
```

### Need Help?

Check the detailed documentation:
- [K3s Setup](docs/K3S_SETUP.md)
- [Data Scraping](docs/DATA_SCRAPING.md)
- [Jupyter Setup](docs/JUPYTER_SETUP.md)

## Summary

You now have:
- ✅ A 4-node k3s cluster running on Raspberry Pi
- ✅ Automated electricity market data scraping
- ✅ Jupyter notebooks for data analysis
- ✅ Scheduled data collection every 6 hours

Happy analyzing! 📊🔌⚡
