from flask import Flask, render_template, request, redirect, url_for
import csv

# This creates my flask application. (__name__) is a special python variable that means "This file"
app = Flask(__name__)

# a "route" is a path in my app
@app.route('/') #when someone visits the home page(/)
def index():#this function is called#
    return render_template('index.html') # this then shows the index.html files from the templates folder






if __name__ == '__main__': # This checks if this file is being run directly and not just being "imported"
    app.run(debug=True) # this automatically reloads when i change code, really useful
