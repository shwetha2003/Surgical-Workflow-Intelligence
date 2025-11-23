"""
Tests for data loader functionality
"""

import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import SurgicalDataLoader

class TestSurgicalDataLoader:
    """Test cases for SurgicalDataLoader"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.loader = SurgicalDataLoader(data_path="test_data/")
        self.procedures, self.tool_metrics, self.notes, self.sensor_data = self.loader.generate_sample_data(10)
    
    def test_procedures_data_generation(self):
        """Test procedures data generation"""
        assert len(self.procedures) == 10
        assert 'procedure_id' in self.procedures.columns
        assert 'procedure_type' in self.procedures.columns
        assert 'duration_minutes' in self.procedures.columns
        assert all(self.procedures['duration_minutes'] > 0)
    
    def test_tool_metrics_generation(self):
        """Test tool metrics generation"""
        assert len(self.tool_metrics) > 0
        assert 'tool_type' in self.tool_metrics.columns
        assert 'usage_time_minutes' in self.tool_metrics.columns
        assert all(self.tool_metrics['usage_time_minutes'] > 0)
    
    def test_surgical_notes_generation(self):
        """Test surgical notes generation"""
        assert len(self.notes) == 10
        assert all('procedure_id' in note for note in self.notes)
        assert all('surgeon_notes' in note for note in self.notes)
    
    def test_sensor_data_generation(self):
        """Test sensor data generation"""
        assert len(self.sensor_data) > 0
        assert 'timestamp_minutes' in self.sensor_data.columns
        assert 'force_sensor' in self.sensor_data.columns
    
    def test_data_loading(self):
        """Test data loading from files"""
        procedures_loaded = self.loader.load_procedures_data()
        assert len(procedures_loaded) == 10
        assert all(col in procedures_loaded.columns for col in ['procedure_id', 'procedure_type', 'duration_minutes'])
