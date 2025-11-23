"""
Visualization utilities for surgical workflow data.
Creates interactive plots and dashboards.
"""

import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List
import json

class SurgicalVisualizer:
    """Creates visualizations for surgical workflow analysis"""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
        plt.style.use('seaborn-v0_8')
    
    def create_procedure_efficiency_dashboard(self, procedures: pd.DataFrame, tool_metrics: pd.DataFrame) -> go.Figure:
        """Create comprehensive procedure efficiency dashboard"""
        
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Procedure Duration vs Efficiency',
                'Tool Usage Patterns',
                'Complications by Procedure Type', 
                'Surgeon Experience Impact'
            ],
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Plot 1: Duration vs Efficiency
        fig.add_trace(
            go.Scatter(
                x=procedures['duration_minutes'],
                y=procedures['efficiency_score'],
                mode='markers',
                marker=dict(
                    size=8,
                    color=procedures['blood_loss_ml'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Blood Loss (ml)")
                ),
                text=procedures['procedure_type'],
                name='Duration vs Efficiency'
            ),
            row=1, col=1
        )
        
        # Plot 2: Tool usage patterns
        tool_summary = tool_metrics.groupby('tool_type').agg({
            'usage_time_minutes': 'mean',
            'efficiency_rating': 'mean'
        }).reset_index()
        
        fig.add_trace(
            go.Bar(
                x=tool_summary['tool_type'],
                y=tool_summary['usage_time_minutes'],
                name='Avg Usage Time',
                marker_color=self.color_palette[0]
            ),
            row=1, col=2
        )
        
        # Plot 3: Complications by procedure type
        complications_by_type = procedures.groupby('procedure_type')['complications'].mean().reset_index()
        
        fig.add_trace(
            go.Bar(
                x=complications_by_type['procedure_type'],
                y=complications_by_type['complications'] * 100,
                name='Complication Rate %',
                marker_color=self.color_palette[2]
            ),
            row=2, col=1
        )
        
        # Plot 4: Surgeon experience impact
        experience_bins = pd.cut(procedures['surgeon_experience_yrs'], bins=[0, 5, 10, 25])
        experience_impact = procedures.groupby(experience_bins)['efficiency_score'].mean()
        
        fig.add_trace(
            go.Scatter(
                x=[f"{int(bin.left)}-{int(bin.right)}yrs" for bin in experience_impact.index],
                y=experience_impact.values,
                mode='lines+markers',
                name='Experience Impact',
                line=dict(color=self.color_palette[4], width=3)
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="Surgical Procedure Efficiency Analysis",
            showlegend=False
        )
        
        return fig
    
    def create_surgical_phase_visualization(self, phase_analysis: Dict) -> go.Figure:
        """Visualize detected surgical phases"""
        
        phase_summary = phase_analysis['phase_summary']
        phases = list(phase_summary.keys())
        phase_names = [phase_summary[phase]['phase_name'] for phase in phases]
        durations = [phase_summary[phase]['avg_duration_minutes'] for phase in phases]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=phase_names,
            y=durations,
            marker_color=self.color_palette,
            text=[f"{dur:.1f} min" for dur in durations],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Detected Surgical Phases - Average Duration",
            xaxis_title="Surgical Phase",
            yaxis_title="Average Duration (minutes)",
            showlegend=False
        )
        
        return fig
    
    def create_outlier_analysis_plot(self, outlier_analysis: Dict, procedures: pd.DataFrame) -> go.Figure:
        """Visualize procedure outliers"""
        
        outlier_ids = list(outlier_analysis['outlier_procedures'].keys())
        outlier_data = procedures[procedures['procedure_id'].isin(outlier_ids)]
        normal_data = procedures[~procedures['procedure_id'].isin(outlier_ids)]
        
        fig = go.Figure()
        
        # Normal procedures
        fig.add_trace(go.Scatter(
            x=normal_data['duration_minutes'],
            y=normal_data['efficiency_score'],
            mode='markers',
            name='Normal Procedures',
            marker=dict(color='blue', size=8, opacity=0.6)
        ))
        
        # Outlier procedures
        fig.add_trace(go.Scatter(
            x=outlier_data['duration_minutes'],
            y=outlier_data['efficiency_score'],
            mode='markers',
            name='Efficiency Outliers',
            marker=dict(color='red', size=12, symbol='x')
        ))
        
        fig.update_layout(
            title="Procedure Efficiency Outlier Detection",
            xaxis_title="Duration (minutes)",
            yaxis_title="Efficiency Score",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return fig
    
    def create_tool_performance_heatmap(self, tool_metrics: pd.DataFrame) -> go.Figure:
        """Create heatmap of tool performance metrics"""
        
        tool_performance = tool_metrics.groupby('tool_type').agg({
            'usage_time_minutes': 'mean',
            'efficiency_rating': 'mean',
            'max_force_applied': 'mean',
            'tissue_sticking_incidents': 'mean'
        }).round(2)
        
        fig = px.imshow(
            tool_performance.T,
            text_auto=True,
            aspect="auto",
            color_continuous_scale='Blues',
            title="Tool Performance Metrics Heatmap"
        )
        
        fig.update_layout(
            xaxis_title="Tool Type",
            yaxis_title="Performance Metric"
        )
        
        return fig
    
    def create_real_time_monitoring_simulation(self, sensor_data: pd.DataFrame) -> go.Figure:
        """Simulate real-time monitoring dashboard"""
        
        # Sample one procedure for demonstration
        sample_procedure = sensor_data['procedure_id'].iloc[0]
        procedure_data = sensor_data[sensor_data['procedure_id'] == sample_procedure]
        
        fig = sp.make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Force Sensor Readings',
                'Motor Current',
                'Temperature Profile',
                'Vibration Levels'
            ]
        )
        
        # Force sensor
        fig.add_trace(
            go.Scatter(
                x=procedure_data['timestamp_minutes'],
                y=procedure_data['force_sensor'],
                mode='lines',
                name='Force',
                line=dict(color='red', width=2)
            ),
            row=1, col=1
        )
        
        # Motor current
        fig.add_trace(
            go.Scatter(
                x=procedure_data['timestamp_minutes'],
                y=procedure_data['motor_current'],
                mode='lines',
                name='Motor Current',
                line=dict(color='blue', width=2)
            ),
            row=1, col=2
        )
        
        # Temperature
        fig.add_trace(
            go.Scatter(
                x=procedure_data['timestamp_minutes'],
                y=procedure_data['temperature'],
                mode='lines',
                name='Temperature',
                line=dict(color='orange', width=2)
            ),
            row=2, col=1
        )
        
        # Vibration
        fig.add_trace(
            go.Scatter(
                x=procedure_data['timestamp_minutes'],
                y=procedure_data['vibration'],
                mode='lines',
                name='Vibration',
                line=dict(color='green', width=2)
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            title_text=f"Real-time Monitoring Simulation - Procedure {sample_procedure}",
            showlegend=False
        )
        
        return fig
