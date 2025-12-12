# Jupyter Notebook Setup

This guide explains how to set up and access Jupyter notebooks for exploratory data analysis (EDA) of electricity market data.

## Overview

The Jupyter notebook environment provides:
- Interactive data analysis
- Visualization capabilities
- Pre-built notebooks for ENTSO-E and EPEX data
- Access to scraped data

## Local Setup (Development)

### 1. Install Jupyter

```bash
pip install jupyter pandas numpy matplotlib seaborn
```

### 2. Start Jupyter

From the repository root:
```bash
jupyter notebook notebooks/
```

This opens Jupyter in your browser at `http://localhost:8888`.

### 3. Available Notebooks

- **01_entsoe_data_analysis.ipynb**: ENTSO-E data exploration
- **02_epex_spot_analysis.ipynb**: EPEX Spot market analysis
- **03_combined_analysis.ipynb**: Combined multi-market analysis

## Kubernetes Deployment

### 1. Deploy Jupyter to k3s

```bash
kubectl apply -f k3s-setup/jupyter-deployment.yaml
```

This creates:
- Deployment: `jupyter-notebook`
- Service: `jupyter-notebook-service` (NodePort)
- PVC: `jupyter-notebooks-pvc` (5Gi)
- Ingress: `jupyter-ingress` (optional)

### 2. Access Jupyter

#### Option A: NodePort Access

Access Jupyter using any node IP and port 30888:
```
http://192.168.1.10:30888
http://192.168.1.11:30888
http://192.168.1.12:30888
http://192.168.1.13:30888
```

#### Option B: Port Forward (for remote access)

```bash
kubectl port-forward -n data-lab svc/jupyter-notebook-service 8888:8888
```

Then access at: `http://localhost:8888`

### 3. Get Jupyter Token

On first access, you'll need the token:

```bash
# Get pod name
POD=$(kubectl get pod -n data-lab -l app=jupyter-notebook -o jsonpath='{.items[0].metadata.name}')

# Get logs to find token
kubectl logs $POD -n data-lab | grep token
```

Look for a line like:
```
http://127.0.0.1:8888/?token=abc123def456...
```

Copy the token and use it to log in.

### 4. Upload Notebooks

#### Method 1: Copy via kubectl

```bash
# Copy all notebooks to the Jupyter pod
POD=$(kubectl get pod -n data-lab -l app=jupyter-notebook -o jsonpath='{.items[0].metadata.name}')

kubectl cp notebooks/01_entsoe_data_analysis.ipynb \
  data-lab/$POD:/home/jovyan/work/

kubectl cp notebooks/02_epex_spot_analysis.ipynb \
  data-lab/$POD:/home/jovyan/work/

kubectl cp notebooks/03_combined_analysis.ipynb \
  data-lab/$POD:/home/jovyan/work/
```

#### Method 2: Git Clone (Recommended)

Inside Jupyter, open a terminal and:
```bash
cd work
git clone https://github.com/Opulski/home-data-lab.git
cd home-data-lab/notebooks
```

## Using the Notebooks

### 1. ENTSO-E Data Analysis

Open `01_entsoe_data_analysis.ipynb`:

This notebook analyzes:
- Day-ahead electricity prices
- Load patterns
- Generation by type
- Price-load correlations

**Prerequisites**:
- Run the ENTSO-E scraper first to collect data
- Data files in `../data-scrapers/data/`

### 2. EPEX Spot Analysis

Open `02_epex_spot_analysis.ipynb`:

This notebook provides:
- Multi-market price comparison
- Market coupling analysis
- Cross-border price spreads
- Volatility analysis

### 3. Combined Analysis

Open `03_combined_analysis.ipynb`:

Advanced analysis including:
- Price-load relationships
- Renewable generation impact
- Cross-market dynamics
- Temporal patterns

## Data Access in Notebooks

### Local Development

Data is located in `../data-scrapers/data/`:
```python
from pathlib import Path
data_dir = Path('../data-scrapers/data')
```

### Kubernetes Environment

Data is mounted at `/home/jovyan/data`:
```python
from pathlib import Path
data_dir = Path('/home/jovyan/data')
```

The deployment automatically mounts the scraper data PVC.

## Installing Additional Packages

### In Local Environment

```bash
pip install package-name
```

### In Jupyter (Kubernetes)

Open a terminal in Jupyter:
```bash
pip install package-name
```

