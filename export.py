from sqlalchemy import create_engine
import pandas as pd

secrets = st.secrets["postgres"]
engine = create_engine(
    f"postgresql://{secrets.user}:{secrets.password}@{secrets.host}:{secrets.port}/{secrets.database}"
)

df = pd.read_sql("SELECT * FROM editor02.combates_2024", engine)
df.to_csv("dados/combates_2024.csv", index=False)