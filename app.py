from flask import Flask, render_template, request, redirect, url_for, flash
from decimal import Decimal
import mysql.connector as sql

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Establish MySQL connection
def get_db_connection():
    conn = sql.connect(host='localhost', user='root', password='geobhavan1$',port=3306, database='expensetracker')
    return conn

# Initialize balance
def initialize_balance():
    conn = get_db_connection()
    c1 = conn.cursor()
    c1.execute("SELECT total_balance FROM balance ORDER BY id DESC LIMIT 1")
    balance_row = c1.fetchone()
    conn.close()
    if balance_row:
        return Decimal(balance_row[0])
    else:
        conn = get_db_connection()
        c1 = conn.cursor()
        c1.execute("INSERT INTO balance (total_balance) VALUES (0)")
        conn.commit()
        conn.close()
        return Decimal(0)

# Update balance in the database
def update_balance(new_balance):
    conn = get_db_connection()
    c1 = conn.cursor()
    c1.execute("INSERT INTO balance (total_balance) VALUES (%s)", (str(new_balance),))  # Insert balance as string
    conn.commit()
    conn.close()

@app.route('/')
def index():
    balance = initialize_balance()
    conn = get_db_connection()
    c1 = conn.cursor()
    c1.execute("SELECT expense_name, amount, expense_date FROM expenses")
    expenses = c1.fetchall()
    conn.close()
    return render_template('index.html', balance=balance, expenses=expenses)

@app.route('/add_initial_budget', methods=['POST'])
def add_initial_budget():
    if request.method == 'POST':
        initial_amount = Decimal(request.form['initial_amount'])
        balance = initialize_balance() + initial_amount
        update_balance(balance)
        flash(f"Initial amount of Rs. {initial_amount} added successfully!", "success")
    return redirect(url_for('index'))

@app.route('/add_extra_budget', methods=['POST'])
def add_extra_budget():
    if request.method == 'POST':
        extra_budget = Decimal(request.form['extra_budget'])
        balance = initialize_balance() + extra_budget
        update_balance(balance)
        flash(f"Extra budget of Rs. {extra_budget} added successfully!", "success")
    return redirect(url_for('index'))

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if request.method == 'POST':
        expense_name = request.form['expense_name']
        expense_amount = Decimal(request.form['expense_amount'])
        balance = initialize_balance()

        if expense_amount <= balance:
            conn = get_db_connection()
            c1 = conn.cursor()
            c1.execute("INSERT INTO expenses (expense_name, amount) VALUES (%s, %s)", (expense_name, str(expense_amount)))
            conn.commit()
            conn.close()
            balance -= expense_amount
            update_balance(balance)
            flash(f"Expense '{expense_name}' of Rs. {expense_amount} added successfully!", "success")
        else:
            flash("Insufficient balance to add this expense!", "danger")
    return redirect(url_for('index'))

@app.route('/delete_expense/<int:id>', methods=['POST'])
def delete_expense(id):
    conn = get_db_connection()
    c1 = conn.cursor()
    c1.execute("SELECT amount FROM expenses WHERE id = %s", (id,))
    data = c1.fetchone()

    if data:
        balance = initialize_balance() + Decimal(data[0])
        c1.execute("DELETE FROM expenses WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        update_balance(balance)
        flash("Expense deleted successfully!", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
