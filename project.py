import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def load_and_clean_data():
    try:
        # Tried different encodings
        df = pd.read_csv('sales_data_sample.csv', encoding='latin1')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv('sales_data_sample.csv', encoding='cp1252')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv('sales_data_sample.csv', encoding='iso-8859-1')
            except UnicodeDecodeError:
                print("Error: Unable to read the CSV file. Please check the file encoding.")
                return None
    
    # Printed initial data info
    print("\nInitial Data Info:")
    print("-----------------")
    print(f"Number of rows: {len(df)}")
    print(f"Number of columns: {len(df.columns)}")
    
    # Converted ORDERDATE to datetime
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'])
    
    # Created additional date-related columns
    df['Year'] = df['ORDERDATE'].dt.year
    df['Month'] = df['ORDERDATE'].dt.month
    df['Quarter'] = df['ORDERDATE'].dt.quarter
    df['DayOfWeek'] = df['ORDERDATE'].dt.day_name()
    
    # Handling missing values 
    df = df.fillna({
        'POSTALCODE': 'UNKNOWN',
        'STATE': 'UNKNOWN',
        'ADDRESSLINE2': '',
        'PHONE': 'NO PHONE',
        'CITY': 'UNKNOWN',
        'TERRITORY': 'UNKNOWN'
    })
    
    # Clean and standardize text columns
    text_columns = ['COUNTRY', 'STATE', 'CITY', 'PRODUCTLINE', 'STATUS']
    for col in text_columns:
        df[col] = df[col].str.strip().str.upper()
    
    
    df = df.drop_duplicates(subset=['ORDERNUMBER', 'PRODUCTCODE'])
    
    
    df['PRICEEACH'] = pd.to_numeric(df['PRICEEACH'], errors='coerce')
    df['SALES'] = pd.to_numeric(df['SALES'], errors='coerce')
    
    
    df = df[df['QUANTITYORDERED'] > 0]  
    df = df[df['PRICEEACH'] > 0]       
    
    # Add derived columns
    df['PROFIT_MARGIN'] = ((df['SALES'] - (df['QUANTITYORDERED'] * df['PRICEEACH'])) / df['SALES']) * 100
    df['DAYS_TO_SHIP'] = (df['ORDERDATE'] - df['ORDERDATE'].min()).dt.days
    
    # Standardize DEALSIZE categories
    df['DEALSIZE'] = df['DEALSIZE'].str.capitalize()
    
    # Log basic data quality metrics
    print(f"Total records: {len(df)}")
    print(f"Date range: {df['ORDERDATE'].min()} to {df['ORDERDATE'].max()}")
    print(f"Number of unique customers: {df['CUSTOMERNAME'].nunique()}")
    print(f"Number of unique products: {df['PRODUCTCODE'].nunique()}")
    print("\nMissing values summary:")
    print(df.isnull().sum()[df.isnull().sum() > 0])
    
    return df

