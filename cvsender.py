from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


def load_page(driver: webdriver, offer_id: str, job_name: str, link: str) -> list:
    wanted_city = ["Remote", "Katowice"]
    driver.get(link)
    assert job_name in driver.title
    apply_button = driver.find_element(By.ID, "applyButton")
    apply_button.click()

    # check if on stock nfj apply page
    try:
        apply_text = driver.find_element(By.CSS_SELECTOR, "h2.tw-text-center").text
        if not apply_text == "Apply for the job":
            raise

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
        cv_upload.send_keys("D:\\text.txt")

        # add linkedin info
        add_linkedin = driver.find_element(
            By.CSS_SELECTOR,
            "nfj-apply-optional.tw-my-2\.5:nth-child(7) > div:nth-child(1)",
        )
        add_linkedin.click()
        add_linkedin_url = driver.find_element(
            By.CSS_SELECTOR, "input.ng-pristine:nth-child(1)"
        )
        add_linkedin_url.send_keys("LINK DO LINKEDIN")
        driver.find_element(By.CSS_SELECTOR, "button.nfj-btn:nth-child(2)").click()

        # add github info
        add_github = driver.find_element(
            By.CSS_SELECTOR,
            "nfj-apply-optional.tw-my-2\.5:nth-child(8) > div:nth-child(1)",
        )
        add_github.click()
        add_github_url = driver.find_elements(
            By.CSS_SELECTOR, "input.ng-pristine:nth-child(1)"
        )
        add_github_url.send_keys("LINK DO GITHUB")
        driver.find_element(By.CSS_SELECTOR, "button.nfj-btn:nth-child(2)").click()

        # apply
        driver.find_element(By.CSS_SELECTOR, ".btn-apply").click()

        print(f"Successfully sent CV to offer ID: {offer_id} {job_name}")
        return offer_id, job_name

    except:
        print(
            f"Not on NFJ built-in apply page, skipping offer: {offer_id} {job_name} {link}"
        )


def run_sender(offers: list):
    driver = webdriver.Firefox()

    # index 1 is id, index 2 is job_name and index 8 is link
    for offer in offers:
        load_page(driver, offer.id, offer.job_name, offer.link)
