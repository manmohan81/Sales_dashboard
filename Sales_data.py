import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(page_title="Retail Dashboard", layout="wide")

# Sidebar: File uploader
st.sidebar.title("📁 Upload Excel File")
uploaded_file = st.sidebar.file_uploader("Upload your retail Excel file", type=["xlsx", "xls"])

# Load data after upload
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Month'] = df['Date'].dt.to_period('M')
    return df

# Proceed only if file is uploaded
if uploaded_file:
    df = load_data(uploaded_file)

    # Sidebar Filters
    st.sidebar.title("🔍 Filters")
    branches = st.sidebar.multiselect("Select Branch", df['Branch'].unique(), default=df['Branch'].unique())
    customer_types = st.sidebar.multiselect("Select Customer Type", df['Customer_type'].unique(), default=df['Customer_type'].unique())
    cities = st.sidebar.multiselect("Select City", df['City'].unique(), default=df['City'].unique())
    genders = st.sidebar.multiselect("Select Gender", df['Gender'].unique(), default=df['Gender'].unique())
    products = st.sidebar.multiselect("Select Product Line", df['Product line'].unique(), default=df['Product line'].unique())

    # Apply filters
    filtered_df = df[
        (df['Branch'].isin(branches)) &
        (df['Customer_type'].isin(customer_types)) &
        (df['City'].isin(cities)) &
        (df['Gender'].isin(genders)) &
        (df['Product line'].isin(products))
    ]

    # Dashboard Title
    st.title("📊 Retail Sales Dashboard")

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${filtered_df['Total'].sum():,.2f}")
    col2.metric("Total Profit", f"${filtered_df['gross income'].sum():,.2f}")
    col3.metric("Avg. Rating", f"{filtered_df['Rating'].mean():.2f} ⭐")

    st.markdown("---")

    # Sales by Product Line
    st.subheader("🛍️ Sales by Product Line")
    sales_by_product = filtered_df.groupby("Product line")['Total'].sum().reset_index()
    chart = alt.Chart(sales_by_product).mark_bar().encode(
        x=alt.X('Product line', sort='-y'),
        y='Total',
        color='Product line'
    ).properties(width=700, height=400)
    st.altair_chart(chart)

    # Profit by Branch
    st.subheader("🏢 Gross Income by Branch")
    profit_by_branch = filtered_df.groupby("Branch")['gross income'].sum()
    st.bar_chart(profit_by_branch)

    # Payment Method Distribution
    st.subheader("💳 Payment Method Distribution")
    payment_counts = filtered_df['Payment'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(payment_counts, labels=payment_counts.index, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

    # Monthly Sales Trend
    st.subheader("📈 Monthly Sales Trend")
    monthly_sales = filtered_df.groupby('Month')['Total'].sum().reset_index()
    monthly_sales['Month'] = monthly_sales['Month'].astype(str)
    st.line_chart(monthly_sales.set_index('Month'))

    # Customer Type Distribution
    st.subheader("👥 Customer Type Distribution")
    cust_dist = filtered_df['Customer_type'].value_counts()
    st.bar_chart(cust_dist)

    # Ratings by Product Line
    st.subheader("⭐ Average Ratings by Product Line")
    rating_avg = filtered_df.groupby("Product line")['Rating'].mean()
    st.bar_chart(rating_avg)

    # Raw Data
    with st.expander("🔎 View Raw Data"):
        st.dataframe(filtered_df)

else:
    st.info("👈 Please upload an Excel file to begin.")
