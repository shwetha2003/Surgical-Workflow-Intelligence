"""
Interactive Plotly Dash dashboard for surgical workflow intelligence
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import SurgicalDataLoader
from analyzer import SurgicalAnalyzer
from visualizer import SurgicalVisualizer

# Initialize components
loader = SurgicalDataLoader()
analyzer = SurgicalAnalyzer()
visualizer = SurgicalVisualizer()

# Load sample data
print("Loading data...")
procedures, tool_metrics, surgical_notes, sensor_data = loader.generate_sample_data(200)

# Perform initial analysis
print("Performing initial analysis...")
correlations = analyzer.analyze_tool_performance_correlation(procedures, tool_metrics)
outliers = analyzer.identify_efficiency_outliers(procedures, tool_metrics)
procedure_patterns = analyzer.analyze_procedure_type_patterns(procedures, tool_metrics)

# Create initial figures
efficiency_fig = visualizer.create_procedure_efficiency_dashboard(procedures, tool_metrics)
outlier_fig = visualizer.create_outlier_analysis_plot(outliers, procedures)
heatmap_fig = visualizer.create_tool_performance_heatmap(tool_metrics)

# Initialize Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("Surgical Workflow Intelligence Platform", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30})
    ]),
    
    # Overview Stats
    html.Div([
        html.Div([
            html.H3(f"{len(procedures)}", style={'color': '#3498db', 'margin': 0}),
            html.P("Procedures Analyzed", style={'margin': 0})
        ], className='stat-card', style={'flex': 1, 'textAlign': 'center', 'padding': '20px', 'margin': '10px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3(f"{len(tool_metrics)}", style={'color': '#e74c3c', 'margin': 0}),
            html.P("Tool Usage Records", style={'margin': 0})
        ], className='stat-card', style={'flex': 1, 'textAlign': 'center', 'padding': '20px', 'margin': '10px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
        
        html.Div([
            html.H3(f"{outliers['total_outliers']}", style={'color': '#f39c12', 'margin': 0}),
            html.P("Efficiency Outliers", style={'margin': 0})
        ], className='stat-card', style={'flex': 1, 'textAlign': 'center', 'padding': '20px', 'margin': '10px', 'backgroundColor': '#ecf0f1', 'borderRadius': '10px'}),
    ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 30}),
    
    # Main Visualization
    html.Div([
        dcc.Graph(
            id='efficiency-dashboard',
            figure=efficiency_fig,
            style={'height': '800px'}
        )
    ], style={'marginBottom': 30}),
    
    # Secondary Visualizations
    html.Div([
        html.Div([
            dcc.Graph(
                id='outlier-analysis',
                figure=outlier_fig,
                style={'height': '500px'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        
        html.Div([
            dcc.Graph(
                id='tool-heatmap',
                figure=heatmap_fig,
                style={'height': '500px'}
            )
        ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'})
    ]),
    
    # Procedure Type Selector
    html.Div([
        dcc.Dropdown(
            id='procedure-type-selector',
            options=[{'label': proc_type, 'value': proc_type} for proc_type in procedures['procedure_type'].unique()],
            value=procedures['procedure_type'].iloc[0],
            style={'width': '50%', 'margin': '20px auto'}
        )
    ], style={'textAlign': 'center'}),
    
    # Real-time Monitoring Section
    html.Div([
        html.H2("Real-time Monitoring Simulation", style={'textAlign': 'center', 'color': '#2c3e50'}),
        html.Button('Update Real-time Data', id='update-button', n_clicks=0,
                   style={'margin': '20px auto', 'display': 'block', 'padding': '10px 20px'}),
        dcc.Graph(id='real-time-monitoring')
    ], style={'marginTop': 50}),
    
    # Analysis Summary
    html.Div([
        html.H2("Key Insights", style={'color': '#2c3e50'}),
        html.Ul([
            html.Li(f"Found {outliers['total_outliers']} procedures with unusual efficiency patterns"),
            html.Li(f"Average procedure duration: {procedures['duration_minutes'].mean():.1f} minutes"),
            html.Li(f"Overall efficiency score: {procedures['efficiency_score'].mean():.1f}%"),
            html.Li(f"Complication rate: {procedures['complications'].mean()*100:.1f}%")
        ], style={'fontSize': '18px', 'lineHeight': '1.6'})
    ], style={'backgroundColor': '#f8f9fa', 'padding': '30px', 'borderRadius': '10px', 'marginTop': 30})
])

@callback(
    Output('real-time-monitoring', 'figure'),
    Input('update-button', 'n_clicks')
)
def update_real_time_monitoring(n_clicks):
    """Update real-time monitoring simulation"""
    return visualizer.create_real_time_monitoring_simulation(sensor_data)

if __name__ == '__main__':
    print("Starting dashboard...")
    print("Open http://localhost:8050 in your browser")
    app.run_server(debug=True, host='127.0.0.1', port=8050)
