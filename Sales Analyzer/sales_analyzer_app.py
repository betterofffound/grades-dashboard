import pandas as pd
import streamlit as st
import plotly.express as px
px.defaults.template = "plotly_white"

st.set_page_config(page_title="Sales Analyzer", layout="wide")

st.title("Sales Dashboard")
uploaded_file = st.sidebar.file_uploader("Upload sales data", type=("xlsx"))

if uploaded_file is None:
    st.info("Upload sales data file to view the dashboard.")
    st.stop()
sales_data = pd.read_excel(uploaded_file)


#MISSING COLUMN VALIDATION BLOCK
required_columns = [
    "Order ID", "Order Date", "Order Month", "Customer ID", "Customer Name", "Customer Email", "Product Name",
    "Category","Unit Price","Discount Rate","Gross Sales","Discount Amount","Net Sales","Payment Method",
    "Sales Channel","Branch","Sales Rep"
]
missing_columns = [col for col in required_columns if col not in sales_data.columns]

if missing_columns:
    st.error(f"Missing required columns: {','.join(missing_columns)}")
    st.stop()

#NUMERIC COLUMN VALIDATION
numeric_columns = ["Unit Price","Discount Rate","Gross Sales","Discount Amount","Net Sales",]
for col in numeric_columns:
    sales_data[col] = pd.to_numeric(sales_data[col],errors="coerce")

sales_data = sales_data.dropna(subset=numeric_columns)

bad_rows = sales_data[sales_data[numeric_columns].isna().any(axis=1)]

if not bad_rows.empty:
    st.error("Some rows have missing or invalid numeric values.")
    st.dataframe(bad_rows[["Order ID"] + numeric_columns], width="stretch")
    st.stop()    

#DUPLICATE ORDER ID VALIDATION

st.sidebar.subheader("Data Quality")

duplicate_rows = sales_data[sales_data.duplicated(subset="Order ID", keep=False)]

if not duplicate_rows.empty:
    st.sidebar.warning(f"Found {len(duplicate_rows)} rows with duplicate Order ID values.")
    with st.expander("View Duplicate rows:"):
        st.dataframe(duplicate_rows, width="stretch")
else:
    st.sidebar.success("No duplicate order ID's found!")

#DATA GROUPING and CONVERSION

sales_data["Order Month"] = pd.to_datetime(sales_data["Order Date"]).dt.to_period("M").astype(str)
grouped_monthly_sales = sales_data.groupby("Order Month")
# monthly_sales = grouped_monthly_sales["Gross Sales"].sum()
# monthly_units_sold = grouped_monthly_sales["Quantity"].sum()

selected_month = st.sidebar.selectbox("Month",["All"]+sorted(sales_data["Order Month"].dropna().unique()))
selected_branch = st.sidebar.selectbox("Branch",["All"]+sorted(sales_data["Branch"].dropna().unique()))


filtered_data = sales_data

if selected_month != "All":
    filtered_data = filtered_data[filtered_data["Order Month"]==selected_month]

if  selected_branch !="All":
    filtered_data= filtered_data[filtered_data["Branch"] == selected_branch]

st.caption(f"Selected Filters: {selected_month} Months | {selected_branch} Branches")

monthly_gross_sales = filtered_data["Gross Sales"].sum().round(2)
formatted_gross_sales = f'{monthly_gross_sales:,.2f}'
monthly_units_sold = filtered_data["Quantity"].sum().round(2)
formatted_units_sold = f'{monthly_units_sold:,.2f}'
net_sales = filtered_data["Net Sales"].sum().round(2)
formatted_net_sales = f'{net_sales:,.2f}'
total_orders = filtered_data["Order ID"].count()
average_order_value = (net_sales/total_orders).round(2)
formatted_average_order_value = f'{average_order_value:,.2f}'

summary_tab, charts_tab, table_tab = st.tabs(["Summary", "Charts", "Sales Data Results"])
with summary_tab:
    st.subheader("Summary")
    st.caption("Overview based on the selected month and branch.")
    
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    
    row1_col1.metric("Total Gross sales",formatted_gross_sales)
    row1_col2.metric("Total Unit Sales",formatted_units_sold)
    row1_col3.metric("Total Net Sales",formatted_net_sales)
    
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    row2_col1.metric("Total Orders",total_orders)
    row2_col2.metric("Average Order Value",average_order_value)
st.divider()

