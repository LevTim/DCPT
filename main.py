import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException


def get_average_price(driver, selector):
    # Чекаємо, поки елементи з'являться на сторінці
    elements = WebDriverWait(driver, 15).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
    )

    prices = []
    for elem in elements:
        text = elem.text
        # У Фокстроті ціни зазвичай виглядають як "25 999 ₴"
        # Витягуємо тільки цифри
        clean_text = re.sub(r'\D', '', text)

        if clean_text:
            prices.append(float(clean_text))

    if not prices:
        return 0.0

    average = sum(prices) / len(prices)
    return round(average, 2)


def main():
    # Налаштування опцій для безголового режиму
    chrome_options = Options()
    chrome_options.add_argument("--headless=new") # headless режим
    chrome_options.add_argument("--window-size=1920,1080") # Задаємо розмір екрану
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36") # Підміна User-Agent

    service = Service(ChromeDriverManager().install())
    # Передаємо створені опції у драйвер
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # СЕЛЕКТОРИ
    PRICE_SELECTOR = ".price--current"
    SORT_DROPDOWN_SELECTOR = ".selected-sort"
    SORT_OPTION_XPATH = "//*[contains(text(), 'від дешевих до дорогих')]"

    try:
        # 1. Відкриваємо сайт
        print("Запускаємо браузер у фоновому режимі (Headless)...")
        driver.get("https://www.foxtrot.com.ua/uk/shop/noutbuki.html")

        # 1.5. Закриваємо попапи (cookie або вибір міста), якщо вони є
        try:
            close_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".button-accept-cookies, .city-modal__close"))
            )
            close_btn.click()
            print("Закрили спливаюче вікно.")
        except TimeoutException:
            pass  # Якщо вікна немає - йдемо далі

        # 2. Збираємо середню ціну ДО сортування
        print("Збираємо дані ДО сортування...")
        avg_price_before = get_average_price(driver, PRICE_SELECTOR)
        print(f"Середня ціна до сортування: {avg_price_before} ₴")

        # Занотовуємо перший товар, щоб перевірити, коли оновиться сторінка
        first_product_before = driver.find_element(By.CSS_SELECTOR, PRICE_SELECTOR)

        # 3. Застосовуємо сортування
        print("Відкриваємо меню сортування...")
        dropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, SORT_DROPDOWN_SELECTOR))
        )
        driver.execute_script("arguments[0].click();", dropdown)

        print("Обираємо 'Від дешевих до дорогих'...")
        option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, SORT_OPTION_XPATH))
        )
        driver.execute_script("arguments[0].click();", option)

        # 4. Очікування оновлення сторінки (КРИТИЧНИЙ КРОК)
        print("Чекаємо оновлення списку товарів...")
        WebDriverWait(driver, 15).until(
            EC.staleness_of(first_product_before)
        )
        time.sleep(1)

        # 5. Збираємо середню ціну ПІСЛЯ сортування
        print("Збираємо дані ПІСЛЯ сортування...")
        avg_price_after = get_average_price(driver, PRICE_SELECTOR)
        print(f"Середня ціна після сортування: {avg_price_after} ₴")

        # 6. Порівнюємо результати
        print("-" * 30)
        print("РЕЗУЛЬТАТИ:")
        if avg_price_before == avg_price_after:
            print("Середня ціна на сторінці не змінилася.")
        else:
            print(f"Середня ціна змінилася з {avg_price_before} ₴ на {avg_price_after} ₴.")
            diff = abs(avg_price_before - avg_price_after)
            print(f"Різниця: {round(diff, 2)} ₴")

    except Exception as e:
        print(f"Сталася помилка: {e}")

    finally:
        driver.quit()
        print("Браузер закрито.")


if __name__ == "__main__":
    main()