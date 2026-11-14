import duckdb
import vectorbt as vbt


DATABASE = 'market_data.duckdb'
x = duckdb.connect(DATABASE)
print(x.sql("SELECT table_name FROM information_schema.tables WHERE table_schema = {self.schema}"))