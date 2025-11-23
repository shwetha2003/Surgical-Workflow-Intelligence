"""
Tests for analytical functions
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzer import SurgicalAnalyzer
from data_loader import SurgicalDataLoader

class TestSurgicalAnalyzer:
    """Test cases for SurgicalAnalyzer"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = SurgicalAnalyzer()
        self.loader = SurgicalDataLoader(data_path="test_data/")
        self.procedures, self.tool_metrics, self.notes, self.sensor_data = self.loader.generate_sample_data(50)
    
    def test_tool_performance_correlation(self):
        """Test tool performance correlation analysis"""
        correlations = self.analyzer.analyze_tool_performance_correlation(self.procedures, self.tool_metrics)
        
        assert isinstance(correlations, dict)
        if len(correlations) > 0:
            first_key = list(correlations.keys())[0]
            assert 'correlation' in correlations[first_key]
            assert 'p_value' in correlations[first_key]
    
    def test_outlier_detection(self):
        """Test efficiency outlier detection"""
        outliers = self.analyzer.identify_efficiency_outliers(self.procedures, self.tool_metrics)
        
        assert 'outlier_procedures' in outliers
        assert 'total_outliers' in outliers
        assert isinstance(outliers['outlier_procedures'], dict)
    
    def test_procedure_type_analysis(self):
        """Test procedure type pattern analysis"""
        patterns = self.analyzer.analyze_procedure_type_patterns(self.procedures, self.tool_metrics)
        
        assert isinstance(patterns, dict)
        assert len(patterns) > 0
        first_type = list(patterns.keys())[0]
        assert 'avg_duration' in patterns[first_type]
        assert 'common_tools' in patterns[first_type]
    
    def test_power_analysis(self):
        """Test statistical power analysis"""
        power_results = self.analyzer.perform_power_analysis(self.procedures)
        
        assert isinstance(power_results, dict)
        assert 'effect_size_0.2' in power_results
        assert 'required_sample_size' in power_results['effect_size_0.2']
