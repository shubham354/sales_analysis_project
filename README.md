# Sales Data Analysis Project

A comprehensive Python-based sales data analysis tool that processes, analyzes, and visualizes sales data to generate actionable business insights.

## Features

- **Data Loading & Cleaning**
  - Handles multiple file encodings
  - Standardizes data formats
  - Removes duplicates
  - Handles missing values
  - Creates derived metrics

- **Analysis Capabilities**
  - Sales trends and patterns
  - Customer behavior analysis
  - Geographic distribution
  - Product performance metrics
  - Temporal analysis (daily, monthly, quarterly)
  - Profit margin calculations
  - Deal size analysis

- **Visualization Outputs**
  - Sales trend charts with moving averages
  - Product performance comparisons
  - Geographic distribution maps
  - Customer segmentation visualizations
  - Temporal heatmaps
  - Correlation matrices

## Generated Files

The script generates several output files:
- `sales_analysis_overview.png`: Overall sales metrics and trends
- `customer_geographic_analysis.png`: Customer and geographic insights
- `temporal_patterns.png`: Time-based analysis visualizations
- `product_analysis.png`: Product performance and correlations
- `sales_analysis_report.txt`: Detailed written analysis
- `detailed_statistics.txt`: Comprehensive statistical metrics

## Requirements
python
pandas
matplotlib
seaborn

## Usage

1. Ensure your sales data is in CSV format with the following required columns:
   - ORDERDATE
   - QUANTITYORDERED
   - PRICEEACH
   - SALES
   - PRODUCTLINE
   - CUSTOMERNAME
   - COUNTRY
   - DEALSIZE
   - PRODUCTCODE
   - STATUS

2. Place your CSV file named `sales_data_sample.csv` in the same directory as the script

3. Run the script:

```bash
python project.py
```

## Data Processing Steps

1. **Data Loading**: Attempts multiple encodings to properly read the CSV file
2. **Date Processing**: Converts dates and creates temporal features
3. **Data Cleaning**: Handles missing values and standardizes formats
4. **Feature Engineering**: Creates derived columns like profit margins
5. **Analysis**: Generates comprehensive statistical analysis
6. **Visualization**: Creates multiple visual representations of the data
7. **Reporting**: Generates detailed reports with insights

## Output Examples

The analysis provides insights such as:
- Top performing products
- Best/worst selling periods
- Customer purchase patterns
- Geographic sales distribution
- Profit margin analysis
- Sales trends and seasonality

## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License
This project can be used for educational purposes.
