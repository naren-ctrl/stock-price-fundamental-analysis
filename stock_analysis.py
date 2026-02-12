"""
STOCK PRICE VS FUNDAMENTALS ANALYSIS
Complete solution for internship assignment
RUN THIS EXACT CODE - IT WILL WORK
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import f_regression
from fpdf import FPDF
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
import os

# Create output folders
os.makedirs('output', exist_ok=True)
os.makedirs('reports', exist_ok=True)

print("="*80)
print("STOCK PRICE VS FUNDAMENTALS ANALYSIS")
print("="*80)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)

# ============================================
# STEP 1: LOAD DATA
# ============================================
print("\n📁 STEP 1: Loading data...")

file_path = ("E:\stock-analysis-assignment\Intern test 2 - correlation regression - Copy.xls")

try:
    df_stocks = pd.read_excel(file_path, sheet_name='Sheet1', header=None)
    # Read fundamentals without forcing a header - sheet has a non-standard layout
    df_fund_raw = pd.read_excel(file_path, sheet_name='Sheet2', header=None)
    print(f"   ✓ Stock data loaded: {df_stocks.shape}")
    print(f"   ✓ Fundamentals loaded: {df_fund_raw.shape}")
except Exception as e:
    print(f"   ✗ Error loading file: {e}")
    print("   Please make sure the Excel file is in the same directory")
    exit()

# ============================================
# STEP 2: EXTRACT AND CLEAN STOCK PRICES
# ============================================
print("\n📈 STEP 2: Processing stock prices...")

tickers = ['TCS', 'INFY', 'HCLTECH', 'WIPRO', 'TECHM']
company_names = df_stocks.iloc[1, 1:6].values

# Extract price data
dates = df_stocks.iloc[5:, 0].values
price_data = df_stocks.iloc[5:, 1:6].values

stock_df = pd.DataFrame(price_data, columns=tickers, index=dates)
stock_df = stock_df.apply(pd.to_numeric, errors='coerce')
stock_df.index = pd.to_datetime(stock_df.index, format='%m/%d/%Y', errors='coerce')
stock_df = stock_df.dropna()
stock_df['Year'] = stock_df.index.year
yearly_prices = stock_df.groupby('Year')[tickers].mean()

print(f"   ✓ Date range: {stock_df.index[0].date()} to {stock_df.index[-1].date()}")
print(f"   ✓ Yearly averages calculated: {len(yearly_prices)} years")

# ============================================
# STEP 3: PROCESS FUNDAMENTAL DATA
# ============================================
print("\n📊 STEP 3: Processing fundamentals...")

fundamental_data = {}

# Detect a row that contains year labels (look in the first few rows)
year_row_idx = None
for r in range(min(8, len(df_fund_raw))):
    row = df_fund_raw.iloc[r, 4:]
    ok = 0
    total = 0
    for val in row:
        total += 1
        try:
            iv = int(float(val))
            if 1900 <= iv <= 2100:
                ok += 1
        except Exception:
            pass
    if total and ok >= max(3, int(total * 0.4)):
        year_row_idx = r
        break

if year_row_idx is not None:
    years = df_fund_raw.iloc[year_row_idx, 4:].astype(str).tolist()
else:
    # fallback: use positional year indices
    years = [str(i) for i in range(1, df_fund_raw.shape[1] - 4 + 1)]

# Parse rows: search for any occurrence of 'SALES' across columns and treat each as a block
rows = df_fund_raw
ncols = df_fund_raw.shape[1]
found_blocks = []
for r in range(len(rows)):
    for c in range(ncols):
        try:
            cell = str(rows.iat[r, c]).strip().upper() if pd.notna(rows.iat[r, c]) else ''
        except Exception:
            cell = ''
        if cell == 'SALES':
            # block assumed to start 3 columns to the left of 'SALES'
            block_start = max(0, c - 3)

            # find ticker/company near the left of the block
            ticker_raw = ''
            compname = ''
            for look in range(block_start, min(block_start + 3, ncols)):
                try:
                    v = rows.iat[r, look]
                    if pd.notna(v):
                        s = str(v).strip()
                        if len(s) <= 6 and s.isalpha():
                            ticker_raw = s.upper()
                            break
                        # fallback to company name
                        if len(s) > 0 and len(s) < 80:
                            compname = s.upper()
                except Exception:
                    continue

            matched = None
            for t in tickers:
                if ticker_raw == t:
                    matched = t
                    break
                if ticker_raw and ticker_raw in t:
                    matched = t
                    break
                if compname and t in compname:
                    matched = t
                    break

            # extract numbers starting at column c+1 for this block
            sales = None
            ebitda = None
            pat = None
            try:
                sales = rows.iloc[r, c + 1: ncols].values
            except Exception:
                sales = None
            try:
                ebitda = rows.iloc[r + 1, c + 1: ncols].values
            except Exception:
                ebitda = None
            try:
                pat = rows.iloc[r + 2, c + 1: ncols].values
            except Exception:
                pat = None

            if matched and sales is not None:
                df = pd.DataFrame({
                    'Year': years[:len(sales)],
                    'Sales': sales[:len(years)],
                    'EBITDA': (ebitda[:len(years)] if ebitda is not None else [None] * len(years)),
                    'PAT': (pat[:len(years)] if pat is not None else [None] * len(years))
                })
                for col in ['Sales', 'EBITDA', 'PAT']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

                try:
                    df['Year'] = df['Year'].astype(int)
                except Exception:
                    pass

                df = df.dropna().sort_values('Year') if 'Year' in df.columns else df.dropna()

                if len(df) >= 2:
                    df['Sales_Growth'] = df['Sales'].pct_change() * 100
                    df['EBITDA_Growth'] = df['EBITDA'].pct_change() * 100
                    df['PAT_Growth'] = df['PAT'].pct_change() * 100
                    df['EBITDA_Margin'] = (df['EBITDA'] / df['Sales']) * 100
                    df['PAT_Margin'] = (df['PAT'] / df['Sales']) * 100
                    df['EBITDA_Margin_Change'] = df['EBITDA_Margin'].diff()
                    df['PAT_Margin_Change'] = df['PAT_Margin'].diff()

                    # If multiple blocks map to same company, prefer larger df (more years)
                    prev = fundamental_data.get(matched)
                    if prev is None or len(df) > len(prev):
                        fundamental_data[matched] = df
                        try:
                            yr_min = int(df['Year'].min()) if 'Year' in df.columns else 'N/A'
                            yr_max = int(df['Year'].max()) if 'Year' in df.columns else 'N/A'
                            print(f"   ✓ {matched}: {len(df)} years ({yr_min}-{yr_max})")
                        except Exception:
                            print(f"   ✓ {matched}: {len(df)} rows parsed")
            else:
                if not matched:
                    # log unknown block start for debugging
                    pass
            found_blocks.append((r, c, matched))

# ============================================
# STEP 4: MERGE DATASETS
# ============================================
print("\n🔄 STEP 4: Merging stock prices with fundamentals...")

merged_data = {}
for ticker in tickers:
    if ticker in fundamental_data:
        prices = yearly_prices[ticker].reset_index()
        prices.columns = ['Year', 'Avg_Stock_Price']
        
        fund = fundamental_data[ticker][['Year', 'Sales_Growth', 'EBITDA_Growth', 
                        'PAT_Growth', 'EBITDA_Margin_Change', 
                        'PAT_Margin_Change']].copy()
        # ensure Year is numeric and compatible with yearly_prices Year
        fund['Year'] = pd.to_numeric(fund['Year'], errors='coerce')
        fund = fund.dropna(subset=['Year']).copy()
        fund['Year'] = fund['Year'].astype(int)
        
        merged = pd.merge(prices, fund, on='Year', how='inner')
        merged = merged.dropna()
        
        if len(merged) > 0:
            merged_data[ticker] = merged
            print(f"   ✓ {ticker}: {len(merged)} years ({merged['Year'].min()}-{merged['Year'].max()})")

if len(merged_data) == 0:
    print("   ✗ No merged data available. Exiting.")
    exit()

# ============================================
# STEP 5: CORRELATION ANALYSIS
# ============================================
print("\n🔍 STEP 5: Running correlation analysis...")

vars_to_analyze = ['Avg_Stock_Price', 'Sales_Growth', 'EBITDA_Growth', 
                   'PAT_Growth', 'EBITDA_Margin_Change', 'PAT_Margin_Change']

all_data = []
for ticker, data in merged_data.items():
    d = data[vars_to_analyze].copy()
    all_data.append(d)

combined_df = pd.concat(all_data, ignore_index=True)
overall_corr = combined_df[vars_to_analyze].corr()
corr_with_price = overall_corr['Avg_Stock_Price'].sort_values(ascending=False)

print("\n   📊 Overall Correlation with Stock Price:")
print(corr_with_price.round(3))

company_corr = {}
print("\n   📊 Company-wise Correlations:")
print("-" * 85)
print(f"{'Company':<10} {'Sales_Growth':>12} {'EBITDA_Growth':>12} {'PAT_Growth':>12} "
      f"{'EBITDA_Margin_Ch':>16} {'PAT_Margin_Ch':>14}")
print("-" * 85)

for ticker, data in merged_data.items():
    corr = data[vars_to_analyze].corr()['Avg_Stock_Price'].drop('Avg_Stock_Price')
    company_corr[ticker] = corr
    print(f"{ticker:<10} {corr['Sales_Growth']:>12.3f} {corr['EBITDA_Growth']:>12.3f} "
          f"{corr['PAT_Growth']:>12.3f} {corr['EBITDA_Margin_Change']:>16.3f} "
          f"{corr['PAT_Margin_Change']:>14.3f}")

# ============================================
# STEP 6: REGRESSION ANALYSIS
# ============================================
print("\n📐 STEP 6: Running regression analysis...")

independent_vars = ['Sales_Growth', 'EBITDA_Growth', 'PAT_Growth', 
                    'EBITDA_Margin_Change', 'PAT_Margin_Change']

regression_results = []

print("\n   📊 Regression Results by Company:")
print("=" * 90)

for ticker, data in merged_data.items():
    X = data[independent_vars].copy()
    y = data['Avg_Stock_Price'].copy()
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
    
    model = LinearRegression()
    model.fit(X_scaled, y)
    
    f_stats, p_values = f_regression(X_scaled, y)
    r2 = model.score(X_scaled, y)
    adj_r2 = 1 - (1 - r2) * (len(y) - 1) / (len(y) - X.shape[1] - 1)
    
    result = {
        'Company': ticker,
        'R_Squared': r2,
        'Adj_R_Squared': adj_r2,
        'Observations': len(y)
    }
    
    for i, var in enumerate(independent_vars):
        result[f'coef_{var}'] = model.coef_[i]
        result[f'pval_{var}'] = p_values[i]
    
    regression_results.append(result)
    
    print(f"\n   {ticker}:")
    print(f"   R² = {r2:.4f}, Adj R² = {adj_r2:.4f}, N = {len(y)}")
    print(f"   {'Variable':<25} {'Coefficient':>12} {'P-Value':>12}")
    print(f"   {'-'*51}")
    
    for i, var in enumerate(independent_vars):
        print(f"   {var:<25} {model.coef_[i]:>12.4f} {p_values[i]:>12.4f}")

reg_df = pd.DataFrame(regression_results)
reg_df.set_index('Company', inplace=True)

# ============================================
# STEP 7: FIND TOP 3 SIGNIFICANT VARIABLES
# ============================================
print("\n🏆 STEP 7: Identifying top 3 most significant variables...")

significance_data = []
for ticker in merged_data.keys():
    for var in independent_vars:
        significance_data.append({
            'Company': ticker,
            'Variable': var,
            'Coefficient': reg_df.loc[ticker, f'coef_{var}'],
            'P_Value': reg_df.loc[ticker, f'pval_{var}']
        })

sig_df = pd.DataFrame(significance_data)
sig_df = sig_df.sort_values('P_Value')
top_3 = sig_df.head(3)

print("\n   📊 TOP 3 MOST SIGNIFICANT VARIABLES:")
print("=" * 80)
print(f"{'Company':<12} {'Variable':<25} {'Coefficient':>12} {'P-Value':>12}")
print("-" * 80)
for _, row in top_3.iterrows():
    print(f"{row['Company']:<12} {row['Variable']:<25} {row['Coefficient']:>12.4f} {row['P_Value']:>12.4f}")

# ============================================
# STEP 8: CREATE VISUALIZATIONS
# ============================================
print("\n🎨 STEP 8: Creating visualizations...")

plt.style.use('default')
sns.set_palette("husl")

# 1. Correlation Heatmap
fig1, ax1 = plt.subplots(figsize=(10, 8))
sns.heatmap(overall_corr, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            square=True, linewidths=0.5, ax=ax1)
ax1.set_title('Overall Correlation Matrix', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('output/correlation_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ correlation_heatmap.png")

# 2. Company-wise Correlations
fig2, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
for idx, (ticker, corr_data) in enumerate(company_corr.items()):
    if idx < 5:
        colors = ['green' if x > 0 else 'red' for x in corr_data.values]
        axes[idx].barh(corr_data.index, corr_data.values, color=colors)
        axes[idx].axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        axes[idx].set_title(f'{ticker}', fontsize=12, fontweight='bold')
        axes[idx].set_xlabel('Correlation')
        axes[idx].set_xlim(-1, 1)
fig2.delaxes(axes[5])
plt.suptitle('Correlation with Stock Price by Company', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('output/company_correlations.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ company_correlations.png")

# 3. Regression Coefficients
fig3, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
for idx, ticker in enumerate(merged_data.keys()):
    if idx < 5:
        coefs = [reg_df.loc[ticker, f'coef_{var}'] for var in independent_vars]
        colors = ['green' if c > 0 else 'red' for c in coefs]
        axes[idx].barh(independent_vars, coefs, color=colors)
        axes[idx].axvline(x=0, color='black', linestyle='-', linewidth=1)
        axes[idx].set_title(f'{ticker} (R² = {reg_df.loc[ticker, "R_Squared"]:.3f})', fontsize=12, fontweight='bold')
        axes[idx].set_xlabel('Standardized Coefficient')
fig3.delaxes(axes[5])
plt.suptitle('Regression Coefficients by Company', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('output/regression_coefficients.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ regression_coefficients.png")

# 4. R-squared Comparison
fig4, ax4 = plt.subplots(figsize=(10, 6))
r2_values = reg_df['R_Squared']
bars = ax4.bar(r2_values.index, r2_values.values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
ax4.set_ylabel('R-squared')
ax4.set_title('Model Fit Comparison (R²)', fontsize=14, fontweight='bold')
ax4.set_ylim(0, 1)
for bar, val in zip(bars, r2_values.values):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{val:.3f}', ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('output/r_squared_comparison.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ r_squared_comparison.png")

# 5. P-value Heatmap
fig5, ax5 = plt.subplots(figsize=(12, 5))
pval_matrix = []
for ticker in merged_data.keys():
    pvals = [reg_df.loc[ticker, f'pval_{var}'] for var in independent_vars]
    pval_matrix.append(pvals)
pval_df_plot = pd.DataFrame(pval_matrix, index=merged_data.keys(), columns=independent_vars)
sns.heatmap(pval_df_plot, annot=True, fmt='.3f', cmap='RdYlGn_r', center=0.05,
            linewidths=0.5, ax=ax5, cbar_kws={'label': 'P-Value'})
ax5.set_title('Statistical Significance (P-Values)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('output/pvalue_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✓ pvalue_heatmap.png")

# ============================================
# STEP 9: SAVE RESULTS TO CSV
# ============================================
print("\n💾 STEP 9: Saving results to CSV...")

overall_corr.round(3).to_csv('output/overall_correlation_matrix.csv')
pd.DataFrame(company_corr).T.round(3).to_csv('output/company_correlations.csv')
reg_df.round(4).to_csv('output/regression_summary.csv')

coef_cols = [f'coef_{var}' for var in independent_vars]
coef_table = reg_df[coef_cols].round(4)
coef_table.columns = independent_vars
coef_table.to_csv('output/coefficients.csv')

pval_cols = [f'pval_{var}' for var in independent_vars]
pval_table = reg_df[pval_cols].round(4)
pval_table.columns = [f'{var}_pval' for var in independent_vars]
pval_table.to_csv('output/pvalues.csv')

top_3.to_csv('output/top_3_significant.csv', index=False)

print("   ✓ All CSV files saved successfully")

# ============================================
# STEP 10: CREATE SUMMARY REPORT
# ============================================
print("\n📝 STEP 10: Creating summary report...")

summary_file = open('reports/analysis_summary.txt', 'w', encoding='utf-8')

summary_file.write("="*80 + "\n")
summary_file.write("STOCK PRICE VS FUNDAMENTALS ANALYSIS - SUMMARY REPORT\n")
summary_file.write("="*80 + "\n\n")
summary_file.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
summary_file.write("="*80 + "\n")
summary_file.write("PART 1: CORRELATION ANALYSIS\n")
summary_file.write("="*80 + "\n\n")
summary_file.write("Overall Correlation with Stock Price:\n")
summary_file.write(str(corr_with_price.round(3)) + "\n\n")
summary_file.write("Company-wise Correlations:\n")
summary_file.write(str(pd.DataFrame(company_corr).T.round(3)) + "\n\n")
summary_file.write("="*80 + "\n")
summary_file.write("PART 2: REGRESSION ANALYSIS\n")
summary_file.write("="*80 + "\n\n")
summary_file.write("R-squared Values:\n")
summary_file.write(str(reg_df[['R_Squared', 'Adj_R_Squared']].round(4)) + "\n\n")
summary_file.write("="*80 + "\n")
summary_file.write("PART 3: TOP 3 MOST SIGNIFICANT VARIABLES\n")
summary_file.write("="*80 + "\n\n")
summary_file.write(top_3[['Company', 'Variable', 'Coefficient', 'P_Value']].to_string(index=False) + "\n\n")
summary_file.write("="*80 + "\n")
summary_file.write("ANALYSIS COMPLETED SUCCESSFULLY\n")
summary_file.write("="*80 + "\n")

summary_file.close()
print("   ✓ analysis_summary.txt created")

# # ============================================
# # STEP 11: CREATE README FILE
# # ============================================
# print("\n📖 STEP 11: Creating README file...")

# readme_content = f"""# Stock Price vs Fundamental Variables Analysis