# Perform Summary Statistics
def generate_summary_statistics(df):
    analysis_results = {}
    
    # 1. Basic statistics for numerical columns
    numeric_columns = ['QUANTITYORDERED', 'PRICEEACH', 'SALES', 'PROFIT_MARGIN', 'DAYS_TO_SHIP']
    analysis_results['numeric_stats'] = df[numeric_columns].agg([
        'count', 'mean', 'median', 'std', 'min', 'max',
        lambda x: x.quantile(0.25),
        lambda x: x.quantile(0.75)
    ]).round(2)
    analysis_results['numeric_stats'].rename(index={
        '<lambda_0>': 'q25',
        '<lambda_1>': 'q75'
    }, inplace=True)
    
    # 2. Categorical column analysis
    categorical_columns = ['PRODUCTLINE', 'STATUS', 'COUNTRY', 'DEALSIZE', 'Year', 'Quarter']
    analysis_results['categorical_stats'] = {
        col: {
            'value_counts': df[col].value_counts(),
            'mode': df[col].mode()[0],
            'unique_count': df[col].nunique()
        } for col in categorical_columns
    }
    
    # 3. Time-based analysis
    analysis_results['temporal_stats'] = {
        'monthly_sales': df.groupby(['Year', 'Month'])['SALES'].agg([
            'count', 'sum', 'mean', 'median'
        ]).round(2),
        'quarterly_sales': df.groupby(['Year', 'Quarter'])['SALES'].agg([
            'count', 'sum', 'mean', 'median'
        ]).round(2),
        'day_of_week_stats': df.groupby('DayOfWeek')['SALES'].agg([
            'count', 'sum', 'mean', 'median'
        ]).round(2)
    }
    
    # 4. Product performance metrics
    analysis_results['product_stats'] = {
        'product_line_performance': df.groupby('PRODUCTLINE').agg({
            'SALES': ['count', 'sum', 'mean', 'median'],
            'QUANTITYORDERED': 'sum',
            'PROFIT_MARGIN': 'mean'
        }).round(2),
        'deal_size_performance': df.groupby('DEALSIZE').agg({
            'SALES': ['count', 'sum', 'mean'],
            'QUANTITYORDERED': 'sum'
        }).round(2)
    }
    
    # 5. Customer analysis
    analysis_results['customer_stats'] = {
        'top_customers': df.groupby('CUSTOMERNAME').agg({
            'SALES': 'sum',
            'ORDERNUMBER': 'count'
        }).sort_values('SALES', ascending=False).head(10).round(2),
        'country_performance': df.groupby('COUNTRY').agg({
            'SALES': ['sum', 'mean', 'count'],
            'CUSTOMERNAME': 'nunique'
        }).round(2)
    }
    
    # 6. Correlation analysis
    numeric_cols_for_corr = ['QUANTITYORDERED', 'PRICEEACH', 'SALES', 'PROFIT_MARGIN']
    analysis_results['correlations'] = df[numeric_cols_for_corr].corr().round(3)
    
    # Print key insights
    print("\nKey Statistical Insights:")
    print("-----------------------")
    print(f"Average order value: ${df['SALES'].mean():.2f}")
    print(f"Median order value: ${df['SALES'].median():.2f}")
    print(f"Standard deviation of order value: ${df['SALES'].std():.2f}")
    print(f"Most common product line: {df['PRODUCTLINE'].mode()[0]}")
    print(f"Average profit margin: {df['PROFIT_MARGIN'].mean():.2f}%")
    print(f"Most active customer: {df.groupby('CUSTOMERNAME')['SALES'].count().idxmax()}")
    
    return analysis_results

