import pandas as pd
import numpy as np
from datetime import datetime

# Logging setup
import logging
logging.basicConfig(filename='contract_pricing.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Load natural gas price data
df = pd.read_csv('natgas_R.csv', parse_dates=['Dates'], date_format='%m/%d/%y')
prices = df['Prices'].values
dates = df['Dates'].values

# establish start date
start_date = pd.Timestamp('2020-10-31')
days_from_start = [(day - start_date).days for day in dates]


# Interpolation function
def interpolate(date):
    days = (date - pd.Timestamp('2020-10-31')).days
    if days in days_from_start:
        return prices[days_from_start.index(days)]
    else:
        return amplitude * np.sin(days * 2 * np.pi / 365 + shift) + days * slope + intercept

# Contract value calculation
def calculate_contract_value(
    injection_date, withdrawal_date, volume, injection_rate,
    withdrawal_rate, max_storage, storage_cost_per_month,
    injection_cost_per_mmbtu, withdrawal_cost_per_mmbtu, transportation_cost
):
    if volume > max_storage:
        raise ValueError("Volume exceeds maximum storage capacity.")
    if injection_date >= withdrawal_date:
        raise ValueError("Injection date must be earlier than withdrawal date.")

    injection_price = interpolate(pd.Timestamp(injection_date))
    withdrawal_price = interpolate(pd.Timestamp(withdrawal_date))

    revenue = volume * (withdrawal_price - injection_price)
    storage_duration = (withdrawal_date.year - injection_date.year) * 12 + (withdrawal_date.month - injection_date.month)
    total_storage_cost = storage_cost_per_month * storage_duration
    injection_cost = injection_cost_per_mmbtu * volume
    withdrawal_cost = withdrawal_cost_per_mmbtu * volume
    total_costs = total_storage_cost + injection_cost + withdrawal_cost + transportation_cost
    contract_value = revenue - total_costs

    logging.info(f"Calculated Revenue: {revenue}, Costs: {total_costs}, Contract Value: {contract_value}")
    return contract_value

# Main logic
if __name__ == "__main__":
    try:
        # Get user inputs
        injection_date = pd.Timestamp(input("Enter injection date (YYYY-MM-DD): "))
        withdrawal_date = pd.Timestamp(input("Enter withdrawal date (YYYY-MM-DD): "))
        volume = float(input("Enter the volume to store (MMBtu): "))
        injection_rate = float(input("Enter the injection rate (MMBtu/day): "))
        withdrawal_rate = float(input("Enter the withdrawal rate (MMBtu/day): "))
        max_storage = float(input("Enter the maximum storage capacity (MMBtu): "))
        storage_cost_per_month = float(input("Enter the storage cost per month ($): "))
        injection_cost_per_mmbtu = float(input("Enter the injection cost per MMBtu ($): "))
        withdrawal_cost_per_mmbtu = float(input("Enter the withdrawal cost per MMBtu ($): "))
        transportation_cost = float(input("Enter the transportation cost ($): "))

        # Calculate contract value
        contract_value = calculate_contract_value(
            injection_date, withdrawal_date, volume, injection_rate,
            withdrawal_rate, max_storage, storage_cost_per_month,
            injection_cost_per_mmbtu, withdrawal_cost_per_mmbtu, transportation_cost
        )
        print(f"\nContract Value: ${contract_value:,.2f}")

        # Save results
        output = {
            "Injection Date": injection_date,
            "Withdrawal Date": withdrawal_date,
            "Volume (MMBtu)": volume,
            "Contract Value ($)": contract_value,
        }
        output_df = pd.DataFrame([output])
        output_df.to_csv('contract_pricing_output.csv', index=False)
        print("Contract value saved to 'contract_pricing_output.csv'.")
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"An error occurred: {e}")