# ## Project Overview
# This project analyzes the relationship between stock prices and fundamental financial variables for 5 major Indian IT companies: TCS, Infosys, HCL Technologies, Wipro, and Tech Mahindra.

# ## Key Findings
# - **Overall Best Predictor**: {top_3.iloc[0]['Variable']} (p={top_3.iloc[0]['P_Value']:.4f})
# - **Best Model Fit**: {reg_df['R_Squared'].idxmax()} (R² = {reg_df['R_Squared'].max():.3f})
# - **Strongest Correlation**: {corr_with_price.index[0]} ({corr_with_price.values[0]:.3f})

# ## Data Sources
# - **Stock Prices**: Daily closing prices (2005-2025) from Sheet1
# - **Fundamentals**: Annual Sales, EBITDA, PAT (1996-2024) from Sheet2

# ## Variables Analyzed
# ### Dependent Variable
# - Average Annual Stock Price

# ### Independent Variables
# 1. Sales Growth (% YoY)
# 2. EBITDA Growth (% YoY)
# 3. PAT Growth (% YoY)
# 4. EBITDA Margin Change (percentage points)
# 5. PAT Margin Change (percentage points)

# ## Methodology
# 1. **Data Processing**: Converted daily prices to yearly averages, calculated growth rates and margin changes
# 2. **Correlation Analysis**: Pearson correlation coefficients
# 3. **Regression Analysis**: Linear regression with standardized coefficients
# 4. **Significance Testing**: F-test for p-values
# 5. **Model Evaluation**: R-squared and Adjusted R-squared

