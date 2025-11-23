"""
SQL database operations for surgical data
"""
import sqlite3
import pandas as pd
from typing import Optional

class SurgicalDatabase:
    def __init__(self, db_path: str = "data/surgical_analytics.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        
        # Procedures table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS procedures (
                procedure_id TEXT PRIMARY KEY,
                procedure_type TEXT,
                duration_minutes REAL,
                efficiency_score REAL,
                surgeon_experience_yrs INTEGER,
                patient_bmi REAL,
                blood_loss_ml REAL,
                complications INTEGER
            )
        ''')
        
        # Tool metrics table  
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tool_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                procedure_id TEXT,
                tool_type TEXT,
                usage_time_minutes REAL,
                max_force_applied REAL,
                efficiency_rating REAL,
                FOREIGN KEY (procedure_id) REFERENCES procedures (procedure_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_procedures(self, procedures_df: pd.DataFrame):
        """Save procedures data to database"""
        conn = sqlite3.connect(self.db_path)
        procedures_df.to_sql('procedures', conn, if_exists='replace', index=False)
        conn.close()
    
    def query_efficient_procedures(self, min_efficiency: float = 80) -> pd.DataFrame:
        """Query procedures above efficiency threshold"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT * FROM procedures 
            WHERE efficiency_score > ?
            ORDER BY efficiency_score DESC
        """
        result = pd.read_sql_query(query, conn, params=[min_efficiency])
        conn.close()
        return result
