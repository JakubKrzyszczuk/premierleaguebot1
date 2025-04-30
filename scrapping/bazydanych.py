import sqlite3
import pandas as pd

# Funkcja do wczytania danych z bazy SQLite
def load_sqlite_db(db_path, query):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Funkcja do zapisu DataFrame do nowej bazy SQLite
def save_to_sqlite(df, db_path, table_name):
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists='replace', index=False)  # 'replace' zamieni tabelę, jeśli już istnieje
    conn.close()

# Ścieżki do baz danych dla trzech sezonów
db_paths = [
    "C:/Users/Adam/Desktop/PythonProject/.venv/scrapping/merged_2022_2023.db",
    "C:/Users/Adam/Desktop/PythonProject/.venv/scrapping/merged_2023_2024.db",
    "C:/Users/Adam/Desktop/PythonProject/.venv/scrapping/merged_2024_2025.db"
]

# Ładowanie danych z każdej bazy
merged_2022_2023 = load_sqlite_db(db_paths[0], "SELECT * FROM merged_data_2022_2023")
merged_2023_2024 = load_sqlite_db(db_paths[1], "SELECT * FROM merged_data_2023_2024")
merged_2024_2025 = load_sqlite_db(db_paths[2], "SELECT * FROM merged_data_2024_2025")

# Łączenie danych z wszystkich sezonów
all_data = pd.concat([merged_2022_2023, merged_2023_2024, merged_2024_2025], ignore_index=True)

# Zapisz połączone dane do nowej bazy SQLite
all_data_db_path = "/scrapping/all_seasons_merged.db"
save_to_sqlite(all_data, all_data_db_path, "all_seasons_data")

# Sprawdzamy pierwsze wiersze połączonych danych
print(all_data.head())
