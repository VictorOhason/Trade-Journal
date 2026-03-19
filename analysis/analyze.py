import pandas as pd
import matplotlib.pyplot as plt

csv_path = 'data/trades.csv'

try:
    df = pd.read_csv(csv_path, parse_dates=['date'])
except FileNotFoundError:
    print('CSV file not found:', csv_path)
    raise

if df.empty:
    print('No rows in CSV. Add some trades first.')
    raise SystemExit(0)

# Convert types
(df['date']) = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
df['entry'] = pd.to_numeric(df['entry'], errors='coerce').fillna(0)
df['exit'] = pd.to_numeric(df['exit'], errors='coerce').fillna(0)
df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)

# Metrics
print('Total trades:', len(df))
print('Total profit:', df['profit'].sum())
print('Win rate:', (df['profit'] > 0).mean() * 100, '%')
print('Average profit:', df['profit'].mean())

# Plots
import os
charts_dir = 'static/charts'
os.makedirs(charts_dir, exist_ok=True)

profit_by_asset = df.groupby('asset')['profit'].sum().sort_values(ascending=False)
plt.figure(figsize=(8,4))
profit_by_asset.plot(kind='bar', color='#4CAF50')
plt.title('Total Profit by Asset')
plt.ylabel('Profit')
plt.tight_layout()
plt.savefig(f'{charts_dir}/profit_by_asset.png')
plt.close()


cum = df.sort_values('date')
cum['cum_profit']= cum['profit'].cumsum()
plt.figure(figsize=(8,4))
plt.plot(cum['date'], cum['cum_profit'], marker='o')
plt.title('Cumulative Profit Over Time')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f'{charts_dir}/cum_profit.png')
plt.close()

print('Charts saved in', charts_dir)
