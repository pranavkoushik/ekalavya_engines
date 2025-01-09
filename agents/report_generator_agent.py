import google.generativeai as genai
from typing import Dict, List, Any
import json
import pandas as pd
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class ReportGeneratorAgent:
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')

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

    def generate_flowchart(self, data: Dict[str, Any], analysis_text: str) -> Dict[str, Any]:
        """Generate a mermaid flowchart based on data analysis"""
        try:
            # Create context for flowchart generation
            context = f"""
            Based on the following data analysis, create a simple mermaid flowchart that visualizes the data processing and analysis workflow.
            Use proper mermaid flowchart syntax with clear node connections and descriptive labels.
            Keep the flowchart concise with no more than 10 nodes.

            Data Analysis:
            {analysis_text[:500]}  # Limit analysis text

            Key Statistics:
            {json.dumps(data, indent=2)[:500]}  # Limit data

            Generate a mermaid flowchart that shows:
            1. Data input and preprocessing steps
            2. Analysis workflow
            3. Key insights generation
            4. Visualization and reporting steps

            Format the flowchart with proper mermaid syntax, for example:
            ```mermaid
            graph TD
                A[Start] --> B[Process]
                B --> C[End]
            ```
            """

            # Get Gemini's response with retry logic
            response_text = self._generate_content(context)
            
            # Extract mermaid flowchart from response
            flowchart = ""
            lines = response_text.split('\n')
            in_mermaid_block = False
            
            for line in lines:
                if '```mermaid' in line:
                    in_mermaid_block = True
                    continue
                elif '```' in line and in_mermaid_block:
                    in_mermaid_block = False
                    continue
                if in_mermaid_block:
                    flowchart += line + '\n'

            return {
                'status': 'success',
                'flowchart': flowchart.strip()
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def generate_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate key insights from the data"""
        try:
            # Convert data to more readable format
            context = f"""
            Based on the following dataset sample, provide key insights and patterns.
            Keep the response concise and focused on the most important findings.

            Data Overview:
            {json.dumps(data, indent=2)[:1000]}  # Limit data size

            Please provide:
            1. Key trends and patterns (max 3)
            2. Notable anomalies or outliers (max 2)
            3. Potential correlations (max 2)
            4. Business recommendations (max 3)
            """

            response_text = self._generate_content(context)
            
            return {
                'status': 'success',
                'insights': response_text
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def generate_report(self, data: Dict[str, Any], analysis: str, visualizations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a comprehensive report including flowchart"""
        try:
            # First, generate flowchart
            flowchart_result = self.generate_flowchart(data, analysis)
            if flowchart_result['status'] != 'success':
                return flowchart_result

            # Create context for report generation
            context = f"""
            Create a concise report based on the following information.
            Focus on the most important findings and keep sections brief.

            Analysis Results:
            {analysis[:1000]}  # Limit analysis text

            Please structure the report with:
            1. Executive Summary (2-3 sentences)
            2. Key Findings (3-4 bullet points)
            3. Recommendations (2-3 points)
            4. Next Steps (2-3 points)
            """

            response_text = self._generate_content(context)
            
            # Combine report with flowchart
            report = {
                'text': response_text,
                'flowchart': flowchart_result['flowchart'],
                'visualizations': visualizations[:5]  # Limit number of visualizations
            }

            return {
                'status': 'success',
                'report': report
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def generate_executive_summary(self, data: Dict[str, Any], insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an executive summary of the analysis"""
        try:
            context = f"""
            Create a very concise executive summary based on:

            Insights:
            {insights['insights'][:500]}  # Limit insights text

            Data Overview:
            {json.dumps(data, indent=2)[:500]}  # Limit data

            The summary should be:
            1. No more than 3-4 sentences
            2. Focus on top 2-3 findings
            3. Include 1-2 key recommendations
            4. Written for executive stakeholders
            """

            response_text = self._generate_content(context)
            
            return {
                'status': 'success',
                'summary': response_text
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
