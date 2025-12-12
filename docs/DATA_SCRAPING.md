# Data Scraping Setup

This guide explains how to set up and run the data scrapers for ENTSO-E and EPEX Spot electricity market data.

## Overview

The data scraping infrastructure collects electricity market data from:
1. **ENTSO-E Transparency Platform**: Day-ahead prices, load, generation data
2. **EPEX Spot**: Spot market prices (via ENTSO-E or direct API if available)

## Prerequisites

### API Access
- **ENTSO-E API Key**: Required
  - Register at: https://transparency.entsoe.eu/
  - Navigate to Account Settings → Web API Security Token
  - Generate and save your API key

- **EPEX Spot API**: Optional (data available through ENTSO-E)

## Local Setup (Development/Testing)

### 1. Install Dependencies

```bash
cd data-scrapers
pip install -r requirements.txt
```

### 2. Configure API Credentials

```bash
cp config.env.example config.env
nano config.env
```

Update the following:
```env
ENTSOE_API_KEY=your_actual_api_key_here
DATA_DIR=./data
LOG_DIR=./logs
TIMEZONE=Europe/Berlin
```

### 3. Create Required Directories

```bash
mkdir -p data logs
```

### 4. Run Scrapers

#### ENTSO-E Scraper
```bash
python entsoe_scraper.py
```

This will scrape:
- Day-ahead prices for Germany (past 7 days)
- Actual load data
- Generation by production type

To scrape different countries or time periods, modify the `main()` function in `entsoe_scraper.py`:
```python
scraper.scrape_all_data(country_code='FR', days_back=14)  # France, 14 days
```

#### EPEX Spot Scraper
```bash
python epex_spot_scraper.py
```

**Note**: EPEX Spot data is typically accessible through ENTSO-E. This scraper is a template for direct EPEX API access if you have credentials.

### 5. Verify Data

Check the `data/` directory for CSV files:
```bash
ls -lh data/
```

Example output:
```
day_ahead_prices_DE_20240101_20240108.csv
load_DE_20240101_20240108.csv
generation_DE_20240101_20240108.csv
```

## Kubernetes Deployment

### 1. Build Docker Image

```bash
cd data-scrapers
docker build -t data-scraper:latest .
```

For ARM architecture (Raspberry Pi):
```bash
docker buildx build --platform linux/arm64 -t data-scraper:latest .
```

### 2. Load Image to k3s

On each Raspberry Pi node:
```bash
docker save data-scraper:latest | ssh pi@192.168.1.10 'sudo k3s ctr images import -'
docker save data-scraper:latest | ssh pi@192.168.1.11 'sudo k3s ctr images import -'
docker save data-scraper:latest | ssh pi@192.168.1.12 'sudo k3s ctr images import -'
docker save data-scraper:latest | ssh pi@192.168.1.13 'sudo k3s ctr images import -'
```

### 3. Create Kubernetes Secret

```bash
kubectl create namespace data-lab
kubectl create secret generic scraper-secrets \
  --from-literal=entsoe-api-key=YOUR_ACTUAL_API_KEY \
  --namespace=data-lab
```

### 4. Deploy to Kubernetes

```bash
kubectl apply -f ../k3s-setup/data-scraper-deployment.yaml
```

This creates:
- Namespace: `data-lab`
- PersistentVolumeClaim: `scraper-data-pvc` (10Gi)
- CronJob: Runs every 6 hours
- Deployment: For on-demand scraping

### 5. Verify Deployment

```bash
# Check CronJob
kubectl get cronjob -n data-lab

# Check if PVC is bound
kubectl get pvc -n data-lab

# View logs from last scraping job
kubectl logs -n data-lab -l job-name=entsoe-scraper-xxxxx
```

### 6. Manual Scraping

To run scraper manually:
```bash
# Get into the scraper pod
POD=$(kubectl get pod -n data-lab -l app=scraper-service -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD -n data-lab -- bash

# Inside the pod, run:
python entsoe_scraper.py
```

## Data Storage

### Local Storage
- Data files: `./data/` (CSV format)
- Logs: `./logs/`

### Kubernetes Storage
- PersistentVolume: `/data` (shared across scraper pods)
- Accessible from Jupyter notebooks

## Scheduling

### Default Schedule
- **CronJob**: Every 6 hours (`0 */6 * * *`)

### Modify Schedule

Edit the CronJob:
```bash
kubectl edit cronjob entsoe-scraper -n data-lab
```

Common schedules:
- Every hour: `0 * * * *`
- Every 3 hours: `0 */3 * * *`
- Daily at 2 AM: `0 2 * * *`

## Available Data

### ENTSO-E Data Types

The scraper supports:
- **Day-ahead prices**: Hourly electricity prices
- **Actual load**: Real-time electricity demand
- **Generation by type**: 
  - Solar
  - Wind (onshore/offshore)
  - Hydro
  - Nuclear
  - Fossil fuels
  - Biomass
  - Other renewables

### Supported Countries

ENTSO-E provides data for European countries. Common codes:
- `DE`: Germany
- `FR`: France
- `GB`: Great Britain
- `IT`: Italy
- `ES`: Spain
- `NL`: Netherlands
- `BE`: Belgium
- `AT`: Austria
- `CH`: Switzerland
- `PL`: Poland
- `DK`: Denmark
- `SE`: Sweden
- `NO`: Norway

## Troubleshooting

### API Rate Limiting

ENTSO-E API has rate limits. If you encounter errors:
- Reduce scraping frequency
- Scrape smaller time periods
- Add delays between requests

### Missing Data

Some data may not be available for all countries/time periods:
```python
# The scraper handles missing data gracefully
# Check logs for warnings about unavailable data
```

### Permission Errors

If you get permission errors in Kubernetes:
```bash
# Check PVC permissions
kubectl describe pvc scraper-data-pvc -n data-lab

# Check pod security context
kubectl get pod -n data-lab -o yaml
```

## Data Format

### CSV Structure

All data is saved as CSV files with timestamps as index:

```csv
timestamp,price
2024-01-01 00:00:00+00:00,45.23
2024-01-01 01:00:00+00:00,42.15
```

### Loading Data in Python

```python
import pandas as pd

# Load price data
prices = pd.read_csv('data/day_ahead_prices_DE_20240101_20240108.csv', 
                     index_col=0, parse_dates=True)

# Load generation data
generation = pd.read_csv('data/generation_DE_20240101_20240108.csv',
                         index_col=0, parse_dates=True)
```

## Next Steps

1. Set up Jupyter notebooks for data analysis: [JUPYTER_SETUP.md](JUPYTER_SETUP.md)
2. Explore the data with the provided notebooks
3. Set up data visualization dashboards

## Resources

- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
- [entsoe-py Documentation](https://github.com/EnergieID/entsoe-py)
- [ENTSO-E API Guide](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
