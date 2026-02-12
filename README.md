# Stock Price vs Fundamental Variables Analysis

## Project Overview
This project analyzes the relationship between stock prices and fundamental financial variables for 5 major Indian IT companies: Tata Consultancy Services (TCS), Infosys (INFY), HCL Technologies (HCLTECH), Wipro (WIPRO), and Tech Mahindra (TECHM).

Due to data availability, complete analysis was successfully performed for **TCS** and **Infosys**.

## 📊 Key Findings

### Top 3 Most Significant Variables
| Rank | Company | Variable | Coefficient | P-Value | Significance |
|------|---------|---------|------------|---------|--------------|
| 1 | INFY | PAT Growth | -749.6342 | 0.0021 | Highly Significant |
| 2 | TCS | Sales Growth | -1825.5290 | 0.0191 | Significant |
| 3 | TCS | PAT Growth | 457.1751 | 0.0524 | Weakly Significant |

### Model Performance
| Company | R-squared | Adj R-squared | Observations |
|---------|----------|---------------|--------------|
| TCS | 0.4184 | 0.1947 | 19 years |
| INFY | 0.4823 | 0.2831 | 19 years |

### Key Correlations
- **INFY**: PAT Growth vs Stock Price = -0.661 (Strong negative correlation)
- **TCS**: Sales Growth vs Stock Price = -0.532 (Strong negative correlation)
- **Overall**: PAT Growth shows strongest correlation with stock prices (-0.516)

## 📁 Data Sources

### Sheet1 - Stock Prices
- **Format**: Daily closing prices (2005-2025)
- **Companies**: TCS, Infosys, HCL Tech, Wipro, Tech Mahindra
- **Processing**: Converted daily prices to yearly averages
- **Date Range**: 2006-2024 (20 years of yearly averages)

### Sheet2 - Fundamentals
- **Format**: Annual financial data (1996-2024)
- **Metrics**: Sales, EBITDA, PAT for each company
- **Processing**: Calculated growth rates and margin changes

## 🎯 Variables Analyzed

### Dependent Variable
- `Avg_Stock_Price`: Average annual stock price

### Independent Variables
1. `Sales_Growth`: Year-over-year percentage change in Sales
2. `EBITDA_Growth`: Year-over-year percentage change in EBITDA
3. `PAT_Growth`: Year-over-year percentage change in PAT
4. `EBITDA_Margin_Change`: Change in EBITDA margin (percentage points)
5. `PAT_Margin_Change`: Change in PAT margin (percentage points)

## 🔬 Methodology

### Data Preprocessing
1. Converted daily stock prices to yearly averages using pandas groupby
2. Calculated year-over-year growth rates for all fundamental metrics
3. Computed EBITDA and PAT margins and their year-over-year changes
4. Merged stock price and fundamental data on common years
5. Removed missing values and outliers

### Statistical Analysis

#### 1. Correlation Analysis
- **Method**: Pearson correlation coefficient
- **Range**: -1 to +1
- **Interpretation**: 
  - +1: Perfect positive correlation
  - -1: Perfect negative correlation
  - 0: No correlation
- **Tool**: pandas .corr() function

#### 2. Regression Analysis
- **Algorithm**: Linear Regression
- **Implementation**: scikit-learn LinearRegression
- **Feature Scaling**: StandardScaler (z-score normalization)
- **Significance Testing**: F-regression for p-values
- **Model Evaluation**: R-squared and Adjusted R-squared

### Software & Libraries

Python 3.9+
├── pandas - Data manipulation and analysis


├── numpy - Numerical computations


├── scikit-learn - Linear regression, standardization


├── matplotlib - Static visualizations


├── seaborn - Statistical visualizations


├── openpyxl - Excel file handling


└── fpdf - PDF report generation
text


## 📂 Project Structure

stock-analysis-assignment/
│
├── 📄 Intern test 2 - correlation regression - Copy.xls # Original data
├── 📄 stock_analysis.py # Main analysis script
├── 📄 create_pdf_report_final.py # PDF report generator
├── 📄 README.md # This file
│
├── 📁 output/ # Generated outputs
│ ├── 📊 correlation_heatmap.png # Correlation matrix
│ ├── 📊 company_correlations.png # Company-wise correlations
│ ├── 📊 regression_coefficients.png # Regression coefficients
│ ├── 📊 r_squared_comparison.png # Model fit comparison
│ ├── 📊 pvalue_heatmap.png # Statistical significance
│ ├── 📄 overall_correlation_matrix.csv # CSV: correlation matrix
│ ├── 📄 company_correlations.csv # CSV: company correlations
│ ├── 📄 regression_summary.csv # CSV: regression results
│ ├── 📄 coefficients.csv # CSV: coefficients
│ ├── 📄 pvalues.csv # CSV: p-values
│ └── 📄 top_3_significant.csv # CSV: top 3 variables
│
└── 📁 reports/ # Reports
├── 📄 analysis_summary.txt # Text summary
└── 📄 Stock_Price_Analysis_Final.pdf # Complete PDF report
text


## 🚀 How to Run the Analysis

### Prerequisites
```bash
Python 3.7+ installed

Step 1: Clone/Setup Project
bash

# Create project folder
mkdir stock-analysis-assignment
cd stock-analysis-assignment

# Copy the Excel file to this folder
# Save the Python scripts in this folder

Step 2: Create Virtual Environment (Recommended)
bash

# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

Step 3: Install Requirements
bash

pip install pandas numpy matplotlib seaborn scikit-learn openpyxl fpdf

Step 4: Run Analysis
bash

# Run main analysis (generates CSVs and PNGs)
python stock_analysis.py

# Generate PDF report
python create_pdf_report_final.py

Step 5: View Results
bash

# Windows
start output/
start reports/

# Mac/Linux
open output/

open reports/
