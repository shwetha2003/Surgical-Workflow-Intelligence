#!/bin/bash

echo "🔧 Setting up Surgical Workflow Intelligence Platform..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv || echo "Virtual environment creation failed, continuing..."

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating directory structure..."
mkdir -p data/raw data/processed reports

echo "✅ Setup complete!"
echo "🎯 Next steps:"
echo "   source venv/bin/activate  # Activate virtual environment"
echo "   python -c \"from src.data_loader import SurgicalDataLoader; loader = SurgicalDataLoader(); loader.generate_sample_data(100)\""
echo "   python dashboards/plotly_dashboard.py"
