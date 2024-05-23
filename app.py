import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd

# MongoDB connection
client = MongoClient("mongodb+srv://shantnu4755:llBAXH3svUhwY8u2@cluster0.0hoccsd.mongodb.net/?retryWrites=true&w=majority")
db = client.transactionDB
transactions_collection = db.transactions

# Streamlit application
st.title("Office Transactions")

# Function to display transactions
def display_transactions():
    transactions = list(transactions_collection.find().sort("date", 1))  # Sort in ascending order by date
    running_balance = 0
    data = []
    for transaction in transactions:
        if 'credit' in transaction:
            running_balance += transaction['credit']
            credit = transaction['credit']
            debit = '-'
        elif 'debit' in transaction:
            running_balance -= transaction['debit']
            credit = '-'
            debit = transaction['debit']
        data.append([
            transaction['date'].strftime('%Y-%m-%d'),
            transaction['description'],
            credit,
            debit,
            running_balance
        ])
    
    df = pd.DataFrame(data, columns=["Date", "Description", "Credit", "Debit", "Running Balance"])
    st.table(df)

# Function to add a new transaction
def add_transaction():
    with st.form("add_transaction_form"):
        date = st.date_input("Date")
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        transaction_type = st.selectbox("Type", ["Credit", "Debit"])
        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            transaction = {
                "date": datetime.strptime(str(date), '%Y-%m-%d'),
                "description": description,
                "amount": amount,
                "type": transaction_type
            }
            if transaction_type == "Credit":
                transaction['credit'] = amount
            else:
                transaction['debit'] = amount
            transactions_collection.insert_one(transaction)
            st.success("Transaction added successfully")
            st.session_state.add_transaction = False  # Reset the state
            st.experimental_rerun()  # Refresh the page to show the new transaction

# Check if the user wants to add a transaction
if 'add_transaction' not in st.session_state:
    st.session_state.add_transaction = False

# Button to navigate to add transaction page
if st.button("Add Transaction"):
    st.session_state.add_transaction = True

# Show add transaction form if the user clicked the button
if st.session_state.add_transaction:
    add_transaction()
    if st.button("Back to Transactions"):
        st.session_state.add_transaction = False
        st.experimental_rerun()
else:
    st.header("Transactions")
    display_transactions()
