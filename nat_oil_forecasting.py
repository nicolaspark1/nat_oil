import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Load data
file_path = 'Nat_Gas.csv'  # Ensure the file path is correct
nat_gas_data = pd.read_csv(file_path)

# Convert dates to datetime format and set frequency
nat_gas_data['Dates'] = pd.to_datetime(nat_gas_data['Dates'], format='%m/%d/%y')
nat_gas_data.set_index('Dates', inplace=True)
nat_gas_data.index.freq = 'ME'  # Month-end frequency

# Plot the historical data to visualize
plt.figure(figsize=(12, 6))
plt.plot(nat_gas_data.index, nat_gas_data['Prices'], marker='o')
plt.title("Historical Natural Gas Prices")
plt.xlabel("Date")
plt.ylabel("Price")
plt.grid(True)
plt.show()

# Decompose time series to observe trend and seasonality
decomposition = seasonal_decompose(nat_gas_data['Prices'], model='additive', period=12)
plt.figure(figsize=(12, 10))
plt.subplot(4, 1, 1)
plt.plot(nat_gas_data['Prices'], label='Original')
plt.legend(loc='upper left')
plt.subplot(4, 1, 2)
plt.plot(decomposition.trend, label='Trend')
plt.legend(loc='upper left')
plt.subplot(4, 1, 3)
plt.plot(decomposition.seasonal, label='Seasonal')
plt.legend(loc='upper left')
plt.subplot(4, 1, 4)
plt.plot(decomposition.resid, label='Residual')
plt.legend(loc='upper left')
plt.tight_layout()
plt.show()

# Fit an exponential smoothing model with trend and seasonality components
model = ExponentialSmoothing(nat_gas_data['Prices'], trend='add', seasonal='add', seasonal_periods=12)
fitted_model = model.fit()

# Forecast for an additional 12 months
forecast = fitted_model.forecast(steps=12)
forecast_index = pd.date_range(start=nat_gas_data.index[-1] + pd.DateOffset(months=1), periods=12, freq='ME')
forecast_series = pd.Series(forecast, index=forecast_index)

# Plot the forecast with historical data
plt.figure(figsize=(12, 6))
plt.plot(nat_gas_data['Prices'], label='Historical Prices', marker='o')
plt.plot(forecast_series, label='Forecasted Prices', marker='o', linestyle='--')
plt.title("Natural Gas Prices - Historical and Forecasted")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True)
plt.show()

# Function to estimate price for any given date
def estimate_price(date_str):
    """
    Estimate the natural gas price for a specified date.
    
    Parameters:
        date_str (str): Date in 'YYYY-MM-DD' format.
        
    Returns:
        float or str: Estimated price or message if date is out of range.
    """
    date = pd.to_datetime(date_str)
    if date <= nat_gas_data.index[-1]:  # Within historical data range
        return fitted_model.predict(start=date, end=date).iloc[0]
    elif date <= forecast_series.index[-1]:  # Within forecasted range
        return forecast_series[date]
    else:
        return "Date out of forecast range. Please choose a date within the next year."

# Interactive input for date estimation
date_input = input("Enter a date in YYYY-MM-DD format to estimate the natural gas price: ")
estimated_price = estimate_price(date_input)
print(f"Estimated price on {date_input}: {estimated_price}")
