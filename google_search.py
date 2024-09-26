from typing import List
from cat.mad_hatter.decorators import hook, plugin
from cat.log import log
from pydantic import BaseModel, Field
import json
import requests



class Filters(BaseModel):
    links: List[str] = Field(default=["google.com", "bing.com"])
    enable: bool = True


@plugin
def settings_model():
    return Filters


@hook(priority=5)
def before_cat_reads_message(user_message_json: dict, cat) -> dict:
    if "prompt_settings" in user_message_json:
        cat.working_memory["search"] = user_message_json["prompt_settings"].get("search", [])
        cat.working_memory["language"] = user_message_json["prompt_settings"].get("lang", "en")
    return user_message_json


@hook
def agent_fast_reply(fast_reply, cat):
    language = cat.working_memory["language"]
    search_urls = cat.working_memory["search"]
    if not search_urls:
        return fast_reply

    message = cat.working_memory["user_message_json"]["text"]
    api_key = "66a8c1fa0fe5e03eb4bea93d"
    service_url = "https://api.scrapingdog.com/google/"

    search_query = ""
    for url in search_urls:
        search_query += f"site:{url} OR " if url != search_urls[-1] else f"site:{url}"

    params = {
        "api_key": api_key,
        "query": f"{message} {search_query}",
        "results": 5,
        "country": 'it',
        "page": 0
    }

    search_results = []
    response = requests.get(service_url, params=params)
    if response.status_code == 200:
        data = response.json()
        for result in data["organic_data"]:
            search_results.append({
                    "href": result["link"],
                    "title": result["title"],
                    "body": result["snippet"],
                })
    else:
        log.error(f"Error in Google Search API: {response})")

    fast_reply["output"] = json.dumps(search_results)
    return fast_reply
