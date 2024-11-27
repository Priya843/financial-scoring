import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Load and preprocess data
def load_and_preprocess(data):
    df = pd.DataFrame(data)
    df = df.drop_duplicates()  # Remove duplicates
    return df

# Create family-level summary
def aggregate_family_data(df):
    family_data = df.groupby('Family ID').agg({
        'Income': 'mean',
        'Savings': 'mean',
        'Monthly Expenses': 'mean',
        'Loan Payments': 'mean',
        'Credit Card Spending': 'mean',
        'Financial Goals Met (%)': 'mean'
    }).reset_index()
    
    family_data['Savings_to_Income_Ratio'] = family_data['Savings'] / family_data['Income']
    family_data['Expenses_to_Income_Percentage'] = family_data['Monthly Expenses'] / family_data['Income']
    family_data['Loan_to_Income_Percentage'] = family_data['Loan Payments'] / family_data['Income']
    return family_data

# Add discretionary spending and normalize data
def calculate_discretionary_spending(df, family_data):
    discretionary_categories = ['Travel', 'Entertainment', 'Food']
    total_spending = df.groupby('Family ID')['Amount'].sum().reset_index()
    discretionary_spending = df[df['Category'].isin(discretionary_categories)].groupby('Family ID')['Amount'].sum().reset_index()
    discretionary_spending.rename(columns={'Amount': 'Discretionary_Spending'}, inplace=True)
    
    spending_data = pd.merge(total_spending, discretionary_spending, on='Family ID', how='left').fillna(0)
    spending_data['Discretionary_Spending_Percentage'] = spending_data['Discretionary_Spending'] / spending_data['Amount']
    
    family_data = pd.merge(family_data, spending_data[['Family ID', 'Discretionary_Spending_Percentage']], on='Family ID', how='left')
    return family_data

# Normalize and calculate financial score
def calculate_financial_score(family_data):
    scaler = MinMaxScaler()
    factors_to_normalize = [
        'Savings_to_Income_Ratio',
        'Expenses_to_Income_Percentage',
        'Loan_to_Income_Percentage',
        'Discretionary_Spending_Percentage',
        'Financial Goals Met (%)'
    ]
    
    family_data_normalized = family_data.copy()
    family_data_normalized[factors_to_normalize] = scaler.fit_transform(family_data[factors_to_normalize])
    
    weights = {
        'Savings_to_Income_Ratio': 0.25,
        'Expenses_to_Income_Percentage': 0.20,
        'Loan_to_Income_Percentage': 0.15,
        'Discretionary_Spending_Percentage': 0.20,
        'Financial Goals Met (%)': 0.10
    }
    
    family_data_normalized['Financial_Score'] = (
        family_data_normalized['Savings_to_Income_Ratio'] * weights['Savings_to_Income_Ratio'] +
        (1 - family_data_normalized['Expenses_to_Income_Percentage']) * weights['Expenses_to_Income_Percentage'] +
        (1 - family_data_normalized['Loan_to_Income_Percentage']) * weights['Loan_to_Income_Percentage'] +
        (1 - family_data_normalized['Discretionary_Spending_Percentage']) * weights['Discretionary_Spending_Percentage'] +
        family_data_normalized['Financial Goals Met (%)'] * weights['Financial Goals Met (%)']
    )
    
    family_data_normalized['Financial_Score'] *= 100
    return family_data_normalized

# Generate recommendations
def generate_recommendations(row):
    recommendations = []
    if row['Financial_Score'] < 50:
        recommendations.append("Increase savings and reduce unnecessary expenses.")
    elif 50 <= row['Financial_Score'] < 75:
        recommendations.append("Consider optimizing your savings further.")
    else:
        recommendations.append("You're doing great. Keep up the good work!")
    return recommendations

def add_recommendations(family_data_normalized):
    family_data_normalized['Recommendations'] = family_data_normalized.apply(generate_recommendations, axis=1)
    return family_data_normalized

# Main function to process and score data
def process_financial_data(data):
    df = load_and_preprocess(data)
    family_data = aggregate_family_data(df)
    family_data = calculate_discretionary_spending(df, family_data)
    family_data_normalized = calculate_financial_score(family_data)
    family_data_with_recommendations = add_recommendations(family_data_normalized)
    return family_data_with_recommendations.to_dict(orient='records')