Or in a notebook cell:
```python
!pip install package-name
```

Common packages for energy data analysis:
```bash
pip install entsoe-py statsmodels scikit-learn plotly
```

## Customizing the Deployment

### Change Jupyter Resources

Edit the deployment:
```bash
kubectl edit deployment jupyter-notebook -n data-lab
```

Update resources:
```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "4000m"
```

### Enable Persistent Notebooks

Notebooks are automatically saved to the PVC. To back them up:
```bash
# Export notebooks
POD=$(kubectl get pod -n data-lab -l app=jupyter-notebook -o jsonpath='{.items[0].metadata.name}')
kubectl cp data-lab/$POD:/home/jovyan/work ./notebook-backup/
```

### Set Password Instead of Token

Create a hashed password:
```python
from notebook.auth import passwd
passwd()
# Enter your password when prompted
# Copy the generated hash
```

Update the deployment with the hash:
```yaml
env:
- name: JUPYTER_TOKEN
  value: ""
- name: JUPYTER_PASSWORD
  value: "sha1:abc123..."  # Your hashed password
```

## Tips for Effective Analysis

### 1. Data Refresh

Before analysis, ensure you have recent data:
```bash
# Trigger manual scraping
kubectl create job --from=cronjob/entsoe-scraper entsoe-manual-1 -n data-lab
```

### 2. Large Datasets

For large datasets, use chunking:
```python
# Read data in chunks
chunksize = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunksize):
    # Process chunk
    pass
```

### 3. Interactive Plots

Use plotly for interactive visualizations:
```python
import plotly.express as px

fig = px.line(df, x='timestamp', y='price', title='Interactive Price Chart')
fig.show()
```

### 4. Export Results

Save analysis results:
```python
# Save figures
plt.savefig('analysis_result.png', dpi=300, bbox_inches='tight')

# Export summary data
summary_df.to_csv('summary.csv')
summary_df.to_excel('summary.xlsx')
```

## Troubleshooting

### Jupyter Not Accessible

Check pod status:
```bash
kubectl get pods -n data-lab
kubectl describe pod <jupyter-pod> -n data-lab
```

Check service:
```bash
kubectl get svc -n data-lab
kubectl describe svc jupyter-notebook-service -n data-lab
```

### Data Not Found

Verify data PVC is mounted:
```bash
POD=$(kubectl get pod -n data-lab -l app=jupyter-notebook -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD -n data-lab -- ls -la /home/jovyan/data
```

### Kernel Crashes

If the kernel dies frequently:
- Increase memory limits in deployment
- Check for memory leaks in your code
- Use data sampling for large datasets

### Slow Performance

Optimize Jupyter:
```python
# Disable progress bars in pandas
pd.set_option('display.notebook_repr_html', False)

# Use efficient data types
df = df.astype({'column': 'float32'})  # Instead of float64
```

## Sharing Notebooks

### Export Notebooks

Download notebooks from Jupyter UI: File → Download as → Notebook (.ipynb)

Or via kubectl:
```bash
POD=$(kubectl get pod -n data-lab -l app=jupyter-notebook -o jsonpath='{.items[0].metadata.name}')
kubectl cp data-lab/$POD:/home/jovyan/work/my_notebook.ipynb ./my_notebook.ipynb
```

### Convert to HTML/PDF

In Jupyter terminal:
```bash
jupyter nbconvert --to html notebook.ipynb
jupyter nbconvert --to pdf notebook.ipynb
```

### Share via Git

```bash
# In Jupyter terminal
cd work
git add my_analysis.ipynb
git commit -m "Add my analysis"
git push
```

## Security Considerations

### Production Deployment

For production:
1. Use authentication (password instead of token)
2. Enable HTTPS via Ingress with TLS
3. Restrict network access
4. Use RBAC for pod access

### Secure Deployment Example

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: jupyter-config
  namespace: data-lab
type: Opaque
stringData:
  jupyter_notebook_config.py: |
    c.NotebookApp.password = 'sha1:...'
    c.NotebookApp.allow_remote_access = True
```

## Next Steps

1. Explore the provided notebooks
2. Create custom analyses for your use case
3. Set up automated reporting
4. Build predictive models

## Resources

- [Jupyter Documentation](https://jupyter.org/documentation)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Matplotlib Gallery](https://matplotlib.org/stable/gallery/)
- [Seaborn Tutorial](https://seaborn.pydata.org/tutorial.html)
