from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import sqlite3
import time
import random

# Konfiguracja przeglądarki
options = Options()
options.add_argument('--headless')
driver_path = 'C:/chromedriver/chromedriver-win64/chromedriver.exe'
driver = webdriver.Chrome(service=Service(driver_path), options=options)

# Połączenie z bazą danych SQLite
db = sqlite3.connect("premier_league_lineups_24_25.db")
cursor = db.cursor()

# Tworzenie tabeli na składy
cursor.execute('''
    CREATE TABLE IF NOT EXISTS match_lineups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id TEXT,
        home_team TEXT,
        away_team TEXT,
        home_lineup TEXT,
        away_lineup TEXT
    )
''')
db.commit()

# Otwórz stronę z wynikami Premier League
driver.get("https://www.flashscore.pl/pilka-nozna/anglia/premier-league/wyniki/")
time.sleep(2)

# Klikanie "Pokaż więcej meczów"
for _ in range(20):
    try:
        show_more = driver.find_element(By.CLASS_NAME, "event__more")
        if show_more.is_displayed():
            driver.execute_script("arguments[0].click();", show_more)
            time.sleep(1)
        else:
            break
    except:
        break

# Zbieranie linków do meczów
matches = driver.find_elements(By.CLASS_NAME, "event__match")
match_links = []
match_teams = []
for match in matches:
    try:
        home = match.find_element(By.CSS_SELECTOR, ".event__homeParticipant [data-testid='wcl-scores-simpleText-01']").text
        away = match.find_element(By.CSS_SELECTOR, ".event__awayParticipant [data-testid='wcl-scores-simpleText-01']").text
        link = match.find_element(By.CLASS_NAME, "eventRowLink").get_attribute("href")
        match_links.append(link)
        match_teams.append((home, away))
    except:
        continue

# Pobieranie składów i zapisywanie do bazy
for idx, link in enumerate(match_links):
    try:
        home_team, away_team = match_teams[idx]
        match_id = link.split("/")[-3]
        lineup_url = f"https://www.flashscore.pl/mecz/pilka-nozna/{match_id}/#/szczegoly-meczu/sklady"
        driver.get(lineup_url)
        time.sleep(random.uniform(2, 4))  # Losowe opóźnienie

        # Szukanie zawodników
        home_players = []
        away_players = []

        home_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='wcl-lineupsParticipantGeneral-left'] strong")
        for player in home_elements:
            name = player.text.strip()
            if name not in ['(B)', '(C)'] and name != '':
                home_players.append(name)

        away_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid='wcl-lineupsParticipantGeneral-right'] strong")
        for player in away_elements:
            name = player.text.strip()
            if name not in ['(B)', '(C)'] and name != '':
                away_players.append(name)

        # Ograniczenie do podstawowego składu (11 zawodników)
        home_starting_11 = home_players[:11]
        away_starting_11 = away_players[:11]

        # Zapisz do bazy danych
        cursor.execute('''
            INSERT INTO match_lineups (match_id, home_team, away_team, home_lineup, away_lineup)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            match_id,
            home_team,
            away_team,
            ', '.join(home_starting_11),
            ', '.join(away_starting_11)
        ))
        db.commit()

        print(f"✅ Zapisano skład meczu {home_team} vs {away_team}")

    except Exception as e:
        print(f"❌ Błąd przy meczu {link}: {e}")
        continue

# Zakończenie
driver.quit()
db.close()
