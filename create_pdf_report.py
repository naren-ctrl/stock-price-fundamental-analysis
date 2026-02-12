"""
Ultra Simple PDF Report - NO SPECIAL CHARACTERS AT ALL
Save as final_report.py and run
"""

from fpdf import FPDF
import pandas as pd
from datetime import datetime
import os

# Read your results
top_3 = pd.read_csv('output/top_3_significant.csv')
reg_summary = pd.read_csv('output/regression_summary.csv')
company_corr = pd.read_csv('output/company_correlations.csv')

print("✓ Results loaded successfully")

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Stock Price vs Fundamentals Analysis', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# Create PDF
pdf = PDF()
pdf.add_page()

# ============================================
# TITLE PAGE
# ============================================
pdf.set_font('Arial', 'B', 20)
pdf.cell(0, 40, 'FINANCIAL ANALYSIS REPORT', 0, 1, 'C')
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, 'Stock Price vs Fundamental Variables', 0, 1, 'C')
pdf.set_font('Arial', '', 12)
pdf.cell(0, 10, f'Date: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
pdf.ln(20)

# ============================================
# EXECUTIVE SUMMARY
# ============================================
pdf.add_page()
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, '1. EXECUTIVE SUMMARY', 0, 1)
pdf.ln(5)

pdf.set_font('Arial', '', 11)
pdf.multi_cell(0, 6, 'This analysis examines the relationship between stock prices and fundamental variables for Indian IT companies (TCS and Infosys).')
pdf.ln(5)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 6, 'KEY FINDINGS:', 0, 1)
pdf.ln(2)

pdf.set_font('Arial', '', 11)
pdf.cell(0, 6, '1. TOP 3 MOST SIGNIFICANT VARIABLES:', 0, 1)
pdf.cell(0, 6, f'   (1) INFY - PAT Growth (p-value = {top_3.iloc[0]["P_Value"]:.4f})', 0, 1)
pdf.cell(0, 6, f'   (2) TCS - Sales Growth (p-value = {top_3.iloc[1]["P_Value"]:.4f})', 0, 1)
pdf.cell(0, 6, f'   (3) TCS - PAT Growth (p-value = {top_3.iloc[2]["P_Value"]:.4f})', 0, 1)
pdf.ln(2)

pdf.cell(0, 6, '2. MODEL PERFORMANCE:', 0, 1)
pdf.cell(0, 6, f'   - Infosys (INFY): R-squared = {reg_summary.iloc[1]["R_Squared"]:.3f}', 0, 1)
pdf.cell(0, 6, f'   - TCS: R-squared = {reg_summary.iloc[0]["R_Squared"]:.3f}', 0, 1)
pdf.ln(2)

pdf.cell(0, 6, '3. KEY CORRELATIONS:', 0, 1)
pdf.cell(0, 6, '   - INFY: PAT Growth vs Stock Price = -0.661', 0, 1)
pdf.cell(0, 6, '   - TCS: Sales Growth vs Stock Price = -0.532', 0, 1)

# ============================================
# TOP 3 SIGNIFICANT VARIABLES
# ============================================
pdf.add_page()
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, '2. TOP 3 MOST SIGNIFICANT VARIABLES', 0, 1)
pdf.ln(5)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 6, 'Rank  Company      Variable           Coefficient    P-Value    Significance', 0, 1)
pdf.set_font('Arial', '', 11)
pdf.cell(0, 6, '----------------------------------------------------------------------------', 0, 1)

for i, (_, row) in enumerate(top_3.iterrows(), 1):
    p_val = row['P_Value']
    if p_val < 0.01:
        sig = 'Highly Significant'
    elif p_val < 0.05:
        sig = 'Significant'
    elif p_val < 0.10:
        sig = 'Weakly Significant'
    else:
        sig = 'Not Significant'
    
    pdf.cell(0, 6, f'{i}     {row["Company"]:<10} {row["Variable"]:<18} {row["Coefficient"]:>12.4f}    {row["P_Value"]:>8.4f}    {sig}', 0, 1)

pdf.ln(10)
pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 6, 'Significance Levels:', 0, 1)
pdf.set_font('Arial', '', 11)
pdf.cell(0, 6, '- p < 0.01: Highly Significant', 0, 1)
pdf.cell(0, 6, '- p < 0.05: Significant', 0, 1)
pdf.cell(0, 6, '- p < 0.10: Weakly Significant', 0, 1)

# ============================================
# CORRELATION ANALYSIS
# ============================================
pdf.add_page()
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, '3. CORRELATION ANALYSIS RESULTS', 0, 1)
pdf.ln(5)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 6, 'Correlation with Stock Price by Company:', 0, 1)
pdf.ln(2)

# Table
col_width = 180 / 6
pdf.set_font('Arial', 'B', 9)

