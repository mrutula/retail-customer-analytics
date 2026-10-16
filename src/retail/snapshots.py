import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
import numpy as np

def build_snapshot(purchases: pd.DataFrame, returns: pd.DataFrame, cut_off: str) -> pd.DataFrame:
    """
    Create customer snapshot based on cut off date. Features from 180 days before cut-off date and churn result is between cut off date and cut off + 90 days

    Parameters:
        purchases: pd.DataFrame
            DataFrame containing all transactions (purchases)
        returns: pd.DataFrame
            DataFrame containing returns 
        cut_off: str
            Cut off date

    Returns:
        pd.DataFrame
    """
    if not isinstance(cut_off, str):
        logger.error("Cut off date is not a string")
        return pd.DataFrame()
    try: 
        cut_off_dt = datetime.strptime(cut_off, '%Y-%m-%d')
    except ValueError:
        raise ValueError(
            f"Invalid cut-off date string '{cut_off}'. "
            f"The date must be a valid date in 'YYYY-MM-DD' format."
        )

    # 180 DAYS before (exc cut off date)
    observation_df = purchases[(purchases['InvoiceDate'] < cut_off_dt)&(purchases['InvoiceDate'] >= cut_off_dt - timedelta(days=180))]

    #90 days after (from cut off date)
    outcome_df = purchases[(purchases['InvoiceDate'] >= cut_off_dt)&(purchases['InvoiceDate'] < cut_off_dt + timedelta(days=90))]

    # Customer first purchase date (before cut off)
    cus_frst_purchase_df = purchases[purchases['InvoiceDate']< cut_off_dt].groupby('Customer ID').agg(
                first_purchase_dt = ('InvoiceDate', 'min')
                ).reset_index()

    # UK share
    invoice_df = observation_df[['Customer ID', 'Invoice', 'Country']].drop_duplicates(subset=['Invoice']).copy()

    invoice_df['is_uk'] = (
        invoice_df['Country'] == 'United Kingdom'
    )
    uk_share_df =  invoice_df.groupby('Customer ID').agg(
        total_invoice=('Invoice', 'nunique'),
        uk_invoice=('is_uk', 'sum')
    ).reset_index()
    
    uk_share_df['uk_invoice_share_180d'] = uk_share_df['uk_invoice']/ uk_share_df['total_invoice']
    uk_share_df = uk_share_df[['Customer ID', 'uk_invoice_share_180d']]

    cust_ob_df = observation_df.groupby('Customer ID').agg(
        product_breadth = ("StockCode", "nunique"),
        frequency_180d = ("Invoice", "nunique"),
        monetary_180d = ("line_value", "sum"),
        last_purchase_date = ("InvoiceDate", 'max'),
        country_count_180d = ("Country", "nunique")
    ).reset_index()

    # Check for invalid monetary_180d valuesß
    invalid_spend = (cust_ob_df['monetary_180d'].isna() | (cust_ob_df['monetary_180d'] <= 0))
    if invalid_spend.any():
        raise ValueError(
            f"Found {invalid_spend.sum()} customers "
            "with missing or non-positive monetary_180d"
        )

    customer_transaction_df = pd.merge(cust_ob_df, cus_frst_purchase_df, on = 'Customer ID', how='left')
    customer_transaction_df['aov_180d'] = customer_transaction_df['monetary_180d']/customer_transaction_df['frequency_180d']
    customer_transaction_df['tenure_days'] = (cut_off_dt - customer_transaction_df['first_purchase_dt']).dt.days
    customer_transaction_df['recency_days'] = (cut_off_dt - customer_transaction_df['last_purchase_date']).dt.days


    customer_transaction_df = pd.merge(customer_transaction_df, uk_share_df, on = 'Customer ID', how = 'left')

    # spend trend 
    last_90d_trans = observation_df[(observation_df['InvoiceDate'] < cut_off_dt)&(observation_df['InvoiceDate'] >= cut_off_dt - timedelta(days=90))]
    first_90d_trans = observation_df[(observation_df['InvoiceDate'] < cut_off_dt - timedelta(days=90))&(observation_df['InvoiceDate'] >= cut_off_dt - timedelta(days=180))]

    cust_last_90d_trans = last_90d_trans.groupby('Customer ID').agg(monetary_last_90d = ('line_value', 'sum')).reset_index()
    cust_frst_90d_trans = first_90d_trans.groupby('Customer ID').agg(monetary_first_90d = ('line_value', 'sum')).reset_index()

    customer_transaction_df = pd.merge(customer_transaction_df, cust_last_90d_trans, on = 'Customer ID', how='left')
    customer_transaction_df = pd.merge(customer_transaction_df, cust_frst_90d_trans, on = 'Customer ID', how='left')

    colm_list = ['uk_invoice_share_180d', 'monetary_last_90d' , 'monetary_first_90d']
    customer_transaction_df[colm_list] = customer_transaction_df[colm_list].fillna(0)

    customer_transaction_df['spend_trend'] = customer_transaction_df['monetary_last_90d'] - customer_transaction_df['monetary_first_90d']

    # return rate
    returns_180d = returns[(returns['InvoiceDate'] < cut_off_dt)&(returns['InvoiceDate'] >= cut_off_dt - timedelta(days=180))]
    returns_amount_df = returns_180d.groupby('Customer ID').agg(return_amount = ('line_value', sum)).reset_index()

    customer_transaction_df = pd.merge(customer_transaction_df, returns_amount_df, on = 'Customer ID', how='left').fillna(0)

    customer_transaction_df['return_rate'] = customer_transaction_df['return_amount'].abs()/customer_transaction_df['monetary_180d']

    # outcome
    outcome_cust_df = outcome_df.groupby('Customer ID').agg(future_transaction_lines = ('Invoice', 'size')).reset_index()

    final_df = pd.merge(customer_transaction_df, outcome_cust_df, on = 'Customer ID', how= 'left')

    final_df['churned'] = np.where(final_df['future_transaction_lines'] > 0, 0 , 1)

    final_df['snapshot_date'] = cut_off_dt

    final_df = final_df.drop(columns=['future_transaction_lines', 'first_purchase_dt', 'last_purchase_date'])

    return final_df
