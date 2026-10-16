# Load and combine the data and remove duplicate rows
import pandas as pd
from loguru import logger

def load_and_combine_data() -> None:
    """
    Load excel file, combine it and store as parquet
    
    Parameters:
        None
    Return:
        None
    """
    df = pd.DataFrame()
    # Load the excel file - all sheets
    df_dict = pd.read_excel("/Users/mrutulasuresh/Documents/GitHub/retail-customer-analytics/data/raw/online_retail_II.xlsx"
                            , sheet_name=None
                            , dtype={'Invoice': 'str', 
                                      'StockCode': 'str', 
                                      'Description': 'str', 
                                      'Quantity': 'int', 
                                      'InvoiceDate': 'datetime64[ns]', 
                                      'Price': 'float', 
                                      'Customer ID': 'str', 
                                      'Country': 'str'})

    for key, value in df_dict.items():
        logger.info(f"Sheet Name: {key} and rows: {value.shape[0]}")
        min_value, max_value = value['InvoiceDate'].min(), value['InvoiceDate'].max()
        logger.info(f"The Min and max date for {key} are {min_value} and {max_value}")
        df = pd.concat([df, value], ignore_index = True)

    del df_dict
    logger.info(f"Final number of rows in dataframe {df.shape[0]}")

    logger.info("drop any duplicate rows")

    df = df.drop_duplicates()

    logger.info(f"Rows in dataframe after duplicates removal: {df.shape[0]}")

    df.to_parquet("/Users/mrutulasuresh/Documents/GitHub/retail-customer-analytics/data/processed/online_retail.parquet"
                  , engine='pyarrow', index=False
                  , compression='snappy')

    logger.info(f"Parquet file successfully created")


if __name__ == '__main__':
    load_and_combine_data()