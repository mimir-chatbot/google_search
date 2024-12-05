import requests
import json
import logging
import os

log = logging.getLogger(__name__)


def agent_fast_reply_google():
    fast_reply = {}

    message = "ciao"
    api_key = "66a8c1fa0fe5e03eb4bea93d"
    service_url = "https://api.scrapingdog.com/google/"

    search_query = ""
    search_urls = ["stackoverflow.com", "github.com"]
    for url in search_urls:
        search_query += f"site:{url} OR " if url != search_urls[-1] else f"site:{url}"

    params = {
        "api_key": api_key,
        "query": f"{message} {search_query}",
        "results": 5,
        "country": "it",
        "page": 0,
    }

    search_results = []
    response = requests.get(service_url, params=params)
    if response.status_code == 200:
        data = response.json()
        for result in data["organic_results"]:
            search_results.append(
                {
                    "href": result["link"],
                    "title": result["title"],
                    "body": result["snippet"],
                }
            )
    else:
        log.error(f"Error in Google Search API: {response})")

    fast_reply["output"] = json.dumps(search_results)
    return fast_reply


def agent_fast_reply_brave():
    fast_reply = {}

    message = "ciao"
    api_key = os.getenv("BRAVE_API_KEY")
    service_url = "https://api.search.brave.com/res/v1/web/search"

    search_query = ""
    search_urls = ["google.com"]
    for url in search_urls:
        search_query += f"site:{url} OR " if url != search_urls[-1] else f"site:{url}"

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
    response = requests.get(service_url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        for result in data["web"]["results"]:
            search_results.append(
                {
                    "href": result["url"],
                    "title": result["title"],
                    "body": result["description"],
                }
            )
    else:
        log.error(f"Error in Brave Search API: {response})")

    fast_reply["output"] = json.dumps(search_results)
    return fast_reply


g = agent_fast_reply_google()
b = agent_fast_reply_brave()
print(g)
print(b)