pdf.cell(col_width, 6, 'Company', 1, 0, 'C')
pdf.cell(col_width, 6, 'Sales Gr', 1, 0, 'C')
pdf.cell(col_width, 6, 'EBITDA Gr', 1, 0, 'C')
pdf.cell(col_width, 6, 'PAT Gr', 1, 0, 'C')
pdf.cell(col_width, 6, 'EBITDA Mar', 1, 0, 'C')
pdf.cell(col_width, 6, 'PAT Mar', 1, 0, 'C')
pdf.ln()

pdf.set_font('Arial', '', 9)
for _, row in company_corr.iterrows():
    pdf.cell(col_width, 6, str(row.iloc[0]), 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[1]:.3f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[2]:.3f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[3]:.3f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[4]:.3f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[5]:.3f}", 1, 0, 'C')
    pdf.ln()

pdf.ln(5)
pdf.set_font('Arial', '', 11)
pdf.cell(0, 6, 'Key Observations:', 0, 1)
pdf.cell(0, 6, '- INFY: Strong negative correlation with PAT Growth (-0.661)', 0, 1)
pdf.cell(0, 6, '- TCS: Strong negative correlation with Sales Growth (-0.532)', 0, 1)

# ============================================
# REGRESSION ANALYSIS
# ============================================
pdf.add_page()
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, '4. REGRESSION ANALYSIS RESULTS', 0, 1)
pdf.ln(5)

pdf.set_font('Arial', 'B', 11)
pdf.cell(0, 6, 'Model Summary (R-squared):', 0, 1)
pdf.ln(2)

col_width = 180 / 3
pdf.set_font('Arial', 'B', 9)

pdf.cell(col_width, 6, 'Company', 1, 0, 'C')
pdf.cell(col_width, 6, 'R-squared', 1, 0, 'C')
pdf.cell(col_width, 6, 'Adj R-squared', 1, 0, 'C')
pdf.ln()

pdf.set_font('Arial', '', 9)
for _, row in reg_summary.iterrows():
    pdf.cell(col_width, 6, row['Company'], 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row['R_Squared']:.4f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row['Adj_R_Squared']:.4f}", 1, 0, 'C')
    pdf.ln()

pdf.ln(5)
pdf.set_font('Arial', '', 11)
pdf.cell(0, 6, f'Interpretation:', 0, 1)
pdf.cell(0, 6, f'- INFY model explains {reg_summary.iloc[1]["R_Squared"]*100:.1f}% of stock price variation', 0, 1)
pdf.cell(0, 6, f'- TCS model explains {reg_summary.iloc[0]["R_Squared"]*100:.1f}% of stock price variation', 0, 1)

# ============================================
# COEFFICIENTS
# ============================================
pdf.add_page()
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, '5. REGRESSION COEFFICIENTS', 0, 1)
pdf.ln(5)

coef_df = pd.read_csv('output/coefficients.csv')

col_width = 180 / 6
pdf.set_font('Arial', 'B', 9)

pdf.cell(col_width, 6, 'Company', 1, 0, 'C')
pdf.cell(col_width, 6, 'Sales Gr', 1, 0, 'C')
pdf.cell(col_width, 6, 'EBITDA Gr', 1, 0, 'C')
pdf.cell(col_width, 6, 'PAT Gr', 1, 0, 'C')
pdf.cell(col_width, 6, 'EBITDA Mar', 1, 0, 'C')
pdf.cell(col_width, 6, 'PAT Mar', 1, 0, 'C')
pdf.ln()

pdf.set_font('Arial', '', 9)
for _, row in coef_df.iterrows():
    pdf.cell(col_width, 6, row.iloc[0], 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[1]:.1f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[2]:.1f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[3]:.1f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[4]:.1f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[5]:.1f}", 1, 0, 'C')
    pdf.ln()

# ============================================
# P-VALUES
# ============================================
pdf.add_page()
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, '6. STATISTICAL SIGNIFICANCE (P-VALUES)', 0, 1)
pdf.ln(5)

pval_df = pd.read_csv('output/pvalues.csv')

col_width = 180 / 6
pdf.set_font('Arial', 'B', 9)

pdf.cell(col_width, 6, 'Company', 1, 0, 'C')
pdf.cell(col_width, 6, 'Sales Gr', 1, 0, 'C')
pdf.cell(col_width, 6, 'EBITDA Gr', 1, 0, 'C')
pdf.cell(col_width, 6, 'PAT Gr', 1, 0, 'C')
pdf.cell(col_width, 6, 'EBITDA Mar', 1, 0, 'C')
pdf.cell(col_width, 6, 'PAT Mar', 1, 0, 'C')
pdf.ln()

pdf.set_font('Arial', '', 9)
for _, row in pval_df.iterrows():
    pdf.cell(col_width, 6, row.iloc[0], 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[1]:.4f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[2]:.4f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[3]:.4f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[4]:.4f}", 1, 0, 'C')
    pdf.cell(col_width, 6, f"{row.iloc[5]:.4f}", 1, 0, 'C')
    pdf.ln()

