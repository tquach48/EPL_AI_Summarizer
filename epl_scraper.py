from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

import json
import time
import random
import os


# -------------------------------------------------------------------
# HUMAN-LIKE WAITING
# -------------------------------------------------------------------
def human_delay(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))


# -------------------------------------------------------------------
# JSON WRITING: WRITE AFTER EVERY MATCH
# -------------------------------------------------------------------
def append_match_to_json(match_data, filename="premier_league_results.json"):
    """Append a single match to the JSON file, creating it if needed."""

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = []

    existing.append(match_data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)

    print(f"💾 Match written to {filename}")


# -------------------------------------------------------------------
# CLICK PREVIOUS MONTH
# -------------------------------------------------------------------
def click_previous_month(driver):
    try:
        prev_btn = WebDriverWait(driver, 7).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "div.match-list-header__button-container button[aria-label='Previous Month']")
            )
        )
        prev_btn.click()
        return True
    except:
        return False


# -------------------------------------------------------------------
# OPEN A TAB (Stats / Report / Commentary)
# -------------------------------------------------------------------
def open_tab(driver, tab_name):
    wait = WebDriverWait(driver, 12)
    try:
        tab_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, f"//button[normalize-space()='{tab_name}']")))

        tab_btn.click()
        return True
    except Exception as e:
        print(f"⚠ Could not open {tab_name}: {e}")
        return False


# -------------------------------------------------------------------
# SCRAPE MATCH STATS
# -------------------------------------------------------------------
def scrape_match_stats(driver):
    wait = WebDriverWait(driver, 12)
    stats_data = {}

    try:
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[data-testid='matchStatsContainer']")
        ))
    except:
        return stats_data

    containers = driver.find_elements(By.CSS_SELECTOR, "div[data-testid='matchStatsContainer']")

    for container in containers:
        try:
            title = container.find_element(By.CSS_SELECTOR, ".match-stats__title").text.strip()
        except:
            continue

        stats_data[title] = []
        rows = container.find_elements(By.CSS_SELECTOR, ".match-stats__table-row")

        for row in rows:
            try:
                stat_name = row.find_element(By.CSS_SELECTOR, ".match-stats__stat-name").text.strip()
            except:
                continue

            # Possession / Percentage stats
            try:
                home_val = row.find_element(By.CSS_SELECTOR, ".match-stats__stat-percentage--home").text.strip()
                away_val = row.find_element(By.CSS_SELECTOR, ".match-stats__stat-percentage--away").text.strip()
            except:
                # Normal stats
                try:
                    home_val = row.find_element(By.CSS_SELECTOR, ".match-stats__table-cell--home").text.strip()
                except:
                    home_val = None
                try:
                    away_val = row.find_element(By.CSS_SELECTOR, ".match-stats__table-cell--away").text.strip()
                except:
                    away_val = None

            stats_data[title].append({
                "stat": stat_name,
                "home": home_val,
                "away": away_val
            })

    return stats_data


# -------------------------------------------------------------------
# SCRAPE MATCH REPORT
# -------------------------------------------------------------------
def scrape_match_report(driver):
    wait = WebDriverWait(driver, 12)
    report_text = ""

    try:
        report_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[data-testid='matchReportInternal']")
        ))
        report_btn.click()

        full_report = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "article[data-testid='matchReportInternalFull'] .temp-article__content")
        ))

        paragraphs = full_report.find_elements(By.TAG_NAME, "p")
        report_text = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])

    except Exception as e:
        print("⚠ Could not scrape match report:", e)
        return None

    return report_text


