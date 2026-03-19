from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt

# This creates my flask application. (__name__) is a special python variable that means "This file"
app = Flask(__name__)

# a "route" is a path in my app
@app.route('/') #when someone visits the home page(/)
def index():#this function is called#
    return render_template('index.html') # this then shows the index.html files from the templates folder

@app.route('/submit', methods = ['POST']) # Listens for POST requests to /submit
def submit_trade(): # function to get and store data in csv file format
    #get the form data
    date = request.form['date']
    asset = request.form['asset']
    direction = request.form['direction']
    quantity = request.form['quantity']
    entry = request.form['entry']
    exit_price = request.form['exit']
    comment = request.form.get('comment', '')
    
    # Calculate profit
    # Profit = (Exit - Entry) * Quantity, Long positive when price rises, Short reversed
    entry_float = float(entry)
    exit_float = float(exit_price)
    quantity_float = float(quantity)
    
    if direction == 'Long':
        profit = (exit_float - entry_float) * quantity_float
    else:  # Short
        profit = (entry_float - exit_float) * quantity_float
        
    # Append a proper row to CSV (use exit_price once, no duplicate exit field)
    with open('data/trades.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date, asset, direction, quantity, entry, exit_price, profit, comment])
        
    # Redirect to dashboard to see the newly logged trade
    return redirect(url_for('show_dashboard'))

@app.route('/dashboard')
def show_dashboard():
    # read all trades from CSV with Pandas
    charts_dir = os.path.join('static', 'charts')
    os.makedirs(charts_dir, exist_ok=True)

    try:
        df = pd.read_csv('data/trades.csv', parse_dates=['date'])
    except Exception:
        df = pd.DataFrame()

    if df.empty:
        # no data rows
        return render_template('dashboard.html', trades=[], total_trades=0,
                               total_profit=0, win_rate=0, avg_profit=0,
                               charts={})

    # Ensure correct types
    df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
    df['entry'] = pd.to_numeric(df['entry'], errors='coerce').fillna(0)
    df['exit'] = pd.to_numeric(df['exit'], errors='coerce').fillna(0)
    df['profit'] = pd.to_numeric(df['profit'], errors='coerce').fillna(0)

    # Metrics
    total_trades = len(df)
    total_profit = round(df['profit'].sum(), 2)
    win_rate = round((df['profit'] > 0).mean() * 100, 2) if total_trades > 0 else 0
    avg_profit = round(df['profit'].mean(), 2) if total_trades > 0 else 0

    # Charts
    chart_paths = {}

    try:
        # Profit by asset (bar)
        profit_by_asset = df.groupby('asset')['profit'].sum().sort_values(ascending=False)
        plt.figure(figsize=(8, 4))
        profit_by_asset.plot(kind='bar', color='#4CAF50')
        plt.title('Total Profit by Asset')
        plt.ylabel('Profit')
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, 'profit_by_asset.png')
        plt.savefig(chart_path)
        plt.close()
        chart_paths['profit_by_asset'] = 'charts/profit_by_asset.png'

        # Cumulative profit over time (line)
        df_sorted = df.sort_values('date')
        df_sorted['cum_profit'] = df_sorted['profit'].cumsum()
        plt.figure(figsize=(8, 4))
        plt.plot(df_sorted['date'], df_sorted['cum_profit'], marker='o', color='#007ACC')
        plt.title('Cumulative Profit Over Time')
        plt.ylabel('Cumulative Profit')
        plt.xlabel('Date')
        plt.xticks(rotation=45)
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, 'cum_profit.png')
        plt.savefig(chart_path)
        plt.close()
        chart_paths['cum_profit'] = 'charts/cum_profit.png'

        # Profit distribution (histogram)
        plt.figure(figsize=(8, 4))
        plt.hist(df['profit'], bins=10, color='#FFA500', edgecolor='black')
        plt.title('Distribution of Trade Profits')
        plt.xlabel('Profit')
        plt.ylabel('Frequency')
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, 'profit_hist.png')
        plt.savefig(chart_path)
        plt.close()
        chart_paths['profit_hist'] = 'charts/profit_hist.png'

        # Win/Loss ratio (pie)
        win_count = (df['profit'] > 0).sum()
        loss_count = (df['profit'] <= 0).sum()
        plt.figure(figsize=(6, 6))
        plt.pie([win_count, loss_count], labels=['Wins', 'Losses'], autopct='%1.0f%%', colors=['#4CAF50', '#E53935'])
        plt.title('Win/Loss Ratio')
        plt.tight_layout()
        chart_path = os.path.join(charts_dir, 'win_ratio.png')
        plt.savefig(chart_path)
        plt.close()
        chart_paths['win_ratio'] = 'charts/win_ratio.png'
    except Exception:
        chart_paths = {}

    # Keep the row data as list of lists for template
    trades = df.to_records(index=False).tolist()

    return render_template('dashboard.html', trades=trades,
                           total_trades=total_trades,
                           total_profit=total_profit,
                           win_rate=win_rate,
                           avg_profit=avg_profit,
                           charts=chart_paths)

@app.route('/download')
def download_csv():
    return send_file('data/trades.csv', as_attachment=True, download_name='trades.csv', mimetype='text/csv')
