import streamlit as st
import pandas as pd
import plotly.express as px
import s3fs


st.set_page_config(page_title="Stock Market Analytics Pro", layout="wide")


st.title(" Pro Stock Market Analytics Dashboard")
st.markdown("---")


BUCKET_NAME = "your bucket name"
FILE_PATH = f's3://{BUCKET_NAME}/transformed_data/stock_data.parquet'


@st.cache_data
def load_data():

    df = pd.read_parquet(FILE_PATH)

    df['event_time'] = pd.to_datetime(df['event_time'])
    return df


try:
    df = load_data()

    # --- SIDEBAR FILTER ---
    st.sidebar.header("Filter Options")
    all_stocks = sorted(df['symbol'].unique())
    selected_stock = st.sidebar.selectbox("Select a Stock Symbol", all_stocks)


    filtered_df = df[df['symbol'] == selected_stock].sort_values('event_time')

    # --- TOP METRICS ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", len(df))
    col2.metric("Total Stocks", len(all_stocks))

    latest_price = filtered_df['price'].iloc[-1] if not filtered_df.empty else 0
    col3.metric(f"Current {selected_stock} Price", f"₹{latest_price}")


    avg_price = round(df['price'].mean(), 2)
    col4.metric("Market Avg Price", f"₹{avg_price}")

    st.markdown("---")

    # --- GRAPHS ---
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader(f" {selected_stock} Price Trend")
        if not filtered_df.empty:
            fig_line = px.line(filtered_df, x='event_time', y='price',
                               markers=True, title=f"Time vs Price for {selected_stock}")
            st.plotly_chart(fig_line, width='stretch')
        else:
            st.write("No data available for this stock.")

    with right_col:
        st.subheader(" Top 5 Stocks by Max Price")
        top_5 = df.groupby('symbol')['price'].max().sort_values(ascending=False).head(5).reset_index()
        fig_bar = px.bar(top_5, x='symbol', y='price', color='symbol', text_auto='.2s')
        st.plotly_chart(fig_bar, width='stretch')

    # --- DATA TABLE ---
    st.markdown("---")
    st.subheader(" Recent Processed Transactions")
    st.dataframe(df.sort_values('event_time', ascending=False).head(50), width='stretch')

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Check your AWS credentials and S3 Path.")