# -------------------------------------------------------------------
# SCRAPE SINGLE MATCH
# -------------------------------------------------------------------
def scrape_match(driver):
    wait = WebDriverWait(driver, 15)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='scoreboardContainer']")))


    match_report = scrape_match_report(driver)

    driver.refresh()

    # TEAM NAMES
    teams = driver.find_elements(By.CSS_SELECTOR, "[data-testid='scoreboardHeaderTeam']")
    home_team = teams[0].find_element(By.CSS_SELECTOR, ".scoreboard-header__team-name").text.strip()
    away_team = teams[1].find_element(By.CSS_SELECTOR, ".scoreboard-header__team-name").text.strip()

    # SCORES
    home_score = driver.find_element(By.CSS_SELECTOR, ".match-status__score--home").text.strip()
    away_score = driver.find_element(By.CSS_SELECTOR, ".match-status__score--away").text.strip()

    # HALF-TIME SCORE
    try:
        ht_text = driver.find_element(By.CSS_SELECTOR, "[data-testid='matchStatusHalfTime']").text
        ht_numbers = ht_text.replace("HT", "").strip().split("-")
        ht_home, ht_away = ht_numbers[0].strip(), ht_numbers[1].strip()
    except:
        ht_home, ht_away = None, None

    # SCORERS
    scorers = []
    for team_label, team_name, selector in [
        ("home", home_team, "[data-testid='homeTeamGoals'] li"),
        ("away", away_team, "[data-testid='awayTeamGoals'] li")
    ]:
        for g in driver.find_elements(By.CSS_SELECTOR, selector):
            scorer = g.find_element(By.CSS_SELECTOR, "[data-testid='scoreboardEventScorer']").text.strip()
            minute = g.find_element(By.CSS_SELECTOR, "[data-testid='scoreboardEventScorer'] span").text.strip()
            scorers.append({
                "team": team_name,
                "player": scorer.replace(minute, "").strip(),
                "minute": minute
            })

    # CARDS
    cards = []
    for team_label, team_name, selector in [
        ("home", home_team, "[data-testid='homeTeamYellowCards'] li"),
        ("away", away_team, "[data-testid='awayTeamYellowCards'] li")
    ]:
        for c in driver.find_elements(By.CSS_SELECTOR, selector):
            cards.append({"team": team_name, "event": c.text.strip()})

    # STATS
    open_tab(driver, "Stats")
    match_stats = scrape_match_stats(driver)

    return {
        "home_team": home_team,
        "away_team": away_team,
        "final_score": {"home": home_score, "away": away_score},
        "half_time_score": {"home": ht_home, "away": ht_away},
        "scorers": scorers,
        "cards": cards,
        "stats": match_stats,
        "report": match_report
    }


# -------------------------------------------------------------------
# SCRAPE ALL MATCHES ACROSS MONTHS
# -------------------------------------------------------------------
def scrape_premier_league_matches():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    MAIN_URL = "https://www.premierleague.com/en/matches?competition=8&season=2025&matchweek=15&month=12&team=7%2C91%2C3%2C94%2C36%2C90%2C8%2C31%2C11%2C54%2C2%2C14%2C43%2C1%2C4%2C17%2C56%2C6%2C21%2C39"
    driver.get(MAIN_URL)

    human_delay(5, 8)

    # Accept cookies (if shown)
    try:
        cookie_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]")))
        cookie_btn.click()
        human_delay(2, 4)
    except:
        pass

    # close popups
    try:
        actions = ActionChains(driver)
        actions.move_by_offset(50, 300).click().perform()
        human_delay(1, 2)
        actions.move_by_offset(-50, -300)
    except:
        pass

    # Skip current month → go to previous
    if not click_previous_month(driver):
        print("No previous month found.")
        driver.quit()
        return
    time.sleep(5)
        # Skip current month → go to previous
    if not click_previous_month(driver):
        print("No previous month found.")
        driver.quit()
        return

    # Loop until no more months
    while True:
        human_delay(3, 5)

        match_list_root = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.match-list-root__content"))
        )

        driver.execute_script("arguments[0].scrollTop = 0;", match_list_root)
        human_delay(2, 4)

        match_cards = driver.find_elements(By.CSS_SELECTOR, "a[data-testid='matchCard']")
        print(f"📌 Found {len(match_cards)} matches")

        match_urls = [m.get_attribute("href") for m in match_cards]
        main_window = driver.current_window_handle

        # OPEN MATCH TABS
        for url in match_urls:
            driver.execute_script(f"window.open('{url}');")
            human_delay(3, 6)

        # SCRAPE EACH TAB
        for handle in driver.window_handles:
            if handle == main_window:
                continue

            driver.switch_to.window(handle)

            print("🔍 Scraping:", driver.current_url)

            try:
                match_data = scrape_match(driver)
                append_match_to_json(match_data)
            except Exception as e:
                print("⚠ Error scraping match:", e)

            driver.close()
            human_delay(2, 4)

        driver.switch_to.window(main_window)

        # NEXT MONTH (previous button)
        if not click_previous_month(driver):
            print("🏁 Finished scraping all months.")
            break

    driver.quit()


# -------------------------------------------------------------------
# RUN SCRIPT
# -------------------------------------------------------------------
if __name__ == "__main__":
    scrape_premier_league_matches()
