import pandas as pd
import google.generativeai as genai
from typing import Dict, List, Any
import json
import os
from .database_manager import DatabaseManager
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class DataProcessorAgent:
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.db = DatabaseManager()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _generate_content(self, prompt: str) -> str:
        """Generate content with retry logic"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e):  # Rate limit error
                print(f"Rate limit hit, retrying in a few seconds...")
                time.sleep(5)  # Add a delay before retry
            raise

    def process_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Process the uploaded dataset and store in database"""
        try:
            # Read dataset
            df = pd.read_csv(dataset_path)
            
            # Get basic statistics
            stats = {
                'row_count': len(df),
                'columns': list(df.columns),
                'numeric_columns': list(df.select_dtypes(include=['int64', 'float64']).columns),
                'categorical_columns': list(df.select_dtypes(include=['object']).columns)
            }
            
            # Store in database
            dataset_name = os.path.basename(dataset_path).split('.')[0]
            dataset_id = self.db.store_dataset(dataset_name, df, "Uploaded dataset")
            
            # Store initial analysis
            self.db.store_analysis(dataset_id, 'basic_stats', stats)
            
            return {
                'status': 'success',
                'statistics': stats,
                'dataset_id': dataset_id
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def analyze_with_gemini(self, query: str, dataset_id: int) -> Dict[str, Any]:
        """Use Gemini to analyze data based on user query"""
        try:
            # Get data from database
            df = self.db.get_dataset(dataset_id)
            dataset_info = self.db.get_dataset_info(dataset_id)
            
            # Create context for Gemini
            context = f"""
            Analyze this dataset with the following columns: {dataset_info['metadata']['columns']}
            Number of rows: {dataset_info['metadata']['rows']}
            Basic statistics:
            {df.describe().to_string()}
            
            User query: {query}
            
            Provide a detailed analysis with insights and recommendations.
            Keep the response concise and focused on the most important findings.
            """

            # Get Gemini's response with retry logic
            response_text = self._generate_content(context)
            
            # Store analysis result
            analysis_result = {
                'query': query,
                'response': response_text,
                'data': df.head(100).to_dict()  # Only store first 100 rows to reduce size
            }
            
            self.db.store_analysis(dataset_id, 'gemini_analysis', analysis_result)
            
            return {
                'status': 'success',
                'analysis': response_text,
                'data': analysis_result['data']
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_dataset_analysis_history(self, dataset_id: int) -> Dict[str, Any]:
        """Get all analysis results for a dataset"""
        try:
            dataset_info = self.db.get_dataset_info(dataset_id)
            analysis_results = self.db.get_analysis_results(dataset_id)
            visualizations = self.db.get_visualizations(dataset_id)
            
            return {
                'status': 'success',
                'dataset_info': dataset_info,
                'analysis_results': analysis_results,
                'visualizations': visualizations
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def close(self):
        """Clean up resources"""
        self.db.close()
