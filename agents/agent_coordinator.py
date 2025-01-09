from typing import Dict, Any
from .data_processor_agent import DataProcessorAgent
from .visualization_agent import VisualizationAgent
from .report_generator_agent import ReportGeneratorAgent
import os

class AgentCoordinator:
    def __init__(self, gemini_api_key: str):
        self.data_processor = DataProcessorAgent(gemini_api_key)
        self.visualizer = VisualizationAgent()
        self.report_generator = ReportGeneratorAgent(gemini_api_key)
        
    def process_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Coordinate the full dataset processing pipeline"""
        try:
            # Step 1: Process and store data
            process_result = self.data_processor.process_dataset(dataset_path)
            if process_result['status'] != 'success':
                return process_result

            # Step 2: Analyze with Gemini
            analysis = self.data_processor.analyze_with_gemini(
                "Provide a comprehensive analysis of this dataset",
                process_result['dataset_id']
            )
            if analysis['status'] != 'success':
                return analysis

            # Step 3: Create visualizations
            dashboard = self.visualizer.create_dashboard(analysis['data'])
            if dashboard['status'] != 'success':
                return dashboard

            # Step 4: Generate insights
            insights = self.report_generator.generate_insights(analysis['data'])
            if insights['status'] != 'success':
                return insights

            # Step 5: Generate final report
            report = self.report_generator.generate_report(
                analysis['data'],
                analysis['analysis'],
                dashboard['visualizations']
            )
            if report['status'] != 'success':
                return report

            # Step 6: Generate executive summary
            summary = self.report_generator.generate_executive_summary(
                analysis['data'],
                insights
            )
            if summary['status'] != 'success':
                return summary

            return {
                'status': 'success',
                'dataset_id': process_result['dataset_id'],
                'statistics': process_result['statistics'],
                'analysis': analysis['analysis'],
                'visualizations': dashboard['visualizations'],
                'insights': insights['insights'],
                'report': report['report'],
                'summary': summary['summary']
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def analyze_query(self, query: str, dataset_id: int) -> Dict[str, Any]:
        """Handle specific user queries about the data"""
        try:
            # Step 1: Get analysis from Gemini
            analysis = self.data_processor.analyze_with_gemini(query, dataset_id)
            if analysis['status'] != 'success':
                return analysis

            # Step 2: Create relevant visualizations
            viz_suggestions = self.visualizer.suggest_visualizations(analysis['data'])
            if viz_suggestions['status'] != 'success':
                return viz_suggestions

            visualizations = []
            for suggestion in viz_suggestions['suggestions']:
                viz = self.visualizer.create_visualization(
                    analysis['data'],
                    suggestion['type'],
                    x_column=suggestion['columns']['x'][0] if isinstance(suggestion['columns']['x'], list) else suggestion['columns']['x'],
                    y_column=suggestion['columns']['y'][0] if isinstance(suggestion['columns']['y'], list) else suggestion['columns']['y'],
                    title=f"{suggestion['description']}"
                )
                if viz['status'] == 'success':
                    visualizations.append(viz['visualization'])

            return {
                'status': 'success',
                'analysis': analysis['analysis'],
                'visualizations': visualizations
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    def get_analysis_history(self, dataset_id: int) -> Dict[str, Any]:
        """Get analysis history for a dataset"""
        return self.data_processor.get_dataset_analysis_history(dataset_id)

    def close(self):
        """Clean up resources"""
        self.data_processor.close()
