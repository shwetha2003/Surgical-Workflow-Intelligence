#!/bin/bash

echo "🚀 Deploying Surgical Workflow Intelligence Platform"

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v

# Generate sample data
python -c "from src.data_loader import SurgicalDataLoader; loader = SurgicalDataLoader(); loader.generate_sample_data(1000)"

echo "✅ Deployment complete! Run with: python dashboards/plotly_dashboard.py"
