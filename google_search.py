from typing import List
from cat.mad_hatter.decorators import hook, plugin
from cat.log import log
from pydantic import BaseModel, Field
import json
import requests
from bs4 import BeautifulSoup
import re


"""
TODO:
- [ ] map language to country code for brave search
- [ ] rename repo and widget to web_search
"""


class Filters(BaseModel):
    links: List[str] = Field(default=["google.com", "bing.com"])
    enable: bool = True


@plugin
def settings_model():
    return Filters


@hook(priority=5)
def before_cat_reads_message(user_message_json: dict, cat) -> dict:
    if "prompt_settings" in user_message_json:
        print("google_search has been called")
        cat.working_memory["search"] = user_message_json["prompt_settings"].get(
            "search", []
        )
        cat.working_memory["language"] = user_message_json["prompt_settings"].get(
            "lang", "en"
        )
    return user_message_json


@hook
def agent_fast_reply(fast_reply, cat):
    log.info("Running Brave Search plugin")
    language = cat.working_memory["language"]
    cat_search = cat.working_memory["search"]

    search_urls = []
    if type(cat_search) is not dict:
        search_urls = cat_search
    elif type(cat_search) is dict:
        search_urls = list(cat.working_memory["search"].values())

    print(f"search_urls: {search_urls}")
    if not search_urls:
        log.info("No search URLs provided, skipping search")
        return fast_reply

    message = cat.working_memory["user_message_json"]["text"]
    api_key = "BSAxTw3NOXYr4t1PqC2bhLVpJ_cqHbu"
    service_url = "https://api.search.brave.com/res/v1/web/search"

    search_query = ""
    for url in search_urls:
        search_query += f"site:{url} OR " if url != search_urls[-1] else f"site:{url}"

    log.info(f"Constructed search query with filters: {search_query}")

    # Request headers
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }

    params = {
        "q": f"{message} {search_query}",
        "count": 5,
        "country": "it",
    }

    search_results = []
    try:
        response = requests.get(service_url, params=params, headers=headers)
        log.info(f"Search API response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            log.info(f"Found {len(data['web']['results'])} search results")
            # log.info(f"data: {data}")
            for result in data["web"]["results"]:
                body = (
                    BeautifulSoup(result["description"], "html.parser")
                    .get_text()
                    .strip()
                )
                # Add ellipsis if the sentence doesn't end with proper punctuation
                if body and not body[-1] in ".!?…":
                    body += "..."

                search_results.append(
                    {
                        "href": result["url"],
                        "title": result["title"],
                        "body": body,
                    }
                )
        else:
            log.error(f"Error in Brave Search API: Status {response.status_code}")
    except Exception as e:
        log.error(f"Exception during search request: {str(e)}")
        return fast_reply

    fast_reply["output"] = json.dumps(search_results)
    return fast_reply
