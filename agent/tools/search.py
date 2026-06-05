from agent.core.registry import get_tools_for_api, get_tool
from agent.core.state import load_state, save_state
from agent.core.executor import execute_tool
import anthropic
import json
import requests
from bs4 import BeautifulSoup
import os
import http.client
from dotenv import load_dotenv


load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")

def search_jobs(query, location = None,focus_area=None ):
    url = "https://jsearch.p.rapidapi.com/search"

    full_query = query
    if location:
        full_query += f"in {location}"
    if focus_area:
        full_query += f"in {focus_area}"
    

    headers = {
        "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    querystring = {"query": full_query, "page": "1", "num_pages": "1", "country": "us", "date_posted": "all"}

    response = requests.get(url, headers=headers, params=querystring)

    return response.json()

def _serper_search(query:str) -> dict:
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
    "q": query,
    })
    headers = {
    'X-API-KEY': SERPER_API_KEY ,
    'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return json.loads(data.decode("utf-8"))

def search_company_pain_points(company_name, role=None):
    query = f"{company_name} company challenges, company pain points"
    if role:
        query += f"{role}"
    return _serper_search(query)

def search_visa_sponsorship(company_name, role=None):
    query = f"{company_name} visa sponsorship"
    if role:
        query += f"{role}"
    return _serper_search(query)


def search_funding(company_name, role=None):
    query = f"{company_name} funding status"
    if role:
        query += f"{role}"
    return _serper_search(query)


def search_fundraising_stage(company_name, role=None):
    query = f"{company_name} fundraising stage"
    if role:
        query += f"{role}"
    return _serper_search(query)


def search_glassdoor_reviews(company_name, role=None):
    query = f"{company_name} glassdoor reviews, employee reviews"
    if role:
        query += f"{role}"
    return _serper_search(query)


def search_press_coverage(company_name, role=None):
    query = f"{company_name} press coverage, news"
    if role:
        query += f"{role}"
    return _serper_search(query)


def search_salary_range(company_name, role=None):
    query = f"{company_name} salary"
    if role:
        query += f"{role}"
    return _serper_search(query)


def search_interview_process(company_name, role=None):
    query = f"{company_name} interview process"
    if role:
        query += f"{role}"
    return _serper_search(query)

def search_career_trajectory(company_name, role=None):
    query = f"{company_name} career trajectory"
    if role:
        query += f"{role}"
    return _serper_search(query)

def search_similar_roles(company_name, role=None):
    query = f"{company_name} similar roles"
    if role:
        query += f"{role}"
    return _serper_search(query)

def search_key_people(company_name, role=None):
    query = f"{company_name} employees and emails"
    if role:
        query += f"{role}"
    return _serper_search(query)

def search_company_website(company_name, role=None):
    query = f"{company_name} company website"
    if role:
        query += f"{role}"
    return _serper_search(query)

def search_key_people(company_name, roles=None, website=None):
    if not website:
        serper_result = search_company_website(company_name)
        # extract the first URL from serper results
        website = serper_result["organic"][0]["link"]
    
    domain = website.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    
    response = requests.get(
        "https://api.hunter.io/v2/domain-search",
        params={
            "domain": domain,
            "api_key": os.getenv("HUNTER_API_KEY")
        }
    )
    return response.json()


def fetch_job_description(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser" )
    return soup.get_text()

def fetch_my_resume():
    try:
        with open ('agent/profile.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}



