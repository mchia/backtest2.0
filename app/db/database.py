import duckdb
import pandas as pd
from app.core.configs import DATABASE
from duckdb import DuckDBPyConnection

class DuckDBManager:
    def __init__(self, db_path: str = DATABASE):
        self.db_path: str = db_path
        self._initialize_storage()

    def get_connection(self) -> DuckDBPyConnection:
        """Returns a new DuckDB connection."""
        return duckdb.connect(self.db_path)

    def _initialize_storage(self) -> None:
        """Creates schemas and tables if they don't exist yet with correct types."""
        with self.get_connection() as con:
            con.sql("CREATE SCHEMA IF NOT EXISTS market_data.market;")
            con.sql("""
                        CREATE TABLE IF NOT EXISTS market_data.market.historical_prices (
                            timestamp TIMESTAMP,
                            symbol VARCHAR,
                            interval VARCHAR,
                            open DOUBLE,
                            high DOUBLE,
                            low DOUBLE,
                            close DOUBLE,
                            volume BIGINT,
                            PRIMARY KEY (symbol, timestamp, interval)
                        );
                    """)

    def _ingest_data(self, df: pd.DataFrame) -> None:
        """
        Method to INSERT OR REPLACE INTO from a DF.

        Args:
            df: Dataframe to ingest.
        """
        with self.get_connection() as con:
            con.sql(f"INSERT OR REPLACE INTO market_data.market.historical_prices SELECT * FROM df")

    def run(self) -> None:
        self.get_connection()
        self._initialize_storage()

db_manager: DuckDBManager = DuckDBManager()