import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Fetch Company Data from yfinance
def get_company_data(ticker):
    company = yf.Ticker(ticker)

    # Get financial statements
    income_statement = company.financials.T
    balance_sheet = company.balance_sheet.T
    cash_flow = company.cashflow.T

    # Get historical stock price data
    stock_data = company.history(period="5y")

    return income_statement, balance_sheet, cash_flow, stock_data

# Step 2: Calculate Key Ratios
def calculate_ratios(income_statement, balance_sheet):
    gross_margin = income_statement['Gross Profit'] / income_statement['Total Revenue']
    operating_margin = income_statement['Operating Income'] / income_statement['Total Revenue']
    net_profit_margin = income_statement['Net Income'] / income_statement['Total Revenue']
    debt_to_equity = balance_sheet['Total Liabilities'] / balance_sheet['Total Stockholder Equity']

    return {
        'gross_margin': gross_margin,
        'operating_margin': operating_margin,
        'net_profit_margin': net_profit_margin,
        'debt_to_equity': debt_to_equity
    }

# Step 3: Project Future Financials
def project_financials(income_statement, net_profit_margin, growth_rate=0.10, years=5):
    initial_revenue = income_statement['Total Revenue'][-1]
    revenue_projections = [initial_revenue * (1 + growth_rate)**i for i in range(years)]
    net_income_projections = [rev * net_profit_margin[-1] for rev in revenue_projections]

    return revenue_projections, net_income_projections

# Step 4: Perform Discounted Cash Flow (DCF) Valuation
def dcf_valuation(net_income_projections, cash_flow, discount_rate=0.10, terminal_growth_rate=0.02):
    fcf_to_net_income_ratio = cash_flow['Free Cash Flow'][-1] / income_statement['Net Income'][-1]
    free_cash_flow_projections = [ni * fcf_to_net_income_ratio for ni in net_income_projections]

    # Terminal value calculation
    terminal_value = free_cash_flow_projections[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)

    # Discount projected cash flows
    discounted_fcf = [fcf / (1 + discount_rate)**(i + 1) for i, fcf in enumerate(free_cash_flow_projections)]
    discounted_terminal_value = terminal_value / (1 + discount_rate)**len(free_cash_flow_projections)

    # Enterprise value
    enterprise_value = sum(discounted_fcf) + discounted_terminal_value
    return enterprise_value

# Step 5: Sensitivity Analysis
def sensitivity_analysis(net_income_projections, cash_flow, discount_rates, terminal_growth_rate):
    results = []
    fcf_to_net_income_ratio = cash_flow['Free Cash Flow'][-1] / income_statement['Net Income'][-1]
    free_cash_flow_projections = [ni * fcf_to_net_income_ratio for ni in net_income_projections]
    terminal_value = free_cash_flow_projections[-1] * (1 + terminal_growth_rate) / (discount_rates[0] - terminal_growth_rate)

    for rate in discount_rates:
        discounted_fcf = [fcf / (1 + rate)**(i + 1) for i, fcf in enumerate(free_cash_flow_projections)]
        discounted_terminal_value = terminal_value / (1 + rate)**len(free_cash_flow_projections)
        enterprise_value = sum(discounted_fcf) + discounted_terminal_value
        results.append((rate, enterprise_value))
    
    return results

# Step 6: Visualizations
def visualize_projections(years, revenue_projections, net_income_projections):
    plt.plot(years, revenue_projections, marker='o', label="Revenue Projections", color='blue')
    plt.plot(years, net_income_projections, marker='x', label="Net Income Projections", color='green')
    plt.title('Revenue and Net Income Projections')
    plt.xlabel('Year')
    plt.ylabel('Amount ($)')
    plt.legend()
    plt.grid(True)
    plt.show()

def visualize_sensitivity(discount_rates, ev_sensitivity):
    plt.plot(discount_rates, ev_sensitivity, marker='o', color='red')
    plt.title('Sensitivity of Enterprise Value to Discount Rate')
    plt.xlabel('Discount Rate')
    plt.ylabel('Enterprise Value ($)')
    plt.grid(True)
    plt.show()

# Main Function
if __name__ == "__main__":
    ticker = "AAPL"  # Example: Apple
    income_statement, balance_sheet, cash_flow, stock_data = get_company_data(ticker)
    
    # Calculate ratios
    ratios = calculate_ratios(income_statement, balance_sheet)
    print("Financial Ratios:")
    print(ratios)

    # Projections
    growth_rate = 0.10  # Assume 10% revenue growth
    projection_years = ['2023', '2024', '2025', '2026', '2027']
    revenue_projections, net_income_projections = project_financials(income_statement, ratios['net_profit_margin'], growth_rate)

    # Valuation
    discount_rate = 0.10
    terminal_growth_rate = 0.02
    enterprise_value = dcf_valuation(net_income_projections, cash_flow, discount_rate, terminal_growth_rate)
    print(f"Enterprise Value: ${enterprise_value:,.2f}")

    # Sensitivity Analysis
    discount_rates = np.linspace(0.08, 0.12, 5)
    sensitivity_results = sensitivity_analysis(net_income_projections, cash_flow, discount_rates, terminal_growth_rate)

    ev_sensitivity = [ev for _, ev in sensitivity_results]
    for rate, ev in sensitivity_results:
        print(f"Enterprise Value at {rate:.2%} discount rate: ${ev:,.2f}")

    # Visualize Projections and Sensitivity Analysis
    visualize_projections(projection_years, revenue_projections, net_income_projections)
    visualize_sensitivity(discount_rates, ev_sensitivity)
