# retail-customer-analytics

# Definition 

- Customer is anyone who has made a valid transaction with us
- if a customer hasnt made a purchase in the 90 days after cut off date then considered as churned.
- 
#### To install the repo locally 
1) clone the repo
2) cd retail-customer-analytics
3) uv sync 
4) for jupyter notebook : 
   1) uv run python -m ipykernel install --user \
  --name retail-customer-analytics \
  --display-name "Python (retail-customer-analytics)"
5) uv run jupyter notebook

Data Cleansing 
--------------
The data source had 2 excel sheets, 
    > Year 2009-2010 and rows: 525461
    > Year 2010-2011 and rows: 541910
Combined rows: 1067371
After removing duplicate rows (overlapping dates and other indentical transactions): 1033036

The following cleansing down 

| Cleaning activity      |  Reason   |  Rows removed (%) | Rows remaining|
|------------------------|----------|----------------|--------------|
| Customers with NULL Id | Cant assign to customer| 23% | 797885 |                 
| Cancellation moved to another table | Its not a transaction used to calculate return rate| 2.3% | 779495
| Stock Analysis removal (notebook has the reasons) | Didnt represent actual transation | 0.003% | 776686
| Records with Price 0 | Not an actual transation | < 0.0001% | 776624 



