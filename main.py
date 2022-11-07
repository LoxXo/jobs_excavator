from typing import Optional
from datetime import datetime
import json
import requests

from bs4 import BeautifulSoup
from pydantic import BaseModel


class NfjOffers(BaseModel):
    id: str
    job_name: str
    company: str
    tech_main: str
    tech_must: list = None
    tech_nice: list = None
    city: list
    sent_cv: bool = False
    sent_ts: Optional[datetime] = None
    link: str


def post_search_nfj() -> dict:
    # returns dict with lists
    headers = {
        "authority": "nofluffjobs.com",
        "accept": "application/json, text/plain, */*",
        "accept-language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "dnt": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
    }

    params = {
        "limit": "10",
        "offset": "0",
        "salaryCurrency": "PLN",
        "salaryPeriod": "month",
        "region": "pl",
    }

    json_data = {
        "rawSearch": "city=remote,katowice,slask seniority=trainee,junior",
        "page": 1,
    }

    response = requests.post(
        "https://nofluffjobs.com/api/search/posting",
        params=params,
        headers=headers,
        json=json_data,
    )
    return response.json()


def extract_nfj(json_nfj: dict) -> list[NfjOffers]:
    extracted_nfj = []
    # need to exctract info from dict.lists to NfjOffers class
    for postings_nfj in json_nfj["postings"]:
        cities = postings_nfj["location"]["places"]
        cities = [e["city"] for e in cities]

        extracted_nfj.append(
            NfjOffers(
                id=postings_nfj["id"],
                job_name=postings_nfj["title"],
                company=postings_nfj["name"],
                tech_main=postings_nfj["technology"],
                city=cities,
                link="https://nofluffjobs.com/job/" + postings_nfj["url"],
            )
        )
    return extracted_nfj


def get_single_offer_nfj(id: str) -> dict:
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


def filterbytech(seq, value):
    for offer in seq:
        if all(tech not in value for tech in offer.tech_must):
            yield offer


def filterbycity(seq, value):
    for x in seq:
        if x.city in value:
            yield x


def filter_offer(offers_list: list) -> list:
    filtered_offer = []
    wanted_cities = ("Remote", "Katowice", "Gliwice")

    with open("unwanted_tech.txt", "r") as unw_tech:
        unwanted_tech_list = unw_tech.read().split("\n")

    for good in filterbytech(offers_list, unwanted_tech_list):
        print(good)
        filtered_offer.append(good)

    return filtered_offer


if __name__ == "__main__":
    q = post_search_nfj()
    extracted_nfj = extract_nfj(q)
    single_list = check_single_offers_nfj(extracted_nfj)
    list_to_send = filter_offer(single_list)
    # print(list_to_send)
    # add sending and db or .txt to save already coveraged offers
