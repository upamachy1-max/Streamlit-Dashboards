import streamlit as st
import pandas as pd
import altair as alt

# Load cleaned data
df = pd.read_csv("idlc_clean.csv")
df['Date'] = pd.to_datetime(df['Date'])

st.set_page_config(page_title="IDLC Stock Dashboard", layout="wide")
st.title("IDLC Finance PLC Stock Dashboard")

# Sidebar controls
st.sidebar.header("Controls")
start_date = st.sidebar.date_input("Start date", df['Date'].min())
end_date = st.sidebar.date_input("End date", df['Date'].max())
show_ma20 = st.sidebar.checkbox("Show MA20", True)
show_ma50 = st.sidebar.checkbox("Show MA50", True)
show_ma200 = st.sidebar.checkbox("Show MA200", True)

# Filter data based on sidebar date selection
mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
df_filtered = df.loc[mask]

# Summary metrics with dates
highest_close = df_filtered['Close'].max()
highest_close_date = df_filtered.loc[df_filtered['Close'].idxmax(), 'Date']

lowest_close = df_filtered['Close'].min()
lowest_close_date = df_filtered.loc[df_filtered['Close'].idxmin(), 'Date']

total_volume = df_filtered['Volume'].sum()
cumulative_return = df_filtered['Cumulative_Return'].iloc[-1]
cumulative_return_date = df_filtered['Date'].iloc[-1]

st.subheader("Summary Metrics")
col1, col2, col3, col4 = st.columns(4)

col1.metric(label="Highest Close", value=f"{highest_close:.2f}", delta=f"{highest_close_date.date()}")
col2.metric(label="Lowest Close", value=f"{lowest_close:.2f}", delta=f"{lowest_close_date.date()}")
col3.metric(label="Total Volume", value=f"{total_volume}", delta="")
col4.metric(label="Cumulative Return", value=f"{cumulative_return:.4f}", delta=f"{cumulative_return_date.date()}")

# Close Price + Moving Averages (full width)
st.subheader("Close Price & Moving Averages")
ma_columns = ['Close']
if show_ma20:
    ma_columns.append('MA20')
if show_ma50:
    ma_columns.append('MA50')
if show_ma200:
    ma_columns.append('MA200')

price_ma_chart = alt.Chart(df_filtered).transform_fold(
    ma_columns,
    as_=['Metric', 'Value']
).mark_line().encode(
    x='Date:T',
    y='Value:Q',
    color='Metric:N',
    tooltip=['Date:T', 'Metric:N', 'Value:Q']
).interactive()
st.altair_chart(price_ma_chart, use_container_width=True)

# Side-by-side charts for Daily Return and Cumulative Return
st.subheader("Returns")
col1, col2 = st.columns(2)

with col1:
    st.write("Daily Return")
    daily_return_chart = alt.Chart(df_filtered).mark_line(color='green').encode(
        x='Date:T',
        y='Daily_Return:Q',
        tooltip=['Date:T', 'Daily_Return:Q']
    ).interactive()
    st.altair_chart(daily_return_chart, use_container_width=True)

with col2:
    st.write("Cumulative Return")
    cumulative_return_chart = alt.Chart(df_filtered).mark_line(color='blue').encode(
        x='Date:T',
        y='Cumulative_Return:Q',
        tooltip=['Date:T', 'Cumulative_Return:Q']
    ).interactive()
    st.altair_chart(cumulative_return_chart, use_container_width=True)

# Side-by-side charts for Volume and 30-Day Rolling Volatility
st.subheader("Volume & Volatility")
col1, col2 = st.columns(2)

with col1:
    st.write("Volume")
    volume_chart = alt.Chart(df_filtered).mark_bar(color='orange').encode(
        x='Date:T',
        y='Volume:Q',
        tooltip=['Date:T', 'Volume:Q']
    ).interactive()
    st.altair_chart(volume_chart, use_container_width=True)

with col2:
    st.write("30-Day Rolling Volatility")
    vol_chart = alt.Chart(df_filtered).mark_line(color='red').encode(
        x='Date:T',
        y='Volatility_30:Q',
        tooltip=['Date:T', 'Volatility_30:Q']
    ).interactive()
    st.altair_chart(vol_chart, use_container_width=True)

# Pie chart for positive vs negative daily returns
st.subheader("Positive vs Negative Daily Returns")
pos_neg_counts = df_filtered['Daily_Return'].apply(lambda x: 'Positive' if x > 0 else 'Negative').value_counts().reset_index()
pos_neg_counts.columns = ['Return_Type', 'Count']

pie_chart = alt.Chart(pos_neg_counts).mark_arc(innerRadius=50).encode(
    theta='Count:Q',
    color='Return_Type:N',
    tooltip=['Return_Type:N', 'Count:Q']
)
st.altair_chart(pie_chart, use_container_width=True)
