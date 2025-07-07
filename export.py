import os
import pandas as pd
from sqlalchemy import create_engine

user = os.environ["PG_USER"]
password = os.environ["PG_PASSWORD"]
host = os.environ["PG_HOST"]
port = os.environ["PG_PORT"]
database = os.environ["PG_DATABASE"]

engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{database}")

df = pd.read_sql("SELECT * FROM editor02.combates_2024", con=engine)
df.to_csv("dados/combates_2024.csv", index=False)
