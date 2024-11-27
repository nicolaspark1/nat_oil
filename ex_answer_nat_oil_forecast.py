import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from datetime import date, timedelta

# Load data from CSV and parse dates
df = pd.read_csv('natgas_R.csv', parse_dates=['Dates'], date_parser=lambda x: pd.to_datetime(x, format='%m/%d/%y'))
prices = df['Prices'].values
dates = df['Dates'].values

# Plot prices against dates
fig, ax = plt.subplots()
ax.plot(dates, prices, '-')
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.set_title('Natural Gas Prices')
ax.tick_params(axis='x', rotation=45)
plt.savefig('natural_gas_prices.png')  # Save plot as image
plt.show()

# Define start and end dates
start_date = date(2020, 10, 31)
end_date = date(2024, 9, 30)

# Generate a list of end-of-month dates from start_date to end_date
months = []
year = start_date.year
month = start_date.month + 1
while True:
    current = date(year, month, 1) + timedelta(days=-1)
    months.append(current)
    if current.month == end_date.month and current.year == end_date.year:
        break
    else:
        month = ((month + 1) % 12) or 12
        if month == 1:
            year += 1

# Calculate days from the start date
days_from_start = [(day - start_date).days for day in months]

# Simple linear regression to fit a model y = Ax + B
def simple_regression(x, y):
    xbar = np.mean(x)
    ybar = np.mean(y)
    slope = np.sum((x - xbar) * (y - ybar)) / np.sum((x - xbar)**2)
    intercept = ybar - slope * xbar
    return slope, intercept

time = np.array(days_from_start)
slope, intercept = simple_regression(time, prices)

# Plot linear trend
plt.plot(dates, prices, label='Prices')
plt.plot(dates, time * slope + intercept, label='Linear Trend')
plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Linear Trend of Monthly Input Prices')
plt.legend()
plt.savefig('linear_trend.png')
plt.show()
print("Slope:", slope, "Intercept:", intercept)

# Remove linear trend and apply sinusoidal regression for seasonal pattern
sin_prices = prices - (time * slope + intercept)
sin_time = np.sin(time * 2 * np.pi / 365)
cos_time = np.cos(time * 2 * np.pi / 365)

# Bilinear regression to capture amplitude and phase shift of seasonality
def bilinear_regression(y, x1, x2):
    slope1 = np.sum(y * x1) / np.sum(x1 ** 2)
    slope2 = np.sum(y * x2) / np.sum(x2 ** 2)
    return slope1, slope2

slope1, slope2 = bilinear_regression(sin_prices, sin_time, cos_time)
amplitude = np.sqrt(slope1 ** 2 + slope2 ** 2)
shift = np.arctan2(slope2, slope1)

# Plot sinusoidal fit
plt.plot(dates, amplitude * np.sin(time * 2 * np.pi / 365 + shift), label='Sinusoidal Fit')
plt.plot(dates, sin_prices, label='Prices (Detrended)')
plt.title('Smoothed Estimate of Monthly Input Prices')
plt.legend()
plt.savefig('sinusoidal_fit.png')
plt.show()

# Define the interpolation/extrapolation function
def interpolate(date):
    days = (date - pd.Timestamp(start_date)).days
    if days in days_from_start:
        # Exact match found in the data
        return prices[days_from_start.index(days)]
    else:
        # Interpolate/extrapolate using the sin/cos model
        return amplitude * np.sin(days * 2 * np.pi / 365 + shift) + days * slope + intercept

# Create a range of continuous dates from start date to end date
continuous_dates = pd.date_range(start=pd.Timestamp(start_date), end=pd.Timestamp(end_date), freq='D')

# Plot the smoothed estimate of the full dataset using interpolation
plt.plot(continuous_dates, [interpolate(date) for date in continuous_dates], label='Smoothed Estimate')

# Plot the fitted sinusoidal curve along with actual prices
x = np.array(days_from_start)
y = np.array(prices)
plt.plot(dates, y, 'o', label='Monthly Input Prices')
plt.plot(continuous_dates, amplitude * np.sin((continuous_dates - pd.Timestamp(start_date)).days * 2 * np.pi / 365 + shift) + (continuous_dates - pd.Timestamp(start_date)).days * slope + intercept, label='Fit to Sine Curve')

plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Natural Gas Prices')
plt.legend()
plt.savefig('final_fit.png')
plt.show()
