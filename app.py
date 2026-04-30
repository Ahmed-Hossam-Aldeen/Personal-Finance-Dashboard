import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from parse_data import load_and_process_data
from datetime import timedelta

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
    max_date = max(df_transactions['Date'].max(), df_transfers['Date'].max()).date() + timedelta(days=1)

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

        c1, c2 = st.columns(2)
        
        fig_cat = px.pie(df_filtered_trans, values='Amount', names='Category', title="Spending by Category", hole=0.4)
        c1.plotly_chart(fig_cat, use_container_width=True)
        
        fig_trend = px.line(df_filtered_trans.sort_values('Date'), x='Date', y='Amount', title="Daily Spending Trend", markers=True)
        c2.plotly_chart(fig_trend, use_container_width=True)

        top_merch = df_filtered_trans.groupby(['Merchant', 'Category']).agg(
            Amount=('Amount', 'sum'),
            Frequency=('Amount', 'count')
        ).reset_index().sort_values('Amount', ascending=False)

        # 2. Filter for merchants visited more than once for a specific "Loyalty" insight
        frequent_merch = top_merch[top_merch['Frequency'] > 1].sort_values('Frequency', ascending=False)

        # 3. Enhanced Bar Chart: Shows Amount, but adds Frequency to the hover tooltip
        fig_merch = px.bar(
            top_merch, 
            x='Merchant', 
            y='Amount', 
            color='Category', 
            title="Top Spending Locations",
            hover_data={'Frequency': True} # This adds the visit count to the popup
)
        st.plotly_chart(fig_merch, use_container_width=True)
        # 4. New Section: Frequency Leaderboard
        if not frequent_merch.empty:
            st.subheader("🔁 Habitual Merchants (Visited > 1 time)")
            
            # Optional: Visualizing frequency specifically
            fig_freq = px.bar(
                frequent_merch.head(10), 
                x='Frequency', 
                y='Merchant', 
                orientation='h',
                color='Category',
                title="Top 10 Merchants by Visit Frequency",
                text='Frequency'
            )
            fig_freq.update_traces(textposition='outside')
            st.plotly_chart(fig_freq, use_container_width=True)
            
        st.subheader("Transaction Details")
        st.dataframe(df_filtered_trans.sort_values('Date', ascending=False), use_container_width=True)

# --- TAB 2: TRANSFERS ---
with tab2:
    df_received = df_filtered_transf[df_filtered_transf['Type'] == 'Received']
    df_sent = df_filtered_transf[df_filtered_transf['Type'] == 'Sent']
    sent = df_sent['Amount'].sum()
    received = df_received['Amount'].sum()

    col1, col2 = st.columns(2)
    col1.metric("Sent Count", len(df_sent))
    col2.metric("Received Count", len(df_received))
    
    col3, col4 = st.columns(2)
    col3.metric("Total Sent", f"{sent:,.2f} EGP", delta_color="inverse")
    col4.metric("Total Received", f"{received:,.2f} EGP")

    fig_flow = px.histogram(df_filtered_transf, x="Date", y="Amount", color="Type", barmode="group", title="Daily Sent vs Received")
    st.plotly_chart(fig_flow, use_container_width=True)
    
    # Aggregate both Sum and Count for Sent transfers
    top_sent_parties = df_sent.groupby('Party').agg(
        Total_Amount=('Amount', 'sum'),
        Frequency=('Amount', 'count')
    ).reset_index().sort_values('Total_Amount', ascending=False)

    st.divider()
    # Bar chart with Frequency in hover data
    fig_sent = px.bar(
        top_sent_parties, 
        x='Party', 
        y='Total_Amount', 
        color='Total_Amount', 
        title="Top Receiving Parties (By Amount)",
        hover_data={'Frequency': True},
        labels={'Total_Amount': 'Total EGP', 'Frequency': 'Times Sent'}
    )
    st.plotly_chart(fig_sent, use_container_width=True)

    # Optional: Show a small leaderboard for frequent recipients
    frequent_sent = top_sent_parties[top_sent_parties['Frequency'] > 1].sort_values('Frequency', ascending=False)
    if not frequent_sent.empty:
        st.write("🔄 **Frequent Recipients:**")
        st.dataframe(frequent_sent[['Party', 'Frequency', 'Total_Amount']].head(5), hide_index=True)
    st.divider()

    # Aggregate both Sum and Count for Received transfers
    top_received_parties = df_received.groupby('Party').agg(
        Total_Amount=('Amount', 'sum'),
        Frequency=('Amount', 'count')
    ).reset_index().sort_values('Total_Amount', ascending=False)

    # Bar chart with Frequency in hover data
    fig_received = px.bar(
        top_received_parties, 
        x='Party', 
        y='Total_Amount', 
        color='Total_Amount', 
        title="Top Sending Parties (By Amount)",
        hover_data={'Frequency': True},
        labels={'Total_Amount': 'Total EGP', 'Frequency': 'Times Received'}
    )
    st.plotly_chart(fig_received, use_container_width=True)

    # Optional: Show a small leaderboard for frequent senders
    frequent_received = top_received_parties[top_received_parties['Frequency'] > 1].sort_values('Frequency', ascending=False)
    if not frequent_received.empty:
        st.write("📩 **Frequent Senders:**")
        st.dataframe(frequent_received[['Party', 'Frequency', 'Total_Amount']].head(5), hide_index=True)
    
    st.divider()
    st.subheader("All Transfers")
    st.dataframe(df_filtered_transf.sort_values('Date', ascending=False), use_container_width=True)