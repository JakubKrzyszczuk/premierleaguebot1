from __future__ import annotations
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def _accept_consent(driver) -> None:
    """
    Zamyka baner Google Funding Choices / CMP:
    - szuka <button class="fc-primary-button"> ... 'I accept' / 'Akceptuję'
    - przeszukuje *wszystkie* iframy, bo FC wstrzykuje dialog w iframe.
    """

    def _click_if_present(scope):
        try:
            btn = scope.find_element(
                By.CSS_SELECTOR,
                "button.fc-primary-button, "
                "button[aria-label*='Accept'], button[aria-label*='Akcept']"
            )
            driver.execute_script("arguments[0].click();", btn)
            return True
        except NoSuchElementException:
            return False

    # 1️⃣ spróbuj bez przełączania ramek
    if _click_if_present(driver):
        return

    # 2️⃣ sprawdź wszystkie iframe’y
    for fr in driver.find_elements(By.CSS_SELECTOR, "iframe"):
        driver.switch_to.frame(fr)
        if _click_if_present(driver):
            driver.switch_to.default_content()
            break
        driver.switch_to.default_content()

    # 3️⃣ poczekaj, aż dialog zniknie (jeśli klikło)
    WebDriverWait(driver, 1).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, ".fc-dialog-headline, .fc-dialog-container"))
    )


def _open_squad_tab(driver) -> None:
    """Kliknij zakładkę Skład/Squad/Players – javascriptem (omija przesłanianie)."""
    try:
        tab = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(.,'Skład') or contains(.,'Squad') or contains(.,'Players')]"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});"
                              "arguments[0].click();", tab)
    except TimeoutException:
        pass  # już jesteśmy w Skład


def get_players_info(team_slug: str, team_id: str | int,
                     *, headless: bool = True, echo: bool = True) -> list[str]:
    url = f"https://www.sofascore.com/pl/druzyna/pilka-nozna/{team_slug}/{team_id}"

    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    with webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                          options=opts) as dr:
        dr.get(url)

        _accept_consent(dr)       # ⬅️  NOWE, pewne zamknięcie pop-upu
        _open_squad_tab(dr)

        WebDriverWait(dr, 15).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                'a[href^="/pl/zawodnik/"], a[href^="/player/"]'
            ))
        )

        soup = BeautifulSoup(dr.page_source, "html.parser")
        anchors = soup.select('a[href^="/pl/zawodnik/"], a[href^="/player/"]')
        links = sorted({"https://www.sofascore.com" + a["href"] for a in anchors})

    if echo:
        for l in links:
            print(l)

    return links


# ----------------------- demo -----------------------
if __name__ == "__main__":
    get_players_info("liverpool", 44)
    get_players_info("arsenal", 42)
    get_players_info("newcastle-united", 39)
    get_players_info("manchester-city", 17)
    get_players_info("chelsea", 38)
    get_players_info("nottingham-forest", 14)
    get_players_info("aston-villa", 40)
    get_players_info("fulham", 43)
    get_players_info("brighton-and-hove-albion", 30)
    get_players_info("bournemouth", 60)
    get_players_info("brentford", 50)
    get_players_info("crystal-palace", 7)
    get_players_info("wolverhampton", 3)
    get_players_info("manchester-united", 35)
    get_players_info("everton", 48)
    get_players_info("tottenham-hotspur", 33)
    get_players_info("west-ham-united", 37)
    get_players_info("ipswich-town", 32)
    get_players_info("leicester-city", 31)#
    get_players_info("southampton", 45)

