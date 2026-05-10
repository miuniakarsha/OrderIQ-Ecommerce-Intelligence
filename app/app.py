import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import urllib

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="E-Commerce Analytics Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    # Fixed connection string
    params = urllib.parse.quote_plus(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-8G4F56T7\\SQLEXPRESS;"
        "DATABASE=OrderIqDB;"
        "Trusted_Connection=yes;"
    )
    
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")
    
    # Complete query with all calculated fields
    query = """
    SELECT 
        o.order_id,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_delivered_timestamp,
        o.order_estimated_delivery_date,
        c.customer_city,
        c.customer_state,
        oi.price,
        oi.shipping_charges,
        pymt.payment_type,
        pymt.payment_value,
        -- Calculated fields
        CASE 
            WHEN o.order_delivered_timestamp IS NOT NULL THEN 1 
            ELSE 0 
        END AS is_delivered,
        CASE 
            WHEN o.order_delivered_timestamp > o.order_estimated_delivery_date THEN 1 
            ELSE 0 
        END AS is_late,
        DATEDIFF(DAY, o.order_purchase_timestamp, 
                 ISNULL(o.order_delivered_timestamp, GETDATE())) AS delivery_time,
        YEAR(o.order_purchase_timestamp) AS order_year,
        MONTH(o.order_purchase_timestamp) AS order_month,
        FORMAT(o.order_purchase_timestamp, 'yyyy-MM') AS order_month_year
    FROM orders o
        LEFT JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        LEFT JOIN payments pymt ON o.order_id = pymt.order_id
    WHERE o.order_status != 'canceled'
    """
    
    df = pd.read_sql(query, engine)
    
    # Convert to datetime
    if 'order_purchase_timestamp' in df.columns:
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Handle null values
    df['delivery_time'] = df['delivery_time'].fillna(0)
    df['is_delivered'] = df['is_delivered'].fillna(0)
    df['is_late'] = df['is_late'].fillna(0)
    
    return df

# Load data with error handling
try:
    df = load_data()
    st.success(" Data loaded successfully!")
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please check your database connection and ensure the table exists")
    st.stop()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("Filters")

# State filter
states = st.sidebar.multiselect(
    "Select State",
    options=df['customer_state'].unique(),
    default=df['customer_state'].unique()
)

# Status filter
status = st.sidebar.multiselect(
    "Order Status",
    options=df['order_status'].unique(),
    default=df['order_status'].unique()
)

# Date filter (if available)
if 'order_purchase_timestamp' in df.columns:
    min_date = df['order_purchase_timestamp'].min()
    max_date = df['order_purchase_timestamp'].max()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date]
    )

    df = df[
        (df['order_purchase_timestamp'] >= pd.to_datetime(date_range[0])) &
        (df['order_purchase_timestamp'] <= pd.to_datetime(date_range[1]))
    ]

# Apply filters
df = df[
    (df['customer_state'].isin(states)) &
    (df['order_status'].isin(status))
]

# ---------------- TITLE ----------------
st.title("E-Commerce Analytics Dashboard")
st.markdown("### Real-time Business Insights")
st.markdown("---")

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)

total_orders = df['order_id'].nunique()
delivered = df[df['is_delivered'] == 1].shape[0]
late = df[df['is_late'] == 1].shape[0]
avg_delivery = df['delivery_time'].mean()

delivery_rate = (delivered / total_orders) * 100 if total_orders > 0 else 0
late_rate = (late / total_orders) * 100 if total_orders > 0 else 0

col1.metric("Total Orders", total_orders)
col2.metric("Delivery Rate (%)", round(delivery_rate, 2))
col3.metric("Late Delivery (%)", round(late_rate, 2))
col4.metric("Avg Delivery Time", round(avg_delivery, 2))

st.markdown("---")

# ---------------- CHARTS ----------------

# Orders Trend
st.subheader("Orders Trend Over Time")
trend = df.groupby('order_month')['order_id'].count().reset_index()
fig1 = px.line(trend, x='order_month', y='order_id', markers=True)
st.plotly_chart(fig1, use_container_width=True)

# Orders by State
st.subheader("Orders by State")
state = df.groupby('customer_state')['order_id'].count().reset_index()
fig2 = px.bar(state, x='customer_state', y='order_id', color='order_id')
st.plotly_chart(fig2, use_container_width=True)

# Order Status by State
st.subheader("Order Status by State")
status_df = df.groupby(['customer_state','order_status']).size().reset_index(name='count')
fig3 = px.bar(status_df, x='customer_state', y='count', color='order_status', barmode='stack')
st.plotly_chart(fig3, use_container_width=True)

# Pie Chart
st.subheader("Order Status Distribution")
pie = df['order_status'].value_counts().reset_index()
pie.columns = ['status','count']
fig4 = px.pie(pie, values='count', names='status', hole=0.4)
st.plotly_chart(fig4, use_container_width=True)

# Delivery Performance
st.subheader("Average Delivery Time by Status")
delivery = df.groupby('order_status')['delivery_time'].mean().reset_index()
fig5 = px.bar(delivery, x='order_status', y='delivery_time', color='delivery_time')
st.plotly_chart(fig5, use_container_width=True)

# ---------------- EXTRA INSIGHTS ----------------

# Top States
st.subheader("Top 10 States by Orders")
top_states = df['customer_state'].value_counts().head(10)
st.bar_chart(top_states)

# Late Deliveries by State
st.subheader("Late Deliveries by State")
late_state = df[df['is_late'] == 1]['customer_state'].value_counts().head(10)
st.bar_chart(late_state)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("E-Commerce Analytics Dashboard | Built with Streamlit | Data from OrderIqDB")