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
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def _notion_request(method, endpoint, data=None ):
    headers = {
        "Authorization": f"Bearer {os.getenv('NOTION_API_KEY')}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    response = requests.request(
        method,
        f"https://api.notion.com/v1{endpoint}",
        headers = headers,
        json = data
    )
    return response.json()

def create_application_record(company_name, role, confirmation_data=None, key_contacts=None):
    data = {
        "parent": {"database_id": os.getenv("NOTION_DATABASE_ID")},
        "properties": {
            "Company": {"title": [{"text": {"content": company_name}}]},
            "Role": {"rich_text": [{"text": {"content": role}}]},
            "Status": {"select": {"name": "applied"}}
        }
    }
    return _notion_request("POST", "/pages", data)

def log_outreach(record_id, recipient, email_summary, sent_at):
    data = {
        "properties": {
            "Key Contacts": {"rich_text": [{"text": {"content": str(recipient)}}]},
            "Notes": {"rich_text": [{"text": {"content": f"Emailed {sent_at}: {email_summary}"}}]}
        }
    }
    return _notion_request("PATCH", f"/pages/{record_id}", data)

def update_app_status (record_id, status):
    data = {
        "properties": {
            "Status": {"select": {"name": status}},
        }
    }
    return _notion_request("PATCH", f"/pages/{record_id}", data)


def update_contact_response(record_id, contact_name, response_status, response_summary=None):
    data = {
        "properties": {
            "Response Status": {"rich_text": [{"text": {"content":f"{contact_name}: {response_status}" }}],

            "Notes": {"rich_text": [{"text": {"content": response_summary or "" }}]}
        }
    }
    }
    return _notion_request("PATCH", f"/pages/{record_id}", data)

def add_notes(record_id, key_notes = None ):
    data = {
        "properties": {
            "Notes": {"rich_text": [{"text": {"content": key_notes or "" }}]}
        }
    }
    return _notion_request("PATCH", f"/pages/{record_id}", data)

def schedule_next_step(record_id,  contact_name, next_step, scheduled_time, key_notes=None):
    data = {
        "properties": {
            "Next Steps": {"rich_text": [{"text": {"content": f"{next_step} with {contact_name} at {scheduled_time}. {f'Notes: {key_notes}' if key_notes else ''}  " }}]}

        }
    }
    return _notion_request("PATCH", f"/pages/{record_id}", data)

def log_followup(record_id,  followup_number, sent_at, summary ):
    data = {
        "properties": {
            "Log Followup": {"rich_text": [{"text": {"content": f"{followup_number} which was sent at {sent_at}. {f'Notes: This is what you sent:{summary}' if summary else ''}  "}}]}

        }
    }
    return _notion_request("PATCH", f"/pages/{record_id}", data)

def fetch_application_record(record_id=None, company_name=None):
    if record_id:
        return _notion_request("GET", f"/pages/{record_id}", None)
    else:
        data = {
            "filter": {
                "property": "Company",
                "title": {"equals": company_name}
            }
        }
        return _notion_request("POST", f"/databases/{os.getenv('NOTION_DATABASE_ID')}/query", data)