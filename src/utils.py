"""
Utility functions for the surgical workflow intelligence platform.
"""

import pandas as pd
import numpy as np
import json
from typing import Dict, Any, List
import logging
from datetime import datetime
import os

def setup_logging(log_file: str = "surgical_analysis.log"):
    """Set up logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def save_analysis_results(results: Dict, filename: str):
    """Save analysis results to JSON file"""
    os.makedirs('data/processed', exist_ok=True)
    
    # Convert numpy types to Python native types for JSON serialization
    def convert_numpy_types(obj):
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(item) for item in obj]
        return obj
    
    results_serializable = convert_numpy_types(results)
    
    with open(f'data/processed/{filename}', 'w') as f:
        json.dump(results_serializable, f, indent=2, default=str)
    
    logging.info(f"Results saved to data/processed/{filename}")

def load_analysis_results(filename: str) -> Dict:
    """Load analysis results from JSON file"""
    with open(f'data/processed/{filename}', 'r') as f:
        return json.load(f)

def calculate_procedure_statistics(procedures: pd.DataFrame) -> Dict[str, Any]:
    """Calculate comprehensive statistics for procedures"""
    stats = {
        'total_procedures': len(procedures),
        'procedure_types': procedures['procedure_type'].value_counts().to_dict(),
        'avg_duration_minutes': procedures['duration_minutes'].mean(),
        'avg_efficiency_score': procedures['efficiency_score'].mean(),
        'complication_rate': procedures['complications'].mean(),
        'avg_blood_loss_ml': procedures['blood_loss_ml'].mean(),
        'surgeon_experience_stats': {
            'min': procedures['surgeon_experience_yrs'].min(),
            'max': procedures['surgeon_experience_yrs'].max(),
            'mean': procedures['surgeon_experience_yrs'].mean()
        }
    }
    return stats

def validate_data_quality(procedures: pd.DataFrame, tool_metrics: pd.DataFrame) -> Dict:
    """Perform data quality validation checks"""
    issues = []
    
    # Check for missing values
    procedure_missing = procedures.isnull().sum().sum()
    tool_missing = tool_metrics.isnull().sum().sum()
    
    if procedure_missing > 0:
        issues.append(f"Procedures data has {procedure_missing} missing values")
    if tool_missing > 0:
        issues.append(f"Tool metrics has {tool_missing} missing values")
    
    # Check for unrealistic values
    unrealistic_duration = procedures[procedures['duration_minutes'] > 480]  # 8 hours
    if len(unrealistic_duration) > 0:
        issues.append(f"Found {len(unrealistic_duration)} procedures with duration > 8 hours")
    
    unrealistic_efficiency = procedures[procedures['efficiency_score'] > 100]
    if len(unrealistic_efficiency) > 0:
        issues.append(f"Found {len(unrealistic_efficiency)} procedures with efficiency > 100%")
    
    return {
        'has_issues': len(issues) > 0,
        'issues': issues,
        'procedure_records': len(procedures),
        'tool_records': len(tool_metrics)
    }

def export_analysis_report(analysis_results: Dict, filename: str = "analysis_report.md"):
    """Export a comprehensive analysis report in Markdown format"""
    
    report = f"""# Surgical Workflow Analysis Report

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This report summarizes insights from the analysis of {analysis_results.get('total_procedures', 'N/A')} surgical procedures.

## Key Findings

### Procedure Statistics
- **Total Procedures Analyzed**: {analysis_results.get('total_procedures', 'N/A')}
- **Average Procedure Duration**: {analysis_results.get('avg_duration', 0):.1f} minutes
- **Average Efficiency Score**: {analysis_results.get('avg_efficiency', 0):.1f}%
- **Complication Rate**: {analysis_results.get('complication_rate', 0)*100:.1f}%

### Tool Performance Insights
"""

    # Add tool performance insights
    if 'tool_correlations' in analysis_results:
        report += "\n### Tool Performance Correlations\n"
        for corr_name, corr_data in list(analysis_results['tool_correlations'].items())[:5]:
            report += f"- {corr_data.get('interpretation', 'Correlation found')} (r = {corr_data.get('correlation', 0):.3f})\n"

    # Add outlier analysis
    if 'outlier_analysis' in analysis_results:
        outlier_data = analysis_results['outlier_analysis']
        report += f"\n### Efficiency Outliers\n"
        report += f"- **Outliers Identified**: {outlier_data.get('total_outliers', 0)}\n"
        report += f"- **Outlier Rate**: {outlier_data.get('outlier_rate', 0)*100:.1f}%\n"

    # Add phase analysis
    if 'phase_analysis' in analysis_results:
        phase_data = analysis_results['phase_analysis']
        report += f"\n### Surgical Phase Analysis\n"
        report += f"- **Phase Detection Quality**: Silhouette Score = {phase_data.get('silhouette_score', 0):.3f}\n"
        
        if 'phase_summary' in phase_data:
            for phase_id, phase_info in phase_data['phase_summary'].items():
                report += f"- **{phase_info.get('phase_name', 'Phase')}**: {phase_info.get('avg_duration_minutes', 0):.1f} minutes average\n"

    report += f"""
## Recommendations

1. **Tool Optimization**: Consider redesigning tools showing high correlation with extended procedure times
2. **Training Focus**: Develop targeted training for procedures with higher complication rates
3. **Process Improvement**: Analyze outlier procedures to identify best practices and areas for improvement

## Data Quality

- **Data Validation**: { 'PASSED' if not analysis_results.get('data_quality', {}).get('has_issues', True) else 'ISSUES FOUND' }
- **Records Processed**: {analysis_results.get('data_quality', {}).get('procedure_records', 0)} procedures, {analysis_results.get('data_quality', {}).get('tool_records', 0)} tool usage records
"""

    os.makedirs('reports', exist_ok=True)
    with open(f'reports/{filename}', 'w') as f:
        f.write(report)
    
    logging.info(f"Analysis report saved to reports/{filename}")
    return report
