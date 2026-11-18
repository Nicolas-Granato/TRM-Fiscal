from typing import Any, Optional, Sequence
import duckdb

from backend.src.database.scripts.setup_database_query import SETUP_DATABASE


class DuckDBSession:
    def __init__(self):
        self._conn: Optional[duckdb.DuckDBPyConnection] = None

    def _close_connection(self) -> None:
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            finally:
                self._conn = None

    def _setup_database(self) -> None:
        try:
            self._conn = duckdb.connect(":memory:")
            self._conn.execute(SETUP_DATABASE)
        except (duckdb.ParserException, duckdb.Error) as e:
            self._close_connection()
            raise RuntimeError(f"Erro ao carregar o schema do banco de dados: {e}") from e
        except Exception as e:
            self._close_connection()
            raise RuntimeError(f"Erro ao inicializar o banco de dados: {e}") from e

    def execute_sql(self, sql: str, parameters: Optional[Sequence[Any]] = None) -> list[tuple]:
        if not self._conn:
            raise RuntimeError("Conexão com o DuckDB não está ativa.")
        try:
            cursor = self._conn.execute(sql, parameters) if parameters is not None else self._conn.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            self._close_connection()
            raise RuntimeError(f"Erro ao executar a query no banco de dados: {e}") from e

    def executemany_sql(self, sql: str, parameters: list[tuple]) -> None:
        if not self._conn:
            raise RuntimeError("Conexão com o DuckDB não está ativa.")
        try:
            self._conn.executemany(sql, parameters)
        except Exception as e:
            self._close_connection()
            raise RuntimeError(f"Erro ao executar as queries no banco de dados: {e}") from e

    def __enter__(self) -> "DuckDBSession":
        self._setup_database()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._close_connection()