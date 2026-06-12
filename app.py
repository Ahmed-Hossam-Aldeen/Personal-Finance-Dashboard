import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from parse_data import load_and_process_data
from datetime import timedelta

# --- SET PAGE CONFIG ---
st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

# --- APP START ---
st.title("🏦 Your Transaction & Transfer Dashboard")
load_file = st.sidebar.file_uploader("Upload XML File", type="xml")

if load_file is not None:
    target_bank = st.sidebar.selectbox("Select Target Bank", ["BanK-AlAhly", "CIB"])
    last_4_digits = st.sidebar.text_input("Enter Last 4 Digits of Card", type="password")
    if last_4_digits is not None and len(last_4_digits) == 4 and last_4_digits.isdigit() and target_bank is not None:
        try:
            df_transactions, df_transfers = load_and_process_data(load_file, last_4_digits, target_bank)
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.stop()
    else:
        st.warning("Please enter the last 4 digits of the card to match it with the messages correctly!")
        st.stop()
else:
    st.info("### Please upload an XML file containing your SMS messages")
    st.info("""You can use the [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore)
    application to manage your messages effectively.
    """)
    st.stop()

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["🛒 Card Transactions", "💸 Instapay Transfers", "🎯 Monthly Budget"])

if not df_transactions.empty or not df_transfers.empty:
    # Reset date filters if bank or card digits changed to prevent date mismatch errors
    state_key = f"{target_bank}_{last_4_digits}"
    if st.session_state.get("last_state_key") != state_key:
        st.session_state.last_state_key = state_key
        if "date_input_key" in st.session_state:
            del st.session_state.date_input_key
        if "preset_option" in st.session_state:
            del st.session_state.preset_option

    st.sidebar.header("Filter Settings")
    
    # Safely compute min and max dates across populated DataFrames
    dates = []
    if not df_transactions.empty:
        dates.extend([df_transactions['Date'].min(), df_transactions['Date'].max()])
    if not df_transfers.empty:
        dates.extend([df_transfers['Date'].min(), df_transfers['Date'].max()])
        
    min_date = min(dates).date()
    max_date = (max(dates) + timedelta(days=1)).date()

    # Pre-calculate relative preset ranges
    today = datetime.now().date()
    
    # 1. This Week (Monday to today/max_date)
    this_week_start = max_date - timedelta(days = 7)
    this_week_end = max_date
    
    # 2. This Month (1st of this month to today/max_date)
    start_of_month = today.replace(day=1)
    this_month_start = max(start_of_month, min_date)
    this_month_end = min(today, max_date)
    
    # 3. Last Month (1st of last month to end of last month)
    last_month_end_date = today.replace(day=1) - timedelta(days=1)
    start_of_last_month = last_month_end_date.replace(day=1)
    last_month_start = max(start_of_last_month, min_date)
    last_month_end = min(last_month_end_date, max_date)

    # Initialize state variables
    if "date_input_key" not in st.session_state:
        st.session_state.date_input_key = [min_date, max_date]

    if "preset_option" not in st.session_state:
        st.session_state.preset_option = "All Time"

    # Callbacks for synchronization
    def on_preset_change():
        selected = st.session_state.preset_option
        if selected == "This Week":
            st.session_state.date_input_key = [this_week_start, this_week_end]
        elif selected == "This Month":
            st.session_state.date_input_key = [this_month_start, this_month_end]
        elif selected == "Last Month":
            st.session_state.date_input_key = [last_month_start, last_month_end]
        elif selected == "All Time":
            st.session_state.date_input_key = [min_date, max_date]

    def on_date_input_change():
        val = st.session_state.date_input_key
        if len(val) == 2:
            if val[0] == this_week_start and val[1] == this_week_end:
                st.session_state.preset_option = "This Week"
            elif val[0] == this_month_start and val[1] == this_month_end:
                st.session_state.preset_option = "This Month"
            elif val[0] == last_month_start and val[1] == last_month_end:
                st.session_state.preset_option = "Last Month"
            elif val[0] == min_date and val[1] == max_date:
                st.session_state.preset_option = "All Time"
            else:
                st.session_state.preset_option = "Custom Range"

    # Render Preset Dropdown
    st.sidebar.selectbox(
        "Select Date Preset",
        ["All Time", "This Week", "This Month", "Last Month", "Custom Range"],
        key="preset_option",
        on_change=on_preset_change
    )

    # Render Custom Date Input
    date_range = st.sidebar.date_input(
        "Select Time Window",
        min_value=min_date,
        max_value=max_date,
        key="date_input_key",
        on_change=on_date_input_change
    )

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


    with tab3:
        st.subheader("Monthly Budget")
        df_sent = df_filtered_transf[df_filtered_transf['Type'] == 'Sent']

        budget = st.slider("Select Budget", min_value=0, max_value=100000, value=7000, step=500)
        fixed_expenses = st.number_input("Duplicated Expenses", value=7000)
        purchases = int(df_filtered_trans['Amount'].sum())
        transfers = int(df_sent['Amount'].sum()) 
        
        total_spent_raw = purchases + transfers
        total_spent = total_spent_raw - fixed_expenses
        remaining = budget - total_spent

        st.markdown("### 📊 Financial Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("🛒 Purchases", f"{purchases} EGP")
        col2.metric("💸 Transfers", f"{transfers} EGP")
        col3.metric("🧾 Total Spent", f"{total_spent} EGP", help="Purchases + Transfers - Fixed Expenses")
        
        delta_text = f"{(remaining / budget) * 100:.1f}% left" if budget > 0 else ""
        col4.metric("💰 Remaining", f"{remaining} EGP", delta=delta_text, delta_color="normal")

        # Add a visual progress bar for budget usage
        budget_usage_pct = (total_spent / budget) if budget > 0 else 0.0
        st.markdown(f"**Budget Usage:** `{max(0, budget_usage_pct * 100):.1f}%`")
        st.progress(min(max(budget_usage_pct, 0.0), 1.0))