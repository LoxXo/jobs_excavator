import time
import configparser

import selenium.common.exceptions as Selenium_Exceptions
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class WrongFormException(Exception):
    """Raises if webdriver steps into unknown form page."""


def load_page(driver: webdriver, offer_id: str, job_name: str, link: str) -> list:
    wanted_city = ["Remote", "Katowice"]
    driver.get(link)

    # add cookie for nfj to prevent cookie info popup and clear any localstorage data
    driver.add_cookie(
        {"name": "OptanonAlertBoxClosed", "value": "2022-11-24T13:42:59.701Z"}
    )
    driver.execute_script("window.localStorage.clear()")

    time.sleep(2)
    WebDriverWait(driver, timeout=5).until(
        EC.element_to_be_clickable((By.ID, "applyButton"))
    )
    apply_button = driver.find_element(By.ID, "applyButton")
    apply_button.click()

    try:
        if len(driver.window_handles) > 1:
            print("closing new tab")
            driver.switch_to.window((driver.window_handles[1]))
            driver.close()
            driver.switch_to.window((driver.window_handles[0]))
            raise WrongFormException
    except WrongFormException:
        # temporary writes fails to .txt file
        print(f"WrongForm for {offer_id}")
        with open("failed_dump.txt", "a", encoding="utf-8") as fail:
            fail.write(
                f"Not on NFJ built-in apply page - skipping offer: {offer_id}, {job_name}, {link}\n"
            )
        return None

    # try as on stock nfj apply page and if not dump report to .txt
    try:
        WebDriverWait(driver, timeout=5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "h2.tw-text-center"))
        )

        # add full name
        name_field = driver.find_element(By.XPATH, "//input[@formcontrolname='name']")
        name_field.send_keys("Name and surname")

        # add email
        email_field = driver.find_element(By.XPATH, "//input[@type='email']")
        email_field.send_keys("email tutaj")

        # choose desired location
        location_span = driver.find_element(By.CSS_SELECTOR, ".dropdown-btn")
        location_span.click()
        scroll = driver.find_elements(
            By.XPATH, ("//li[@class='multiselect-item-checkbox ng-star-inserted']")
        )
        for e in scroll:
            if e.text in wanted_city:
                e.click()
        location_span.click()

        # upload cv
        cv_upload = driver.find_element(By.XPATH, "//*[@id='attachment']")
        cv_upload.send_keys("D:\\text.pdf")

        # add linkedin info in popup
        add_linkedin = driver.find_element(
            By.CSS_SELECTOR,
            "nfj-apply-optional.tw-my-2\.5:nth-child(7) > div:nth-child(1)",
        )
        add_linkedin.click()
        add_linkedin_url = driver.find_element(
            By.CSS_SELECTOR, "input.ng-pristine:nth-child(1)"
        )
        add_linkedin_url.send_keys("https://www.linkedin.com/in/john-doe/")
        driver.find_element(By.CSS_SELECTOR, "button.nfj-btn:nth-child(2)").click()

        # add github info in popup
        add_github = driver.find_element(
            By.CSS_SELECTOR,
            "nfj-apply-optional.tw-my-2\.5:nth-child(8) > div:nth-child(1)",
        )
        add_github.click()
        add_github_url = driver.find_element(
            By.CSS_SELECTOR, "input.ng-pristine:nth-child(1)"
        )
        add_github_url.send_keys("https://github.com/xX_www_Xx")
        driver.find_element(By.CSS_SELECTOR, "button.nfj-btn:nth-child(2)").click()

        # try to click consents
        try:
            driver.find_element(By.CSS_SELECTOR, "#currentConsent").click()
            driver.find_element(By.CSS_SELECTOR, "#futureConsent").click()
        except:
            pass

        # make screenshot before applying
        driver.save_screenshot(f"./screenshots_sent/{offer_id}.png")

        # click apply button
        driver.find_element(By.CSS_SELECTOR, ".btn-apply").click()

        print(f"Successfully sent CV to offer ID: {offer_id} {job_name}")
        return offer_id

    except Selenium_Exceptions.TimeoutException as te:
        print(f"Timeout during webdriver work ID: {offer_id}")
        return None
    except:
        print("Some kind of error when completing recruitment form.")
        return None


def run_sender(offers: list) -> list:
    """Start webdriver and calls load_page() for every value in given list to
    check offer's link and try to apply.
    Returns offer_id of successfully applied job"""
    driver = webdriver.Firefox()
    sent_cv = []

    # index 1 is id, index 2 is job_name and index 10 is link
    for offer in offers:
        cv = load_page(driver, offer[1], offer[2], offer[10])
        if cv is not None:
            sent_cv.append(cv)
        time.sleep(3)

    driver.close()

    return sent_cv
