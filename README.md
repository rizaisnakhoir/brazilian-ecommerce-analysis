# Olist E-commerce Dashboard

This project is an interactive dashboard for visualizing and analyzing e-commerce data from Olist. The dashboard is built using Streamlit, Pandas, Matplotlib, and Seaborn.

## Project Structure

- **assets/**: Contains static assets like images.
- **dashboard/**: Contains the main dashboard application and data.
  - `dashboard.py`: The main script for the Streamlit dashboard.
  - `main_data.csv`: The main dataset used in the dashboard.
- **data/**: Contains various datasets used in the project.
  - `customers_dataset.csv`
  - `geolocation_dataset.csv`
  - `order_items_dataset.csv`
  - `order_payments_dataset.csv`
  - `order_reviews_dataset.csv`
  - `orders_dataset.csv`
  - `product_category_name_translation.csv`
  - `products_dataset.csv`
  - `sellers_dataset.csv`
- **notebook.ipynb**: Jupyter notebook for data analysis and exploration.
- **README.md**: Project documentation.
- **requirements.txt**: List of dependencies required for the project.
- **url.txt**: Contains the URL to the deployed Streamlit app.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/rizaisnakhoir/brazilian-ecommerce-analysis.git
    cd brazilian-ecommerce-analysis
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the Streamlit app:
    ```sh
    streamlit run dashboard/dashboard.py
    ```

2. Open your web browser and go to `http://localhost:8501` to view the dashboard.

## Features

### Transactions by Day of the Week

Displays the number of transactions for each day of the week.

### Transactions by Hour and Day of the Week

Displays a heatmap of transactions by hour and day of the week.

### Customer Segmentation

Provides details on customer segmentation based on recency, frequency, and monetary value.

### Delivery Analysis

Analyzes the distribution and average delivery time by state.

## Data
![data schema](https://i.imgur.com/HRhd2Y0.png)

The data used in this project is stored in the `data/` directory and includes the following files:
- `customers_dataset.csv`
- `geolocation_dataset.csv`
- `order_items_dataset.csv`
- `order_payments_dataset.csv`
- `order_reviews_dataset.csv`
- `orders_dataset.csv`
- `product_category_name_translation.csv`
- `products_dataset.csv`
- `sellers_dataset.csv`

The main dataset used for the dashboard is `dashboard/main_data.csv`.