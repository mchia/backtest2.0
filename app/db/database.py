import duckdb
import pandas as pd
from app.core.configs import DATABASE
from duckdb import DuckDBPyConnection

class DuckDBManager:
    def __init__(self, db_path: str = DATABASE):
        self.db_path: str = db_path
        self.schema: str = 'ohlcv'
        self.table: str = 'bars'
        self._initialize_schemas()

    def get_connection(self) -> DuckDBPyConnection:
        """Returns a new DuckDB connection."""
        return duckdb.connect(self.db_path)

    def _initialize_schemas(self) -> None:
        """
        Creates schemas if they don't exist.
        """
        with self.get_connection() as con:
            con.sql(f"CREATE SCHEMA IF NOT EXISTS {self.schema};")

    def _ingest_data(self, df: pd.DataFrame, interval: str) -> None:
        """
        Method to dynamically execute CREATE TABLE & INSERT OR REPLACE INTO from a DF, based on interval.

        Args:
            df: Dataframe to ingest.
            interval: Chosen interval.
        """
        tbl: str = f"{self.schema}.{self.table}_{interval}"
        with self.get_connection() as con:
            con.sql(f"""
                CREATE TABLE IF NOT EXISTS {tbl} (
                    timestamp TIMESTAMP,
                    symbol VARCHAR,
                    open DOUBLE,
                    high DOUBLE,
                    low DOUBLE,
                    close DOUBLE,
                    volume BIGINT,
                    PRIMARY KEY (symbol, timestamp)
                );
            """)
            con.sql(f"INSERT OR REPLACE INTO {tbl} SELECT * FROM df")

    def table_verification(self) -> list[str]:
        try:
            with self.get_connection() as con:
                query: str = f"""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = '{self.schema}'
                """
                result = con.execute(query=query).fetchall()
                return [row[0] for row in result]
        except (duckdb.Error, Exception) as e:
            print(e)
            return []

db_manager: DuckDBManager = DuckDBManager()