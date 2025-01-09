import pandas as pd
import numpy as np
from agents.agent_coordinator import AgentCoordinator
from config import GEMINI_API_KEY
import os

def create_sample_dataset():
    """Create a sample sales dataset"""
    np.random.seed(42)
    
    # Generate dates for 3 months instead of a year
    dates = pd.date_range(start='2024-01-01', end='2024-03-31', freq='D')
    
    # Generate sales data
    base_sales = 1000
    trend = np.linspace(0, 200, len(dates))  # Upward trend
    seasonality = 200 * np.sin(2 * np.pi * np.arange(len(dates)) / 90)  # Quarterly seasonality
    noise = np.random.normal(0, 50, len(dates))
    
    sales = base_sales + trend + seasonality + noise
    
    # Generate product categories and regions
    categories = ['Electronics', 'Clothing', 'Food']
    regions = ['North', 'South', 'East']
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'category': np.random.choice(categories, len(dates)),
        'region': np.random.choice(regions, len(dates)),
        'units_sold': np.random.randint(50, 200, len(dates))
    })
    
    # Save to CSV
    csv_path = 'sample_sales_data.csv'
    df.to_csv(csv_path, index=False)
    return csv_path

def main():
    try:
        # Create sample dataset
        print("Creating sample dataset...")
        dataset_path = create_sample_dataset()
        
        # Initialize coordinator
        print("Initializing agent coordinator...")
        coordinator = AgentCoordinator(GEMINI_API_KEY)
        
        # Process dataset and generate report
        print("Processing dataset and generating report...")
        result = coordinator.process_dataset(dataset_path)
        
        if result['status'] == 'success':
            print("\nAnalysis completed successfully!")
            print("\nDataset ID:", result['dataset_id'])
            
            print("\nBasic Statistics:")
            for key, value in result['statistics'].items():
                print(f"{key}: {value}")
            
            print("\nReport Sections:")
            if 'report' in result:
                report = result['report']
                print("\n1. Report Text:")
                print(report['text'][:500] + "..." if len(report['text']) > 500 else report['text'])
                
                print("\n2. Flowchart:")
                print("Mermaid flowchart generated with", len(report['flowchart'].split('\n')), "nodes")
                
                print("\n3. Visualizations:")
                print(f"Generated {len(report['visualizations'])} visualizations")
            
            if 'insights' in result:
                print("\n4. Key Insights:")
                insights = result['insights'].get('insights', '')
                print(insights[:500] + "..." if len(insights) > 500 else insights)
        else:
            print(f"Error: {result.get('message', 'Unknown error')}")
        
        # Clean up
        coordinator.close()
        os.remove(dataset_path)
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error running test: {str(e)}")

if __name__ == "__main__":
    main()
