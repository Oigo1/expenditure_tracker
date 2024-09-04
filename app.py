from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import schedule
import time

app = Flask(__name__)

# Path to the CSV file for storing expenditure data
DATA_FILE = 'data/expenditures.csv'

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# Function to initialize the CSV file if it doesn't exist or is empty
def initialize_csv():
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        df = pd.DataFrame(columns=['Date', 'Description', 'Amount'])
        df.to_csv(DATA_FILE, index=False)

# Call the initialization function
initialize_csv()

# Function to add an expenditure entry
def add_entry(date, description, amount):
    df = pd.read_csv(DATA_FILE)
    new_entry = pd.DataFrame({'Date': [date], 'Description': [description], 'Amount': [amount]})
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# Function to get all expenditure entries
def get_entries():
    df = pd.read_csv(DATA_FILE)
    return df

# Daily check for reminding the user
def daily_check():
    df = pd.read_csv(DATA_FILE)
    today = pd.Timestamp.now().strftime('%Y-%m-%d')
    if not (df['Date'] == today).any():
        print("Reminder: You haven't entered your expenditure for today.")

# Schedule the reminder
schedule.every().day.at("20:00").do(daily_check)

# Route for the home page
@app.route('/')
def index():
    entries = get_entries()
    return render_template('index.html', entries=entries)

# Route for adding a new entry
@app.route('/add', methods=['POST'])
def add():
    date = request.form['date']
    description = request.form['description']
    amount = request.form['amount']
    add_entry(date, description, amount)
    return redirect(url_for('index'))

# Route for generating and showing the statement
@app.route('/statement')
def statement():
    entries = get_entries()
    return render_template('statement.html', entries=entries)

if __name__ == '__main__':
    app.run(debug=True)

    # Start the reminder scheduler in a loop
    while True:
        schedule.run_pending()
        time.sleep(1)
