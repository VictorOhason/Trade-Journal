from flask import Flask, render_template, request, redirect, url_for
import csv

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
    # read all trades from csv
    trades = []
    try:
        with open('data/trades.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader) # skips the header row
            for row in reader:
                if row: # making sure row isnt empty
                    trades.append(row)
    except:
        trades = []
    return render_template('dashboard.html', trades=trades)
                
    




if __name__ == '__main__': # This checks if this file is being run directly and not just being "imported"
    app.run(debug=True) # this automatically reloads when i change code, really useful
