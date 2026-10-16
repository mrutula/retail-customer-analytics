import pandas as pd
from retail.snapshots import build_snapshot
import pytest

@pytest.fixture
def sample_purchase():
    purchases =  pd.DataFrame({
        "Invoice": ['11', '12', '13', '21', '21', '22', '23', '31', '31', '31'],
    	"StockCode": ['111', '112', '113', '111', '112', '113', '114', '115', '116', '117'],
        "Description": ['a', 'b', 'c', 'a', 'b', 'c', 'd', 'e', 'f', 'g']	,
        "Quantity": [1, 2, 3, 1, 2, 3, 1, 2, 3, 4],
        "InvoiceDate": ['2010-04-29 00:00:00','2010-01-29 00:00:00', '2010-07-01 00:00:00', 
                        '2010-01-01 00:00:00', '2010-03-29 00:00:00','2010-06-29 00:00:00', '2010-07-02 00:00:00',
                        '2010-04-29 00:00:00', '2010-03-29 00:00:00', '2010-05-29 00:00:00'
                        ],
        "Price": [1.0, 2.0, 3.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]	,
        "Customer ID": ['1', '1', '1', '2', '2', '2', '2', '3', '3', '3']	,
        "Country": ['United Kingdom', 'United Kingdom', 'France', 'France', 'United Kingdom', 'Spain', 'United Kingdom'
                    , 'France', 'Spain', 'Belgium'],
        "line_value": [1, 4, 9, 1, 4, 9, 16, 10, 18, 28]
    })

    purchases['InvoiceDate'] = pd.to_datetime(purchases['InvoiceDate'])
    purchases['Quantity'] = purchases['Quantity'].astype("int64")
    purchases['Price'] = purchases['Price'].astype("float64")
    
    return purchases

@pytest.fixture
def sample_return():
    return_df =  pd.DataFrame({
        "Invoice": ['15', '35'],
    	"StockCode": ['111', '112'],
        "Description": ['a', 'b']	,
        "Quantity": [-1, -2],
        "InvoiceDate": ['2010-04-29 00:00:00','2010-01-29 00:00:00'],
        "Price": [1.0, 2.0]	,
        "Customer ID": ['1', '3']	,
        "Country": ['United Kingdom', 'United Kingdom'],
        "line_value": [-1.0, -40.0]
    })
    return_df['InvoiceDate'] = pd.to_datetime(return_df['InvoiceDate'])
    return_df['Quantity'] = return_df['Quantity'].astype("int64")
    return_df['Price'] = return_df['Price'].astype("float64")
    
    return return_df


def test_transaction_on_cutoff_date_only_changes_label(sample_purchase, sample_return):
    snapshot = build_snapshot(sample_purchase, sample_return, cut_off='2010-07-01')

    expected_outcome = pd.DataFrame(
        {
            'Customer ID': ['1', '2', '3'],
            'product_breadth':  [2, 2, 3],
            'frequency_180d': [2, 2, 1],
            'monetary_180d': [5, 13, 56],
            'last_purchase_date' : ['2010-04-29', '2010-06-29', '2010-05-29'],
            'country_count_180d' : [1, 2, 3],
            'first_purchase_dt': ['2010-01-29', '2010-01-01', '2010-03-29'],
            'aov_180d': [2.5, 6.5, 56.0],
            'tenure_days': [153, 181, 94],
            'recency_days': [63, 2, 33],
            'uk_invoice_share_180d': [1.0, 0.5, 0.0],
            'monetary_last_90d': [1.0, 9.0, 38.0],
            'monetary_first_90d': [4.0, 4.0, 18.0],
            'spend_trend': [-3, 5, 20],
            'return_amount': [-1.0, 0.0, -40.0],
            'return_rate': [0.2, 0.0, 0.7142857142857143],
            'churned': [0, 0, 1],
            'snapshot_date' : ['2010-07-01', '2010-07-01', '2010-07-01']
        }
    )
    expected_outcome['last_purchase_date'] = pd.to_datetime(expected_outcome['last_purchase_date'], format='%Y-%m-%d')
    expected_outcome['first_purchase_dt'] = pd.to_datetime(expected_outcome['first_purchase_dt'], format='%Y-%m-%d')
    expected_outcome['snapshot_date'] = pd.to_datetime(expected_outcome['snapshot_date'], format='%Y-%m-%d')
    expected_outcome['monetary_last_90d'] = expected_outcome['monetary_last_90d'].astype("int64")
    expected_outcome['monetary_first_90d'] = expected_outcome['monetary_first_90d'].astype("int64")
    expected_outcome['recency_days'] = expected_outcome['recency_days'].astype("int64")
    pd.testing.assert_frame_equal(snapshot, expected_outcome)
              