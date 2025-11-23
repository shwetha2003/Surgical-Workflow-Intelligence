"""
Data loading utilities for surgical workflow data.
Handles both structured and unstructured data formats.
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Tuple
from faker import Faker
from datetime import datetime, timedelta
import random

class SurgicalDataLoader:
    """Loader for surgical procedure and tool data"""
    
    def __init__(self, data_path: str = "data/"):
        self.data_path = data_path
        self.fake = Faker()
        np.random.seed(42)
        random.seed(42)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(f"{self.data_path}/raw", exist_ok=True)
        os.makedirs(f"{self.data_path}/processed", exist_ok=True)
    
    def generate_sample_data(self, num_procedures: int = 500):
        """Generate synthetic surgical data for demonstration"""
        print("Generating sample surgical data...")
        
        # Generate procedures data
        procedures = self._generate_procedures_data(num_procedures)
        procedures.to_csv(f"{self.data_path}/raw/procedures.csv", index=False)
        
        # Generate tool metrics data
        tool_metrics = self._generate_tool_metrics_data(procedures)
        tool_metrics.to_csv(f"{self.data_path}/raw/tool_metrics.csv", index=False)
        
        # Generate surgical notes
        surgical_notes = self._generate_surgical_notes(procedures)
        with open(f"{self.data_path}/raw/surgical_notes.json", 'w') as f:
            json.dump(surgical_notes, f, indent=2)
        
        # Generate time series sensor data
        sensor_data = self._generate_sensor_data(procedures)
        sensor_data.to_csv(f"{self.data_path}/raw/sensor_data.csv", index=False)
        
        print(f"Generated data for {num_procedures} procedures")
        return procedures, tool_metrics, surgical_notes, sensor_data
    
    def _generate_procedures_data(self, num_procedures: int) -> pd.DataFrame:
        """Generate procedure metadata"""
        procedure_types = ['Laparoscopic Cholecystectomy', 'Bariatric Surgery', 
                          'Colorectal Surgery', 'Hernia Repair', 'GI Surgery']
        
        data = []
        for i in range(num_procedures):
            procedure_type = np.random.choice(procedure_types)
            base_duration = 120 if 'Laparoscopic' in procedure_type else 180
            
            procedure = {
                'procedure_id': f"PROC_{i:04d}",
                'procedure_type': procedure_type,
                'duration_minutes': max(45, np.random.normal(base_duration, 30)),
                'efficiency_score': max(60, min(100, np.random.normal(80, 12))),
                'surgeon_experience_yrs': np.random.randint(1, 25),
                'patient_bmi': max(18, min(45, np.random.normal(28, 6))),
                'blood_loss_ml': max(10, np.random.gamma(2, 40)),
                'complications': np.random.choice([0, 1], p=[0.92, 0.08]),
                'surgical_site': np.random.choice(['Abdominal', 'Thoracic', 'Pelvic']),
                'instrument_changes': np.random.poisson(3)
            }
            data.append(procedure)
        
        return pd.DataFrame(data)
    
    def _generate_tool_metrics_data(self, procedures: pd.DataFrame) -> pd.DataFrame:
        """Generate tool usage metrics"""
        tools = ['Harmonic Scalpel', 'Ligasure', 'Robotic Grasper', 
                'Electrosurgical Pencil', 'Stapler', 'Suction/Irrigation']
        
        data = []
        for _, procedure in procedures.iterrows():
            num_tool_uses = np.random.randint(3, 8)
            tools_used = np.random.choice(tools, num_tool_uses, replace=False)
            
            for tool in tools_used:
                usage_time = np.random.uniform(5, 45)
                max_force = np.random.gamma(2, 2)
                avg_temperature = np.random.normal(45, 10)
                
                tool_data = {
                    'procedure_id': procedure['procedure_id'],
                    'tool_type': tool,
                    'usage_time_minutes': usage_time,
                    'max_force_applied': max_force,
                    'avg_temperature_c': avg_temperature,
                    'activation_count': np.random.poisson(15),
                    'efficiency_rating': np.random.normal(7, 1.5),
                    'tissue_sticking_incidents': np.random.poisson(0.5)
                }
                data.append(tool_data)
        
        return pd.DataFrame(data)
    
    def _generate_surgical_notes(self, procedures: pd.DataFrame) -> List[Dict]:
        """Generate unstructured surgical notes"""
        notes = []
        complications_list = [
            "Minimal bleeding controlled with electrocautery",
            "Some adhesions encountered, carefully dissected",
            "Clear anatomy, straightforward procedure",
            "Challoscopic anatomy, required careful dissection",
            "Dense adhesions present, took additional time",
            "Good hemostasis throughout",
            "Some instrument fogging encountered",
            "Tissue sticking to instrument tip occasionally"
        ]
        
        for _, procedure in procedures.iterrows():
            note = {
                'procedure_id': procedure['procedure_id'],
                'surgeon_notes': np.random.choice(complications_list),
                'nurse_notes': f"Patient tolerated procedure well. Estimated blood loss {procedure['blood_loss_ml']}ml.",
                'anesthesia_notes': "Stable hemodynamics throughout case.",
                'difficulty_rating': np.random.randint(1, 6),
                'key_observations': self._generate_observations(procedure)
            }
            notes.append(note)
        
        return notes
    
    def _generate_observations(self, procedure: pd.Series) -> str:
        """Generate realistic surgical observations"""
        observations = []
        
        if procedure['blood_loss_ml'] > 200:
            observations.append("Higher than average blood loss")
        if procedure['duration_minutes'] > 180:
            observations.append("Longer procedure duration")
        if procedure['complications'] == 1:
            observations.append("Minor complications noted")
        if procedure['patient_bmi'] > 35:
            observations.append("Challenging anatomy due to BMI")
            
        return "; ".join(observations) if observations else "Standard procedure"
    
    def _generate_sensor_data(self, procedures: pd.DataFrame) -> pd.DataFrame:
        """Generate time-series sensor data for a subset of procedures"""
        data = []
        sample_procedures = procedures.sample(min(50, len(procedures)))
        
        for _, procedure in sample_procedures.iterrows():
            duration = int(procedure['duration_minutes'])
            time_points = range(0, duration, 2)  # Data every 2 minutes
            
            for minute in time_points:
                sensor_data = {
                    'procedure_id': procedure['procedure_id'],
                    'timestamp_minutes': minute,
                    'force_sensor': max(0, np.random.normal(2, 0.8)),
                    'temperature': np.random.normal(37, 3),
                    'motor_current': np.random.normal(1.5, 0.4),
                    'vibration': np.random.gamma(1, 0.5),
                    'pressure': np.random.normal(12, 2)
                }
                data.append(sensor_data)
        
        return pd.DataFrame(data)
    
    def load_procedures_data(self) -> pd.DataFrame:
        """Load procedures data from CSV"""
        return pd.read_csv(f"{self.data_path}/raw/procedures.csv")
    
    def load_tool_metrics(self) -> pd.DataFrame:
        """Load tool metrics data from CSV"""
        return pd.read_csv(f"{self.data_path}/raw/tool_metrics.csv")
    
    def load_surgical_notes(self) -> List[Dict]:
        """Load surgical notes from JSON"""
        with open(f"{self.data_path}/raw/surgical_notes.json", 'r') as f:
            return json.load(f)
    
    def load_sensor_data(self) -> pd.DataFrame:
        """Load sensor data from CSV"""
        return pd.read_csv(f"{self.data_path}/raw/sensor_data.csv")
