"""
Analytical functions for surgical workflow data.
Includes statistical analysis and machine learning models.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import scipy.stats as stats
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')

class SurgicalAnalyzer:
    """Main analyzer class for surgical workflow data"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.procedure_cluster_model = None
        self.outlier_detector = None
    
    def analyze_tool_performance_correlation(self, procedures: pd.DataFrame, tool_metrics: pd.DataFrame) -> Dict:
        """Analyze correlations between tool usage and procedure outcomes"""
        
        # Merge data
        merged_data = procedures.merge(
            tool_metrics.groupby('procedure_id').agg({
                'usage_time_minutes': 'sum',
                'max_force_applied': 'mean',
                'avg_temperature_c': 'mean',
                'efficiency_rating': 'mean'
            }).reset_index(),
            on='procedure_id'
        )
        
        # Calculate correlations
        correlations = {}
        metrics = ['duration_minutes', 'efficiency_score', 'blood_loss_ml', 'complications']
        tool_features = ['usage_time_minutes', 'max_force_applied', 'avg_temperature_c', 'efficiency_rating']
        
        for metric in metrics:
            for feature in tool_features:
                corr, p_value = stats.pearsonr(merged_data[feature], merged_data[metric])
                if abs(corr) > 0.1:  # Only report meaningful correlations
                    correlations[f"{feature}_{metric}"] = {
                        'correlation': corr,
                        'p_value': p_value,
                        'interpretation': self._interpret_correlation(corr, feature, metric)
                    }
        
        return correlations
    
    def _interpret_correlation(self, corr: float, feature: str, metric: str) -> str:
        """Provide human-readable interpretation of correlations"""
        strength = "strong" if abs(corr) > 0.5 else "moderate" if abs(corr) > 0.3 else "weak"
        direction = "positive" if corr > 0 else "negative"
        
        interpretations = {
            'max_force_applied_duration_minutes': f"{strength} {direction} relationship between maximum force and procedure duration",
            'efficiency_rating_efficiency_score': f"{strength} {direction} relationship between tool efficiency and overall procedure efficiency",
            'usage_time_minutes_blood_loss_ml': f"{strength} {direction} relationship between tool usage time and blood loss"
        }
        
        key = f"{feature}_{metric}"
        return interpretations.get(key, f"{strength} {direction} correlation")
    
    def detect_surgical_phases(self, sensor_data: pd.DataFrame, n_clusters: int = 4) -> Dict:
        """Use clustering to detect phases in surgical procedures"""
        
        # Prepare features for clustering
        phase_features = sensor_data.groupby(['procedure_id', 'timestamp_minutes']).agg({
            'force_sensor': 'mean',
            'motor_current': 'mean',
            'vibration': 'mean',
            'pressure': 'mean'
        }).reset_index()
        
        # Normalize features
        feature_cols = ['force_sensor', 'motor_current', 'vibration', 'pressure']
        X = phase_features[feature_cols]
        X_scaled = self.scaler.fit_transform(X)
        
        # Apply K-means clustering
        self.procedure_cluster_model = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = self.procedure_cluster_model.fit_predict(X_scaled)
        phase_features['phase'] = clusters
        
        # Calculate phase characteristics
        phase_summary = {}
        for phase in range(n_clusters):
            phase_data = phase_features[phase_features['phase'] == phase]
            phase_summary[phase] = {
                'phase_name': self._name_surgical_phase(phase, phase_data[feature_cols].mean().to_dict()),
                'avg_duration_minutes': phase_data.groupby('procedure_id')['timestamp_minutes'].count().mean() * 2,  # 2-minute intervals
                'avg_force': phase_data['force_sensor'].mean(),
                'avg_motor_current': phase_data['motor_current'].mean(),
                'n_procedures': phase_data['procedure_id'].nunique()
            }
        
        return {
            'phase_assignments': phase_features,
            'phase_summary': phase_summary,
            'silhouette_score': silhouette_score(X_scaled, clusters)
        }
    
    def _name_surgical_phase(self, phase_id: int, phase_stats: Dict) -> str:
        """Assign meaningful names to detected surgical phases"""
        force = phase_stats.get('force_sensor', 0)
        current = phase_stats.get('motor_current', 0)
        
        if force < 1.0 and current < 1.0:
            return "Setup/Preparation"
        elif force > 2.0 and current > 1.8:
            return "Active Dissection"
        elif force > 1.5 and current < 1.5:
            return "Precise Manipulation"
        else:
            return "Closure/Finishing"
    
    def identify_efficiency_outliers(self, procedures: pd.DataFrame, tool_metrics: pd.DataFrame) -> Dict:
        """Identify procedures with unusual efficiency patterns"""
        
        # Create efficiency features
        efficiency_data = procedures.merge(
            tool_metrics.groupby('procedure_id').agg({
                'usage_time_minutes': 'sum',
                'efficiency_rating': 'mean',
                'tissue_sticking_incidents': 'sum'
            }).reset_index(),
            on='procedure_id'
        )
        
        # Select features for outlier detection
        outlier_features = ['duration_minutes', 'efficiency_score', 'usage_time_minutes', 
                          'efficiency_rating', 'blood_loss_ml', 'instrument_changes']
        X = efficiency_data[outlier_features]
        X_scaled = self.scaler.fit_transform(X)
        
        # Use Isolation Forest for outlier detection
        self.outlier_detector = IsolationForest(contamination=0.1, random_state=42)
        outliers = self.outlier_detector.fit_predict(X_scaled)
        
        efficiency_data['is_outlier'] = outliers == -1
        outlier_procedures = efficiency_data[efficiency_data['is_outlier']]
        
        # Analyze outlier characteristics
        outlier_analysis = {}
        for _, procedure in outlier_procedures.iterrows():
            proc_id = procedure['procedure_id']
            outlier_analysis[proc_id] = {
                'procedure_type': procedure['procedure_type'],
                'duration': procedure['duration_minutes'],
                'efficiency_score': procedure['efficiency_score'],
                'blood_loss': procedure['blood_loss_ml'],
                'likely_causes': self._identify_outlier_causes(procedure)
            }
        
        return {
            'outlier_procedures': outlier_analysis,
            'total_outliers': len(outlier_procedures),
            'outlier_rate': len(outlier_procedures) / len(efficiency_data)
        }
    
    def _identify_outlier_causes(self, procedure: pd.Series) -> List[str]:
        """Identify potential causes for efficiency outliers"""
        causes = []
        
        if procedure['duration_minutes'] > 200:
            causes.append("Extended procedure duration")
        if procedure['efficiency_score'] < 60:
            causes.append("Low efficiency score")
        if procedure['blood_loss_ml'] > 300:
            causes.append("High blood loss")
        if procedure['instrument_changes'] > 6:
            causes.append("Frequent instrument changes")
            
        return causes if causes else ["Complex case factors"]
    
    def analyze_procedure_type_patterns(self, procedures: pd.DataFrame, tool_metrics: pd.DataFrame) -> Dict:
        """Analyze patterns across different procedure types"""
        
        analysis = {}
        procedure_types = procedures['procedure_type'].unique()
        
        for proc_type in procedure_types:
            type_data = procedures[procedures['procedure_type'] == proc_type]
            type_tools = tool_metrics[tool_metrics['procedure_id'].isin(type_data['procedure_id'])]
            
            analysis[proc_type] = {
                'avg_duration': type_data['duration_minutes'].mean(),
                'avg_efficiency': type_data['efficiency_score'].mean(),
                'complication_rate': type_data['complications'].mean(),
                'common_tools': type_tools['tool_type'].value_counts().head(3).to_dict(),
                'avg_tool_usage_time': type_tools['usage_time_minutes'].mean(),
                'n_procedures': len(type_data)
            }
        
        return analysis
    
    def perform_power_analysis(self, procedures: pd.DataFrame, metric: str = 'efficiency_score') -> Dict:
        """Perform statistical power analysis for clinical trials"""
        
        effect_sizes = [0.2, 0.5, 0.8]  # Small, medium, large effects
        power_analysis = {}
        
        for effect_size in effect_sizes:
            # Simplified power calculation
            required_n = int(16 / (effect_size ** 2))  # Basic formula for t-test
            
            power_analysis[f"effect_size_{effect_size}"] = {
                'effect_size': effect_size,
                'required_sample_size': required_n,
                'interpretation': f"Requires {required_n} procedures to detect {effect_size} effect size with 80% power"
            }
        
        return power_analysis
