import streamlit as st
import pandas as pd
import altair as alt
from pathlib import Path

# Load CSS
css_path = Path(__file__).parent / "assets" / "theme.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# Load data
df = pd.read_csv("idlc_clean.csv")
df['Date'] = pd.to_datetime(df['Date'])

st.set_page_config(page_title="IDLC Stock Dashboard", layout="wide")

# Add logo and title in the same row
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("IDLC.png", width=120)
with col_title:
    st.markdown("<h1 style='margin-top: 20px;'>IDLC Finance PLC Stock Dashboard</h1>", unsafe_allow_html=True)

# Sidebar controls
st.sidebar.header("Controls")
start_date = st.sidebar.date_input("Start date", df['Date'].min())
end_date = st.sidebar.date_input("End date", df['Date'].max())
show_ma20 = st.sidebar.checkbox("Show MA20", True)
show_ma50 = st.sidebar.checkbox("Show MA50", True)
show_ma200 = st.sidebar.checkbox("Show MA200", True)

# Filter data
mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
df_filtered = df.loc[mask]

# Summary metrics
highest_close = df_filtered['Close'].max()
highest_close_date = df_filtered.loc[df_filtered['Close'].idxmax(), 'Date']
lowest_close = df_filtered['Close'].min()
lowest_close_date = df_filtered.loc[df_filtered['Close'].idxmin(), 'Date']
total_volume = df_filtered['Volume'].sum()
cumulative_return = df_filtered['Cumulative_Return'].iloc[-1]
cumulative_return_date = df_filtered['Date'].iloc[-1]

st.subheader("Summary Metrics")

# Add custom CSS for colored date text
st.markdown("""
<style>
.custom-metric {
    background-color: transparent !important;
    padding: 1rem;
}
.metric-label {
    color: rgba(255, 255, 255, 0.7) !important;
    font-size: 14px !important;
    margin-bottom: 0.5rem;
}
.metric-value {
    color: #ffffff !important;
    font-size: 28px !important;
    font-weight: 600 !important;
    margin-bottom: 0.25rem;
}
.metric-date-green {
    color: #10b981 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}
.metric-date-red {
    color: #ef4444 !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}
.metric-date-normal {
    color: rgba(255, 255, 255, 0.6) !important;
    font-size: 14px !important;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="custom-metric">
        <div class="metric-label">Highest Close</div>
        <div class="metric-value">{highest_close:.2f}</div>
        <div class="metric-date-green">↑ {highest_close_date.date()}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="custom-metric">
        <div class="metric-label">Lowest Close</div>
        <div class="metric-value">{lowest_close:.2f}</div>
        <div class="metric-date-red">↓ {lowest_close_date.date()}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="custom-metric">
        <div class="metric-label">Total Volume</div>
        <div class="metric-value">{total_volume:,}</div>
        <div class="metric-date-normal"></div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="custom-metric">
        <div class="metric-label">Cumulative Return</div>
        <div class="metric-value">{cumulative_return:.4f}</div>
        <div class="metric-date-green">↑ {cumulative_return_date.date()}</div>
    </div>
    """, unsafe_allow_html=True)

# Charts helper function - FIXED to match dark theme
def style_chart(chart):
    return chart.configure_view(
        strokeWidth=0,
        fill='#002244'  # Match your background color
    ).configure_axis(
        labelColor='white',
        titleColor='white',
        gridColor='rgba(255,255,255,0.1)',
        domainColor='rgba(255,255,255,0.3)'
    ).configure_legend(
        labelColor='white',
        titleColor='white',
        fillColor='rgba(0,34,68,0.8)',
        strokeColor='rgba(255,255,255,0.3)'
    ).configure_title(
        color='white'
    ).properties(
        background='#002244'
    ).interactive()

# Close Price + Moving Averages
st.subheader("Close Price & Moving Averages")
ma_columns = ['Close']
if show_ma20: ma_columns.append('MA20')
if show_ma50: ma_columns.append('MA50')
if show_ma200: ma_columns.append('MA200')

price_ma_chart = alt.Chart(df_filtered).transform_fold(
    ma_columns,
    as_=['Metric', 'Value']
).mark_line(strokeWidth=2).encode(
    x=alt.X('Date:T', title='Date'),
    y=alt.Y('Value:Q', title='Price'),
    color=alt.Color('Metric:N', scale=alt.Scale(scheme='category10')),
    tooltip=['Date:T', 'Metric:N', 'Value:Q']
)

st.altair_chart(style_chart(price_ma_chart), use_container_width=True)

# Daily & Cumulative Return
st.subheader("Returns")
col1, col2 = st.columns(2)

with col1:
    st.write("Daily Return")
    daily_return_chart = alt.Chart(df_filtered).mark_line(color='#10b981', strokeWidth=2).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Daily_Return:Q', title='Daily Return'),
        tooltip=['Date:T', 'Daily_Return:Q']
    )
    st.altair_chart(style_chart(daily_return_chart), use_container_width=True)

with col2:
    st.write("Cumulative Return")
    cumulative_return_chart = alt.Chart(df_filtered).mark_line(color='#3b82f6', strokeWidth=2).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Cumulative_Return:Q', title='Cumulative Return'),
        tooltip=['Date:T', 'Cumulative_Return:Q']
    )
    st.altair_chart(style_chart(cumulative_return_chart), use_container_width=True)

# Volume & Volatility
st.subheader("Volume & Volatility")
col1, col2 = st.columns(2)

with col1:
    st.write("Volume")
    volume_chart = alt.Chart(df_filtered).mark_bar(color='#f59e0b').encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Volume:Q', title='Volume'),
        tooltip=['Date:T', 'Volume:Q']
    )
    st.altair_chart(style_chart(volume_chart), use_container_width=True)

with col2:
    st.write("30-Day Rolling Volatility")
    vol_chart = alt.Chart(df_filtered).mark_line(color='#ef4444', strokeWidth=2).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Volatility_30:Q', title='Volatility'),
        tooltip=['Date:T', 'Volatility_30:Q']
    )
    st.altair_chart(style_chart(vol_chart), use_container_width=True)

# Pie chart for positive vs negative daily returns
st.subheader("Positive vs Negative Daily Returns")
pos_neg_counts = df_filtered['Daily_Return'].apply(lambda x: 'Positive' if x > 0 else 'Negative').value_counts().reset_index()
pos_neg_counts.columns = ['Return_Type', 'Count']

pie_chart = alt.Chart(pos_neg_counts).mark_arc(innerRadius=50).encode(
    theta=alt.Theta('Count:Q'),
    color=alt.Color('Return_Type:N', scale=alt.Scale(domain=['Positive', 'Negative'], range=['#10b981', '#ef4444'])),
    tooltip=['Return_Type:N', 'Count:Q']
)

st.altair_chart(style_chart(pie_chart), use_container_width=True)