# Key Metrics
def create_visualizations(df):
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    
    # 1. Sales Trends and Patterns
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # Monthly Sales Trend with Moving Average
    monthly_sales = df.groupby(df['ORDERDATE'].dt.to_period('M'))['SALES'].sum()
    moving_avg = monthly_sales.rolling(window=3).mean()
    ax1.plot(range(len(monthly_sales)), monthly_sales, label='Monthly Sales', marker='o')
    ax1.plot(range(len(moving_avg)), moving_avg, label='3-Month Moving Average', linestyle='--')
    ax1.set_title('Monthly Sales Trend with Moving Average')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Total Sales ($)')
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    
    # Sales by Quarter and Year
    quarterly_sales = df.groupby(['Year', 'Quarter'])['SALES'].sum().unstack()
    quarterly_sales.plot(kind='bar', ax=ax2)
    ax2.set_title('Quarterly Sales by Year')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Sales ($)')
    ax2.legend(title='Quarter')
    
    # Product Performance Analysis
    product_sales = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=True)
    product_sales.plot(kind='barh', ax=ax3)
    ax3.set_title('Sales by Product Line')
    ax3.set_xlabel('Total Sales ($)')
    
    # Deal Size Distribution with Average Sales
    deal_size_stats = df.groupby('DEALSIZE').agg({
        'SALES': ['count', 'mean']
    }).round(2)
    
    ax4.bar(deal_size_stats.index, deal_size_stats[('SALES', 'count')], alpha=0.6, label='Count')
    ax4_twin = ax4.twinx()
    ax4_twin.plot(deal_size_stats.index, deal_size_stats[('SALES', 'mean')], 
                 color='red', marker='o', label='Average Sales')
    ax4.set_title('Deal Size Distribution and Average Sales')
    ax4.set_xlabel('Deal Size')
    ax4.set_ylabel('Count')
    ax4_twin.set_ylabel('Average Sales ($)')
    lines1, labels1 = ax4.get_legend_handles_labels()
    lines2, labels2 = ax4_twin.get_legend_handles_labels()
    ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.tight_layout()
    plt.savefig('sales_analysis_overview.png')
    plt.close()
    
    # 2. Customer and Geographic Analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Top 10 Customers
    top_customers = df.groupby('CUSTOMERNAME')['SALES'].sum().sort_values(ascending=True).tail(10)
    top_customers.plot(kind='barh', ax=ax1)
    ax1.set_title('Top 10 Customers by Sales')
    ax1.set_xlabel('Total Sales ($)')
    
    # Sales by Country
    country_sales = df.groupby('COUNTRY')['SALES'].sum().sort_values(ascending=True)
    country_sales.plot(kind='barh', ax=ax2)
    ax2.set_title('Sales by Country')
    ax2.set_xlabel('Total Sales ($)')
    
    plt.tight_layout()
    plt.savefig('customer_geographic_analysis.png')
    plt.close()
    
    # 3. Temporal Patterns
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Sales by Day of Week
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_sales = df.groupby('DayOfWeek')['SALES'].mean()
    daily_sales = daily_sales.reindex(day_order)
    daily_sales.plot(kind='bar', ax=ax1)
    ax1.set_title('Average Sales by Day of Week')
    ax1.set_xlabel('Day of Week')
    ax1.set_ylabel('Average Sales ($)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Monthly Sales Heatmap
    monthly_sales = df.pivot_table(
        values='SALES',
        index=df['ORDERDATE'].dt.month,
        columns=df['ORDERDATE'].dt.year,
        aggfunc='sum'
    )
    sns.heatmap(monthly_sales, cmap='YlOrRd', ax=ax2, annot=True, fmt='.0f')
    ax2.set_title('Monthly Sales Heatmap by Year')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Month')
    
    plt.tight_layout()
    plt.savefig('temporal_patterns.png')
    plt.close()
    
    # 4. Product Analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    
    # Product Line Performance
    product_performance = df.groupby('PRODUCTLINE').agg({
        'SALES': 'sum',
        'PROFIT_MARGIN': 'mean'
    })
    
    ax1.bar(product_performance.index, product_performance['SALES'])
    ax1_twin = ax1.twinx()
    ax1_twin.plot(product_performance.index, product_performance['PROFIT_MARGIN'], 
                 color='red', marker='o')
    ax1.set_title('Product Line Performance')
    ax1.set_xlabel('Product Line')
    ax1.set_ylabel('Total Sales ($)')
    ax1_twin.set_ylabel('Average Profit Margin (%)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Correlation Heatmap
    numeric_cols = ['QUANTITYORDERED', 'PRICEEACH', 'SALES', 'PROFIT_MARGIN']
    correlation_matrix = df[numeric_cols].corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', ax=ax2)
    ax2.set_title('Correlation Matrix of Key Metrics')
    
    plt.tight_layout()
    plt.savefig('product_analysis.png')
    plt.close()

# Insights Report
def generate_report(df, analysis_results):
    with open('sales_analysis_report.txt', 'w') as f:
        f.write("Sales Data Analysis Report\n")
        f.write("=========================\n\n")
        
        # Overall Statistics
        f.write("1. Overall Statistics\n")
        f.write("-----------------\n")
        f.write(f"Total Orders: {len(df)}\n")
        f.write(f"Total Sales: ${df['SALES'].sum():,.2f}\n")
        f.write(f"Average Order Value: ${df['SALES'].mean():,.2f}\n\n")
        
        # Product Performance
        f.write("2. Product Performance\n")
        f.write("--------------------\n")
        top_products = df.groupby('PRODUCTLINE')['SALES'].sum().sort_values(ascending=False)
        f.write("Top Performing Product Lines:\n")
        for product, sales in top_products.items():
            f.write(f"{product}: ${sales:,.2f}\n")
        f.write("\n")
        
        # Seasonal Patterns
        f.write("3. Seasonal Patterns\n")
        f.write("------------------\n")
        monthly_sales = df.groupby(df['ORDERDATE'].dt.month)['SALES'].mean()
        best_month = monthly_sales.idxmax()
        worst_month = monthly_sales.idxmin()
        f.write(f"Best performing month: {best_month}\n")
        f.write(f"Worst performing month: {worst_month}\n")

def main():
    df = load_and_clean_data()
    analysis_results = generate_summary_statistics(df)
    
    with open('detailed_statistics.txt', 'w') as f:
        f.write("Numeric Statistics:\n")
        f.write("------------------\n")
        f.write(analysis_results['numeric_stats'].to_string())
        f.write("\n\n")
        
      
        f.write("Categorical Statistics:\n")
        f.write("----------------------\n")
        for category, stats in analysis_results['categorical_stats'].items():
            f.write(f"\n{category}:\n")
            f.write(f"Mode: {stats['mode']}\n")
            f.write(f"Unique values: {stats['unique_count']}\n")
            f.write("Value counts:\n")
            f.write(stats['value_counts'].to_string())
            f.write("\n")
        
       
        f.write("\nCorrelation Matrix:\n")
        f.write("------------------\n")
        f.write(analysis_results['correlations'].to_string())
    
    create_visualizations(df)
    generate_report(df, analysis_results)
    
    print("\nAnalysis complete! Check the generated files for detailed results.")

if __name__ == "__main__":
    main()
