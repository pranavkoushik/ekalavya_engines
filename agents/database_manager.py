import sqlite3
import pandas as pd
import os
from typing import Dict, List, Any
import json

class DatabaseManager:
    def __init__(self, db_path: str = 'chatbot.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Create a database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            cursor = self.conn.cursor()
            
            # Table for storing datasets
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')

            # Table for storing analysis results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER,
                    analysis_type TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                )
            ''')

            # Table for storing visualizations
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visualizations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER,
                    viz_type TEXT NOT NULL,
                    config TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                )
            ''')

            self.conn.commit()
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            raise

    def store_dataset(self, name: str, df: pd.DataFrame, description: str = None) -> int:
        """Store dataset metadata and create table for the data"""
        try:
            cursor = self.conn.cursor()
            
            # Store dataset metadata
            metadata = {
                'columns': list(df.columns),
                'rows': len(df),
                'dtypes': df.dtypes.astype(str).to_dict()
            }
            
            cursor.execute('''
                INSERT INTO datasets (name, description, metadata)
                VALUES (?, ?, ?)
            ''', (name, description, json.dumps(metadata)))
            
            dataset_id = cursor.lastrowid
            
            # Create table for the dataset
            table_name = f"dataset_{dataset_id}"
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            
            self.conn.commit()
            return dataset_id
        except Exception as e:
            print(f"Error storing dataset: {str(e)}")
            raise

    def get_dataset(self, dataset_id: int) -> pd.DataFrame:
        """Retrieve dataset as pandas DataFrame"""
        try:
            table_name = f"dataset_{dataset_id}"
            return pd.read_sql(f"SELECT * FROM {table_name}", self.conn)
        except Exception as e:
            print(f"Error retrieving dataset: {str(e)}")
            raise

    def store_analysis(self, dataset_id: int, analysis_type: str, result: Dict[str, Any]) -> int:
        """Store analysis results"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_results (dataset_id, analysis_type, result)
                VALUES (?, ?, ?)
            ''', (dataset_id, analysis_type, json.dumps(result)))
            
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error storing analysis: {str(e)}")
            raise

    def store_visualization(self, dataset_id: int, viz_type: str, config: Dict[str, Any]) -> int:
        """Store visualization configuration"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO visualizations (dataset_id, viz_type, config)
                VALUES (?, ?, ?)
            ''', (dataset_id, viz_type, json.dumps(config)))
            
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error storing visualization: {str(e)}")
            raise

    def get_dataset_info(self, dataset_id: int) -> Dict[str, Any]:
        """Get dataset information including metadata"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM datasets WHERE id = ?', (dataset_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                    'metadata': json.loads(row['metadata'])
                }
            return None
        except Exception as e:
            print(f"Error getting dataset info: {str(e)}")
            raise

    def get_analysis_results(self, dataset_id: int) -> List[Dict[str, Any]]:
        """Get all analysis results for a dataset"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM analysis_results 
                WHERE dataset_id = ? 
                ORDER BY created_at DESC
            ''', (dataset_id,))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'analysis_type': row['analysis_type'],
                    'result': json.loads(row['result']),
                    'created_at': row['created_at']
                })
            return results
        except Exception as e:
            print(f"Error getting analysis results: {str(e)}")
            raise

    def get_visualizations(self, dataset_id: int) -> List[Dict[str, Any]]:
        """Get all visualizations for a dataset"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM visualizations 
                WHERE dataset_id = ? 
                ORDER BY created_at DESC
            ''', (dataset_id,))
            
            visualizations = []
            for row in cursor.fetchall():
                visualizations.append({
                    'id': row['id'],
                    'viz_type': row['viz_type'],
                    'config': json.loads(row['config']),
                    'created_at': row['created_at']
                })
            return visualizations
        except Exception as e:
            print(f"Error getting visualizations: {str(e)}")
            raise

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