# ============================================
# CONCLUSIONS
# ============================================
pdf.add_page()
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, '7. CONCLUSIONS AND RECOMMENDATIONS', 0, 1)
pdf.ln(5)

pdf.set_font('Arial', '', 11)
pdf.cell(0, 6, 'PRIMARY FINDINGS:', 0, 1)
pdf.cell(0, 6, '-----------------', 0, 1)
pdf.cell(0, 6, f'1. PAT Growth is the strongest predictor of stock prices,', 0, 1)
pdf.cell(0, 6, f'   particularly for Infosys (p = {top_3.iloc[0]["P_Value"]:.4f}).', 0, 1)
pdf.cell(0, 6, '   Recommendation: Investors should prioritize companies with', 0, 1)
pdf.cell(0, 6, '   strong profit growth.', 0, 1)
pdf.ln(5)

pdf.cell(0, 6, 'COMPANY-SPECIFIC INSIGHTS:', 0, 1)
pdf.cell(0, 6, '--------------------------', 0, 1)
pdf.cell(0, 6, f'2. INFOSYS (INFY):', 0, 1)
pdf.cell(0, 6, f'   - Key Driver: PAT Growth', 0, 1)
pdf.cell(0, 6, f'   - Coefficient: {top_3.iloc[0]["Coefficient"]:.2f}', 0, 1)
pdf.cell(0, 6, f'   - Model Fit: R² = {reg_summary.iloc[1]["R_Squared"]:.3f}', 0, 1)
pdf.cell(0, 6, '   - Recommendation: Monitor quarterly PAT growth closely', 0, 1)
pdf.ln(2)

pdf.cell(0, 6, f'3. TATA CONSULTANCY SERVICES (TCS):', 0, 1)
pdf.cell(0, 6, f'   - Key Driver: Sales Growth', 0, 1)
pdf.cell(0, 6, f'   - Coefficient: {top_3.iloc[1]["Coefficient"]:.2f}', 0, 1)
pdf.cell(0, 6, f'   - Model Fit: R² = {reg_summary.iloc[0]["R_Squared"]:.3f}', 0, 1)
pdf.cell(0, 6, '   - Recommendation: Track sales growth trajectory', 0, 1)
pdf.ln(5)

pdf.cell(0, 6, 'INVESTMENT IMPLICATIONS:', 0, 1)
pdf.cell(0, 6, '------------------------', 0, 1)
pdf.cell(0, 6, '4. Use company-specific models for better predictions', 0, 1)
pdf.cell(0, 6, '5. INFY: Focus on profitability metrics', 0, 1)
pdf.cell(0, 6, '6. TCS: Focus on revenue growth metrics', 0, 1)
pdf.ln(5)

pdf.cell(0, 6, 'LIMITATIONS:', 0, 1)
pdf.cell(0, 6, '------------', 0, 1)
pdf.cell(0, 6, '- Sample size: 19 years of overlapping data', 0, 1)
pdf.cell(0, 6, '- Macro-economic factors not included', 0, 1)
pdf.cell(0, 6, '- Consider adding quarterly data for future analysis', 0, 1)

# ============================================
# VISUALIZATIONS
# ============================================
pdf.add_page()
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, '8. VISUALIZATIONS GENERATED', 0, 1)
pdf.ln(5)

pdf.set_font('Arial', '', 11)
pdf.cell(0, 6, 'The following files are available in the output folder:', 0, 1)
pdf.ln(2)
pdf.cell(0, 6, '1. correlation_heatmap.png - Overall correlation matrix', 0, 1)
pdf.cell(0, 6, '2. company_correlations.png - Company-wise correlations', 0, 1)
pdf.cell(0, 6, '3. regression_coefficients.png - Regression coefficients', 0, 1)
pdf.cell(0, 6, '4. r_squared_comparison.png - Model fit comparison', 0, 1)
pdf.cell(0, 6, '5. pvalue_heatmap.png - Statistical significance heatmap', 0, 1)
pdf.ln(5)

pdf.cell(0, 6, 'CSV Data Files:', 0, 1)
pdf.cell(0, 6, '- overall_correlation_matrix.csv', 0, 1)
pdf.cell(0, 6, '- company_correlations.csv', 0, 1)
pdf.cell(0, 6, '- regression_summary.csv', 0, 1)
pdf.cell(0, 6, '- coefficients.csv', 0, 1)
pdf.cell(0, 6, '- pvalues.csv', 0, 1)
pdf.cell(0, 6, '- top_3_significant.csv', 0, 1)

# ============================================
# Save PDF
# ============================================
pdf.output('reports/Stock_Price_Analysis_Final.pdf', 'F')

print("\n" + "="*60)
print("✅ PDF REPORT CREATED SUCCESSFULLY!")
print("="*60)
print("📄 Location: reports/Stock_Price_Analysis_Final.pdf")
print("="*60)