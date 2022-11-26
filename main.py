import os
import sqlite3
import datetime
from sqlite3 import Error
from typing import Optional

import requests
from pydantic import BaseModel

import tables
import cvsender


""" add ConfigIni class with methods to get values for filtering, getting offers and cvsender
like this: config = ConfigIni('config.ini')
        config.read('section', 'key') -> value"""


class NfjOffers(BaseModel):
    id: str
    job_name: str
    category: str
    company: str
    tech_main: str
    tech_must: list = None
    tech_nice: list = None
    city: list
    get_ts: datetime.datetime = None
    sent_cv: str = "False"
    sent_ts: Optional[datetime.datetime] = None
    contact: str = "False"
    link: str


def create_connection(db_file):
    """create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("SQLlite3 version: " + sqlite3.version)
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table):
    try:
        c = conn.cursor()
        c.execute(create_table)
    except Error as e:
        print(e)
        conn.close()


def create_offer(conn, offer):
    sql = """ INSERT OR IGNORE INTO offers(offer_id, job_name, category, company, tech_main, get_ts, sent_cv, contact, link)
        VALUES(?,?,?,?,?,datetime('now'),?,?,?) """
    try:
        cur = conn.cursor()
        cur.execute(
            sql,
            (
                offer.id,
                offer.job_name,
                offer.category,
                offer.company,
                offer.tech_main,
                offer.sent_cv,
                offer.contact,
                offer.link,
            ),
        )

        conn.commit()
    except Error as e:
        print("Error when creating offers: " + str(e))
        conn.rollback()
        conn.close()

    create_offers_tech(conn, offer)
    create_offers_cities(conn, offer)


def create_tech(conn, tech_set):
    """Create entries in technology table"""
    sql = """ INSERT OR IGNORE INTO technology(name) VALUES(?) """
    try:
        cur = conn.cursor()
        cur.executemany(sql, [(tech,) for tech in tech_set])
        conn.commit()
    except Error as e:
        print("Error when creating tech: " + str(e))
        conn.rollback()
        conn.close()


def create_offers_tech(conn, offer):
    """Create connections in offers_tech Link Table"""
    sql = """ INSERT OR IGNORE INTO offers_tech (offer_id, tech_name) VALUES (?,?)"""
    for must in offer.tech_must:
        try:
            cur = conn.cursor()
            cur.execute(sql, (offer.id, must))
            conn.commit()
        except Error as e:
            print("Error when creating offers_tech: " + str(e))
            conn.rollback()
            conn.close()


def create_cities(conn, cities_set):
    sql = """ INSERT OR IGNORE INTO cities(name) VALUES(?) """
    try:
        cur = conn.cursor()
        cur.executemany(sql, [(cities,) for cities in cities_set])
        conn.commit()
    except Error as e:
        print("Error when creating cities: " + str(e))
        conn.rollback()
        conn.close()


def create_offers_cities(conn, offer):
    """Create connections in offers_cities Link Table"""
    sql = """ INSERT OR IGNORE INTO offers_cities (offer_id, city_name) VALUES (?,?) """
    for city in offer.city:
        try:
            cur = conn.cursor()
            cur.execute(sql, (offer.id, city))
            conn.commit()
        except Error as e:
            print("Error when creating offers_cities: " + str(e))
            conn.rollback()
            conn.close()


def update_sent_cv(conn, offers_id):
    """Updates rows by id in offers table with sent_cv and sent_ts."""
    sql = """ UPDATE offers SET sent_cv = ?, sent_ts = datetime('now') WHERE offer_id = ? """
    for offer_id in offers_id:
        try:
            cur = conn.cursor()
            cur.execute(
                sql,
                ("True", offer_id),
            )
            conn.commit()
        except Error as e:
            print("Error when updating offers with sent_cv: " + str(e))
            conn.rollback()
            conn.close()


def select_unsend_offers(conn) -> list:
    sql = """ SELECT * FROM offers WHERE sent_cv = 'False'"""
    unsend_offers = None
    try:
        cur = conn.cursor()
        unsend_offers = cur.execute(sql)
    except Error as e:
        print("Error when selecting unsend offers: " + str(e))
        conn.rollback()
        conn.close()

    return list(unsend_offers)


def post_search_nfj(offer_limit: int) -> dict:
    """Requests job offers from NFJ according to payload inside function."""
    print("Getting NFJ job offers.")
    headers = {
        "authority": "nofluffjobs.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "dnt": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    }

    params = {
        "limit": f"{offer_limit}",
        "offset": "0",
        "salaryCurrency": "PLN",
        "salaryPeriod": "month",
        "region": "pl",
    }

    json_data = {
        "criteriaSearch": {
            "city": [
                "remote",
                "katowice",
                "gliwice",
            ],
            "category": [
                "backend",
                "frontend",
                "fullstack",
                "mobile",
                "testing",
                "security",
                "artificial-intelligence",
                "big-data",
                "support",
                "it-administrator",
                "agile",
                "business-intelligence",
                "business-analyst",
            ],
            "seniority": [
                "trainee",
                "junior",
            ],
        },
    }

    response = requests.post(
        "https://nofluffjobs.com/api/search/posting",
        params=params,
        headers=headers,
        json=json_data,
    )
    # print(response.json())
    return response.json()


def extract_nfj(json_nfj: dict) -> list[NfjOffers]:
    """Convert job offers from dictionary to list of NfjOffers class objects."""
    extracted_nfj = []
    # need to exctract info from dict.lists to NfjOffers class
    for postings in json_nfj["postings"]:
        cities = postings["location"]["places"]
        cities = [e["city"] for e in cities]
        # using get() to avert KeyError
        technology = postings.get("technology", "")
        extracted_nfj.append(
            NfjOffers(
                id=postings["id"],
                job_name=postings["title"],
                category=postings["category"],
                company=postings["name"],
                tech_main=technology,
                city=cities,
                link="https://nofluffjobs.com/job/" + postings["url"],
            )
        )
    return extracted_nfj


def get_single_offer_nfj(id: str) -> dict:
    """Get a single offer from NFJ by ID."""
    headers = {
        "authority": "nofluffjobs.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "dnt": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    }
    id_upper = id.upper()
    response = requests.get(
        "https://nofluffjobs.com/api/posting/" + id_upper, headers=headers
    )
    return response.json()


def check_single_offers_nfj(offers_list: list[NfjOffers]) -> list[NfjOffers]:
    offers_list_copy = offers_list
    for idoffer, offer in enumerate(offers_list_copy):
        must_list = []
        nice_list = []
        single_offer = get_single_offer_nfj(offer.id)

        for musts in single_offer["requirements"]["musts"]:
            must_list.append(musts["value"])
        setattr(offers_list[idoffer], "tech_must", must_list)

        for nices in single_offer["requirements"]["nices"]:
            nice_list.append(nices["value"])
        setattr(offers_list[idoffer], "tech_nice", nice_list)

    return offers_list


def filterbytech(seq, filter, wanted=True):
    """Filter by must have technology. Default is wanted."""
    if wanted == True:
        for offer in seq:
            if all(tech in filter for tech in offer.tech_must):
                yield offer
    else:
        for offer in seq:
            if all(tech not in filter for tech in offer.tech_must):
                yield offer


def filterbycity(seq, filter, wanted=True):
    """Filter by city. Default is wanted."""
    if wanted == True:
        for x in seq:
            if x.city in filter:
                yield x
    else:
        for x in seq:
            if x.city not in filter:
                yield x


def filter_offer(offers_list: list) -> list:
    """Looks for technologies.txt and cities.txt files. Reads line by line and by default asserts values are wanted.
    Calls for filterbycity() and filterbytech()."""
    # to do - like in comment above
    filtered_offer = []
    wanted_cities = ("Remote", "Katowice", "Gliwice")

    with open("unwanted_tech.txt", "r") as unw_tech:
        unwanted_tech_list = unw_tech.read().split("\n")

    for good in filterbytech(offers_list, unwanted_tech_list, False):
        # print(good)
        filtered_offer.append(good)

    return filtered_offer


def collect_tech(offers_list: list[NfjOffers]) -> set:
    tech_set = set()
    for offer in offers_list:
        # for idoffer, offer in enumerate(offers_list):
        single_offer = get_single_offer_nfj(offer.id)

        for musts in single_offer["requirements"]["musts"]:
            tech_set.add(musts["value"])

        for nices in single_offer["requirements"]["nices"]:
            tech_set.add(nices["value"])

    return tech_set


def collect_cities(json_nfj: dict) -> set:
    cities_set = set()
    for postings in json_nfj["postings"]:
        cities = postings["location"]["places"]
        cities = [e["city"] for e in cities]
        for city in cities:
            cities_set.add(city)

    return cities_set


def start_collection(conn, json_nfj: dict, extracted_nfj: list[NfjOffers]) -> None:
    """Collect cities and tech from offers and insert them into database."""
    print("Starting collection of tech and cities.")
    tech_set = collect_tech(extracted_nfj)
    cities_set = collect_cities(json_nfj)
    create_tech(conn, tech_set)
    create_cities(conn, cities_set)
    print("Collecting finished. Database updated with cities and technologies.")


def main():
    conn = create_connection("cvsender_sqlite.db")

    if conn is not None:
        create_table(conn, tables.sql_table_cities)
        create_table(conn, tables.sql_table_offers)
        create_table(conn, tables.sql_table_technology)
        create_table(conn, tables.sql_table_offers_cities)
        create_table(conn, tables.sql_table_offers_tech)
    else:
        print("Error, no database connection.")

    response = post_search_nfj(10)
    extracted_nfj = extract_nfj(response)

    start_collection(conn, response, extracted_nfj)

    single_list = check_single_offers_nfj(extracted_nfj)
    list_to_send = filter_offer(single_list)
    for offer in list_to_send:
        create_offer(conn, offer)
    print("Offers added to database successfully.")

    unsend = select_unsend_offers(conn)
    sent_cv = cvsender.run_sender(unsend)
    print(sent_cv)
    update_sent_cv(conn, sent_cv)

    conn.close()


if __name__ == "__main__":
    main()
