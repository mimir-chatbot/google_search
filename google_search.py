from typing import List
from cat.mad_hatter.decorators import hook, plugin
from cat.log import log
from pydantic import BaseModel, Field
from googlesearch import search
import json


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
    search_query = ""
    for url in search_urls:
        search_query += f"site:{url} OR " if url != search_urls[-1] else f"site:{url}"
    search_results = []
    for result in search(f"{message} {search_query}", advanced=True, lang=language, num_results=4):
        search_results.append({
            "href": result.url,
            "title": result.title,
            "body": result.description,
        })

    fast_reply["output"] = json.dumps(search_results)
    return fast_reply
