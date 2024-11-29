import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
from babel.numbers import format_currency

sns.set(style='dark')
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, 'main_data.csv')
dataset = pd.read_csv('dashboard/main_data.csv', parse_dates=['order_purchase_timestamp', 'order_delivered_customer_date', 'order_delivered_carrier_date', 'order_approved_at', 'order_estimated_delivery_date'])
dataset = pd.read_csv(data_path, parse_dates=['order_purchase_timestamp', 'order_delivered_customer_date', 'order_delivered_carrier_date', 'order_approved_at'])

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    
    return daily_orders_df

st.title('Olist E-commerce Dashboard')

min_date = dataset['order_purchase_timestamp'].min().date()
max_date = dataset['order_purchase_timestamp'].max().date()    

with st.sidebar:
    st.image("assets/logo.png")
    
    start_date, end_date = st.date_input(
        label='Date Range',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = dataset[(dataset["order_purchase_timestamp"] >= str(start_date)) & 
                (dataset["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)

st.sidebar.title('Navigation')

options = st.sidebar.radio('Select a section:', ['Overview', 'Transaction Details', 'Customer Segmentation', 'Delivery Analysis'])

if options == 'Overview':
  st.subheader('Daily Orders')

  col1, col2 = st.columns(2)

  with col1:
      total_orders = daily_orders_df.order_count.sum()
      st.metric("Total orders", value=total_orders)

  with col2:
      total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='pt_BR')
      st.metric("Total Revenue", value=total_revenue)
  
  # Filter the dataset based on the selected date range
  monthly_orders = main_df.resample('M', on='order_purchase_timestamp').size()

  # Visualization of the number of orders per month
  plt.figure(figsize=(8, 6))
  sns.lineplot(x=monthly_orders.index, y=monthly_orders.values, marker='o')
  plt.title('Orders per Month')
  plt.xlabel('Month')
  plt.ylabel('Number of Orders')
  plt.show()
  st.subheader('Monthly Orders Trend')
  st.line_chart(monthly_orders)
  
elif options == 'Transaction Details':
  st.subheader('Transactions by Hour')
  dataset['order_hour'] = dataset['order_purchase_timestamp'].dt.hour
  plt.figure(figsize=(12, 6))
  sns.countplot(data=dataset, x='order_hour', palette='viridis')
  plt.title('Number of Transactions by Hour')
  plt.xlabel('Hour of the Day')
  plt.ylabel('Number of Transactions')
  st.pyplot(plt)

  st.subheader('Transactions by Day of the Week')
  dataset['order_day_of_week'] = dataset['order_purchase_timestamp'].dt.day_name()
  plt.figure(figsize=(8, 6))
  sns.countplot(data=dataset, x='order_day_of_week', order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], palette='viridis')
  plt.title('Number of Transactions by Day of the Week')
  plt.xlabel('Day of the Week')
  plt.ylabel('Number of Transactions')
  st.pyplot(plt)
  
  st.subheader('Transactions by Hour and Day of the Week')
  # Create a pivot table for heatmap
  heatmap_data = dataset.pivot_table(index='order_day_of_week', columns='order_hour', values='order_id', aggfunc='count', fill_value=0)

  # Reorder the index to ensure the days of the week are in the correct order
  heatmap_data = heatmap_data.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

  # Plot the heatmap
  plt.figure(figsize=(24, 10))
  sns.heatmap(heatmap_data, cmap='viridis', linewidths=.5, annot=True, fmt='d')
  plt.title('Heatmap of Transactions by Hour and Day of the Week')
  plt.xlabel('Hour of the Day')
  plt.ylabel('Day of the Week')
  st.pyplot(plt)

elif options == 'Customer Segmentation':
  st.subheader('Customer Segmentation Details')

  rfm_df = dataset.groupby(by="customer_id", as_index=False).agg({
    "order_delivered_customer_date": "max",
    "order_id": "nunique",
    "payment_value": "sum"
  })
  rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
  current_date = pd.to_datetime('2023-12-17')
  rfm_df['recency'] = (current_date - rfm_df['max_order_timestamp']).dt.days
  rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
  rfm_df['r_rank'] = rfm_df['recency'].rank(ascending=False)
  rfm_df['f_rank'] = rfm_df['frequency'].rank(ascending=True)
  rfm_df['m_rank'] = rfm_df['monetary'].rank(ascending=True)
  rfm_df['r_rank_norm'] = (rfm_df['r_rank']/rfm_df['r_rank'].max())*100
  rfm_df['f_rank_norm'] = (rfm_df['f_rank']/rfm_df['f_rank'].max())*100
  rfm_df['m_rank_norm'] = (rfm_df['m_rank']/rfm_df['m_rank'].max())*100
  rfm_df.drop(columns=['r_rank', 'f_rank', 'm_rank'], inplace=True)
  rfm_df['RFM_score'] = 0.15*rfm_df['r_rank_norm']+0.28*rfm_df['f_rank_norm']+0.57*rfm_df['m_rank_norm']
  rfm_df['RFM_score'] *= 0.05
  rfm_df = rfm_df.round(2)
  rfm_df["customer_segment"] = np.where(
    rfm_df['RFM_score'] > 4.5, "Top customers", (np.where(
      rfm_df['RFM_score'] > 4, "High value customer",(np.where(
        rfm_df['RFM_score'] > 3, "Medium value customer", np.where(
          rfm_df['RFM_score'] > 1.6, 'Low value customers', 'Lost customers'))))))

  customer_segment_df = rfm_df.groupby(by="customer_segment", as_index=False).customer_id.nunique()
  customer_segment_df['customer_segment'] = pd.Categorical(customer_segment_df['customer_segment'], [
    "Lost customers", "Low value customers", "Medium value customer",
    "High value customer", "Top customers"
  ])

  plt.figure(figsize=(6, 4))
  sns.barplot(
    x="customer_id",
    y="customer_segment",
    data=customer_segment_df.sort_values(by="customer_segment", ascending=False),
    palette='viridis'
  )
  plt.title("Number of Customer for Each Segment", loc="center", fontsize=15)
  plt.ylabel(None)
  plt.xlabel(None)
  plt.tick_params(axis='y', labelsize=12)
  st.pyplot(plt)
  
  # Change the column name according to the dataset
  fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 10))

  # Visualization based on Recency
  sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), color='orange', ax=ax[0])
  ax[0].set_ylabel(None)
  ax[0].set_xlabel(None)
  ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
  ax[0].tick_params(axis ='x', labelsize=15)
  ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha='right')

  # Visualization based on Frequency
  sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), color='orange', ax=ax[1])
  ax[1].set_ylabel(None)
  ax[1].set_xlabel(None)
  ax[1].set_title("By Frequency", loc="center", fontsize=18)
  ax[1].tick_params(axis='x', labelsize=15)
  ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha='right')

  # Visualization based on Monetary
  sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), color='orange', ax=ax[2])
  ax[2].set_ylabel(None)
  ax[2].set_xlabel(None)
  ax[2].set_title("By Monetary", loc="center", fontsize=18)
  ax[2].tick_params(axis='x', labelsize=15)
  ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=45, ha='right')

  plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)
  plt.show()

  st.write("### Top 5 Customers by Recency")
  st.dataframe(rfm_df.sort_values(by="recency", ascending=True).head(5))

  st.write("### Top 5 Customers by Frequency")
  st.dataframe(rfm_df.sort_values(by="frequency", ascending=False).head(5))

  st.write("### Top 5 Customers by Monetary Value")
  st.dataframe(rfm_df.sort_values(by="monetary", ascending=False).head(5))

elif options == 'Delivery Analysis':
  st.subheader('Distribution of Delivery Time')
  dataset['delivery_time'] = (dataset['order_delivered_customer_date'] - dataset['order_delivered_carrier_date']).dt.days

  plt.figure(figsize=(8, 6))
  sns.histplot(dataset['delivery_time'], bins=30, kde=True, color='orange')
  plt.title('Distribution of Delivery Time')
  plt.xlabel('Delivery Time (days)')
  plt.ylabel('Frequency')
  st.pyplot(plt)

  st.subheader('Average Delivery Time by State')
  avg_delivery_time_by_seller_state = dataset.groupby('seller_state')['delivery_time'].mean().sort_values()
  plt.figure(figsize=(12, 6))
  sns.barplot(x=avg_delivery_time_by_seller_state.index, y=avg_delivery_time_by_seller_state.values, palette='viridis')
  plt.xticks(rotation=45, ha='right')
  plt.title('Average Delivery Time by Seller State')
  plt.xlabel('Seller State')
  plt.ylabel('Average Delivery Time (days)')
  st.pyplot(plt)
  