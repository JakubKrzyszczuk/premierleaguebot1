import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Funkcja do wczytania danych z bazy SQLite
def load_sqlite_db(db_path, query):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Ścieżka do połączonej bazy danych
db_path = "/scrapping/all_seasons_merged.db"

# Wczytanie danych z bazy danych
query = "SELECT * FROM all_seasons_data"
all_data = load_sqlite_db(db_path, query)

# Wybieramy tylko kolumny numeryczne
numerical_data = all_data.select_dtypes(include=['float64', 'int64'])

# Sprawdzanie korelacji między cechami numerycznymi
correlation_matrix = numerical_data.corr()

# Wizualizacja korelacji
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Macierz korelacji dla danych meczów')
plt.show()


# Usuwanie symboli procentowych i konwersja na liczby
all_data['possession_home'] = all_data['possession_home'].str.replace('%', '').astype(float)
all_data['possession_away'] = all_data['possession_away'].str.replace('%', '').astype(float)

# Tworzymy nowe cechy na podstawie różnic w statystykach
all_data['xG_difference'] = all_data['xg_home'] - all_data['xg_away']
all_data['shots_difference'] = all_data['total_shots_home'] - all_data['total_shots_away']
all_data['possession_difference'] = all_data['possession_home'] - all_data['possession_away']
all_data['corners_difference'] = all_data['corners_home'] - all_data['corners_away']
all_data['yellow_cards_difference'] = all_data['yellow_cards_home'] - all_data['yellow_cards_away']

# Zmieniamy id na unikalne dla wszystkich danych (opcjonalnie, jeśli chcesz uniknąć powtarzających się id)
all_data['id'] = range(1, len(all_data) + 1)

# Sprawdzamy pierwsze wiersze po dodaniu nowych cech
print(all_data[['xG_difference', 'shots_difference', 'possession_difference', 'corners_difference', 'yellow_cards_difference']].head())

