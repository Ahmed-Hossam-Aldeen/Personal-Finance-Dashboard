import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from parse_data import load_and_process_data

# --- SET PAGE CONFIG ---
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

# --- APP START ---
st.title("🏦 NBE Transaction & Transfer Dashboard")
load_file = st.sidebar.file_uploader("Upload XML File", type="xml")

if load_file is not None:
    last_4_digits = st.sidebar.text_input("Enter Last 4 Digits of Card", type="password")
    if last_4_digits is not None and len(last_4_digits) == 4:
        try:
            df_transactions, df_transfers = load_and_process_data(load_file, last_4_digits)
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()
    else:
        st.warning("Please enter the last 4 digits of the card")
        st.stop()
else:
    st.warning("Please upload an XML file containing NBE SMS messages")
    st.stop()

# --- TABS ---
tab1, tab2 = st.tabs(["🛒 Card Transactions", "💸 Instapay Transfers"])

# --- SIDEBAR FILTERS ---
if not df_transactions.empty:
    st.sidebar.header("Filter Settings")
    min_date = min(df_transactions['Date'].min(), df_transfers['Date'].min()).date()
    max_date = max(df_transactions['Date'].max(), df_transfers['Date'].max()).date()

    date_range = st.sidebar.date_input("Select Time Window", [min_date, max_date], min_value=min_date, max_value=max_date)

    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        # Apply filtering
        mask_trans = (df_transactions['Date'] >= start_date) & (df_transactions['Date'] <= end_date)
        mask_transfers = (df_transfers['Date'] >= start_date) & (df_transfers['Date'] <= end_date)
        df_filtered_trans = df_transactions.loc[mask_trans]
        df_filtered_transf = df_transfers.loc[mask_transfers]
    else:
        df_filtered_trans = df_transactions
        df_filtered_transf = df_transfers


    # --- TAB 1: TRANSACTIONS ---
    with tab1:
        col1, col2 = st.columns(2)
        col1.metric("Total Spent", f"{df_filtered_trans['Amount'].sum():,.2f} EGP")
        col2.metric("Transaction Count", len(df_filtered_trans))

        st.subheader("Spending Analysis")
        c1, c2 = st.columns(2)
        
        fig_cat = px.pie(df_filtered_trans, values='Amount', names='Category', title="Spending by Category", hole=0.4)
        c1.plotly_chart(fig_cat, use_container_width=True)
        
        fig_trend = px.line(df_filtered_trans.sort_values('Date'), x='Date', y='Amount', title="Daily Spending Trend", markers=True)
        c2.plotly_chart(fig_trend, use_container_width=True)

        st.subheader("Top Merchants")
        top_merch = df_filtered_trans.groupby('Merchant')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
        fig_merch = px.bar(top_merch, x='Merchant', y='Amount', color='Amount', title="Top Spending Locations")
        st.plotly_chart(fig_merch, use_container_width=True)

        st.subheader("Transaction Details")
        st.dataframe(df_filtered_trans.sort_values('Date', ascending=False), use_container_width=True)
# --- TAB 2: TRANSFERS ---
with tab2:
    df_recieved = df_filtered_transf[df_filtered_transf['Type'] == 'Received']
    df_sent = df_filtered_transf[df_filtered_transf['Type'] == 'Sent']
    sent = df_sent['Amount'].sum()
    received = df_recieved['Amount'].sum()

    col1, col2 = st.columns(2)
    col1.metric("Sent Count", len(df_sent))
    col2.metric("Received Count", len(df_recieved))
    
    col3, col4 = st.columns(2)
    col3.metric("Total Sent", f"{sent:,.2f} EGP", delta_color="inverse")
    col4.metric("Total Received", f"{received:,.2f} EGP")

    fig_flow = px.histogram(df_filtered_transf, x="Date", y="Amount", color="Type", barmode="group", title="Daily Sent vs Received")
    st.plotly_chart(fig_flow, use_container_width=True)

    top_merch = df_sent.groupby('Party')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
    fig_merch = px.bar(top_merch, x='Party', y='Amount', color='Amount', title="Top Spending Locations")
    st.plotly_chart(fig_merch, use_container_width=True)

    top_merch = df_recieved.groupby('Party')['Amount'].sum().reset_index().sort_values('Amount', ascending=False)
    fig_merch = px.bar(top_merch, x='Party', y='Amount', color='Amount', title="Top Spending Locations")
    st.plotly_chart(fig_merch, use_container_width=True)

    st.subheader("Transfer Details")
    st.dataframe(df_filtered_transf.sort_values('Date', ascending=False), use_container_width=True)