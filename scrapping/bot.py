import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import StandardScaler

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

# Usuwamy symbole procentowe i konwertujemy na liczby (np. posession)
all_data['possession_home'] = all_data['possession_home'].str.replace('%', '').astype(float)
all_data['possession_away'] = all_data['possession_away'].str.replace('%', '').astype(float)

# Tworzymy nowe cechy na podstawie różnic w statystykach
all_data['xG_difference'] = all_data['xg_home'] - all_data['xg_away']
all_data['shots_difference'] = all_data['total_shots_home'] - all_data['total_shots_away']
all_data['possession_difference'] = all_data['possession_home'] - all_data['possession_away']
all_data['corners_difference'] = all_data['corners_home'] - all_data['corners_away']
all_data['yellow_cards_difference'] = all_data['yellow_cards_home'] - all_data['yellow_cards_away']

# Przygotowanie etykiety (target) - wygrana, remis, porażka
target = (all_data['home_score'] - all_data['away_score']).apply(lambda x: 1 if x > 0 else (0 if x == 0 else -1))

# Wybieramy cechy (features)
features = all_data[['xG_difference', 'shots_difference', 'possession_difference', 'corners_difference', 'yellow_cards_difference']]

# Standaryzacja cech (opcjonalnie, ale zalecane dla regresji logistycznej)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Podział na zbiór treningowy i testowy (80% trening, 20% test)
X_train, X_test, y_train, y_test = train_test_split(features_scaled, target, test_size=0.2, random_state=42)

# Tworzymy model regresji logistycznej
model = LogisticRegression(max_iter=2000)

# Trening modelu
model.fit(X_train, y_train)

# Predykcja na zbiorze testowym
y_pred = model.predict(X_test)

# Ocena modelu
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)
class_report = classification_report(y_test, y_pred)

# Wyświetlamy wyniki
print("Dokładność modelu:", accuracy)
print("Macierz pomyłek:\n", conf_matrix)
print("Raport klasyfikacji:\n", class_report)

from sklearn.ensemble import RandomForestClassifier

# Tworzymy model Random Forest
model_rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')

# Trening modelu
model_rf.fit(X_train, y_train)

# Predykcja na zbiorze testowym
y_pred_rf = model_rf.predict(X_test)

# Ocena modelu
accuracy_rf = accuracy_score(y_test, y_pred_rf)
conf_matrix_rf = confusion_matrix(y_test, y_pred_rf)
class_report_rf = classification_report(y_test, y_pred_rf)

# Wyświetlamy wyniki
print("Dokładność modelu Random Forest:", accuracy_rf)
print("Macierz pomyłek:\n", conf_matrix_rf)
print("Raport klasyfikacji:\n", class_report_rf)