#VISUALS
with charts_tab:
    st.markdown("##### Sales Trends & Distribution")
    st.caption("Charts based on the selected month and branch.")

    monthly_sales = filtered_data.groupby("Order Month")["Gross Sales"].sum().round(2).reset_index()
    monthly_sales["Order Month"] = monthly_sales["Order Month"].astype(str)
  

    fig_monthly_sales = px.bar(
        monthly_sales,
        x="Order Month",
        y="Gross Sales",
        title="Gross Monthly Sales",
        color_discrete_sequence=["#2563EB"]
    )

    fig_monthly_sales.update_layout(
        height=420,
        showlegend=False,
        yaxis_title="Sales",
        xaxis_title=None
    )
    fig_monthly_sales.update_xaxes(type="category")
    chart_col1, chart_col2 = st.columns(2)
    chart_col1.plotly_chart(fig_monthly_sales, width="stretch")

    units_sold = filtered_data.groupby("Branch")["Quantity"].sum().reset_index()
    fig_units_sold = px.pie(
        units_sold,
        names="Branch",
        values = "Quantity",
        title="Units Sold"
    )
    fig_units_sold.update_traces(
        textinfo="label+percent+value",
        textfont_color="white",
    )
    fig_units_sold.update_layout(
        height = 420,
        legend_title_text = "Result",
        legend_font_color = "black",
        title_font_color = "black"
    )
    chart_col2.plotly_chart(fig_units_sold,width="stretch")
    category_sales = filtered_data.groupby("Category")["Quantity"].sum().reset_index()
    fig_category_sales = px.bar(
        category_sales,
        x="Category",
        y="Quantity",
        text="Quantity",
        title="Product Category Sales"
    )
    fig_category_sales.update_traces(textposition="outside")
    fig_category_sales.update_layout(
        height=420,
        showlegend=False,
        yaxis_title="Sales",
        xaxis_title=None
    )
    fig_category_sales.update_traces(width=0.55)
    #  0.45 = thinner
    #  0.55 = balanced
    #  0.70 = wider
    fig_category_sales.update_xaxes(type="category")
    st.plotly_chart(fig_category_sales, width="stretch")

with table_tab:
    
    top_products_sales = filtered_data.groupby("Product Name")["Net Sales"].sum()
    top_products = top_products_sales.idxmax()
    top_products_sales_value = top_products_sales[top_products]
    top_customer_sales = filtered_data.groupby("Customer Name")["Net Sales"].sum()
    top_customer = top_customer_sales.idxmax()
    top_customer_sales_value = top_customer_sales[top_customer]
    top_agent_sales = filtered_data.groupby("Sales Rep")["Net Sales"].sum()
    top_agent = top_agent_sales.idxmax()
    top_agent_sales_value = top_agent_sales[top_agent]

    st.markdown("#### Highlights")
    st.caption("Filtered records based on the selected month and branch.")
    col1,col2,col3 = st.columns(3)
    col1.caption("Top Selling Product")
    col1.markdown(f"###### {top_products}")
    col1.caption(f"Total Net Sales: {top_products_sales_value:,.2f}")
    
    col2.caption("Top Customer")
    col2.markdown(f"###### {top_customer}")
    col2.caption(f"Total Net Sales: {top_customer_sales_value:,.2f}")


    col3.caption("Top Sales Representative")
    col3.markdown(f"###### {top_agent}")
    col3.caption(f"Total Net Sales: {top_agent_sales_value:,.2f}")    


    # st.markdown("#### Sales Data Results")
    # styled_table = (
    #     filtered_data
    #     .dropna(subset=["Order ID"])
    #     .reset_index(drop=True)
    # )
    # st.dataframe(styled_table, width="stretch")

    st.markdown("###### Filtered Sales Records")
    filtered_columns = [
            "Order ID",
            "Order Date",
            "Customer Name",
            "Product Name",
            "Category",
            "Quantity",
            "Net Sales",
            "Sales Rep"
    ]
    styled_table = (filtered_data[filtered_columns].dropna(subset=["Order ID"]).reset_index(drop=True)
    )
    styled_table["Order Date"] = styled_table["Order Date"].dt.strftime("%Y-%m-%d")
    styled_table["Net Sales"] = styled_table["Net Sales"].map("{:,.2f}".format)

    st.dataframe(styled_table, width="stretch")

    download_sales_data = styled_table

    csv = download_sales_data.to_csv(index=False)

    st.download_button(
    label="Download Sales Data Results",
    data=csv,
    file_name="sales_data_results.csv",
    mime="text/csv"
    )