# ## Files Structure
# ├── Intern test 2 - correlation regression - Copy.xls
# ├── stock_analysis.py
# ├── output/
# │ ├── correlation_heatmap.png
# │ ├── company_correlations.png
# │ ├── regression_coefficients.png
# │ ├── r_squared_comparison.png
# │ ├── pvalue_heatmap.png
# │ ├── overall_correlation_matrix.csv
# │ ├── company_correlations.csv
# │ ├── regression_summary.csv
# │ ├── coefficients.csv
# │ ├── pvalues.csv
# │ └── top_3_significant.csv
# └── reports/
# ├── analysis_summary.txt
# └── [PDF Report will be generated separately]
# text


# ## How to Run
# 1. Install requirements:
#    ```bash
#    pip install pandas numpy matplotlib seaborn scikit-learn openpyxl

#     Place the Excel file in the same directory

#     Run the script:
#     bash

#     python stock_analysis.py

# Requirements

#     Python 3.7+

#     pandas

#     numpy

#     matplotlib

#     seaborn

#     scikit-learn

#     openpyxl

# Author

# [Your Name]
# Date: {datetime.now().strftime('%Y-%m-%d')}
# """

# with open('README.md', 'w', encoding='utf-8') as f:
# f.write(readme_content)
# print(" ✓ README.md created")
# ============================================
# COMPLETION
# ============================================

# print("\n" + "="*80)
# print("✅ ANALYSIS COMPLETED SUCCESSFULLY!")
# print("="*80)
# print("\n📁 Output files saved in:")
# print(" 📊 output/ - All CSV files and PNG images")
# print(" 📄 reports/ - Summary report")
# print(" 📝 README.md - Project documentation")
# print("\n📦 Files generated:")
# try:
# output_files = len(os.listdir('output'))
# print(f" • {output_files} files in output folder")
# except:
# print(" • Files in output folder")
# print(" • 1 summary report in reports folder")
# print(" • 1 README.md file")
# print("\n⏱️ Analysis completed at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
# print("="*80)
# Optional: Generate PDF (uncomment if you have fpdf installed)

# """
# from fpdf import FPDF
# pdf = FPDF()
# pdf.add_page()
# pdf.set_font('Arial', 'B', 16)
# pdf.cell(0, 10, 'Stock Price vs Fundamentals Analysis', 0, 1, 'C')
# pdf.output('reports/analysis_report.pdf')
# print(" ✓ PDF report created")
# """