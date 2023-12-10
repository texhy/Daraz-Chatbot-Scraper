import pandas as pd
from sqlalchemy import create_engine

#code for changing the current csv into sql 
df = pd.read_csv('not_merged.csv')
engine = create_engine('mysql://root:123456@localhost/pai_project')
df.to_sql('not_merged_data', con=engine, index=False, if_exists='replace')


