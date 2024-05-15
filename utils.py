import requests, os
from bs4 import BeautifulSoup

def write_to_cache(path_to_cached: str, html: str) -> None:
    os.makedirs('cache', exist_ok = True)
    with open(path_to_cached, 'w+') as f:
        f.write(html)

def get_html(url: str, html_id: str) -> str:
    """Gets HTML content with requests"""
    response = requests.get(url) # verify = False to ignore SSL errors
    html = response.content.decode("utf-8", "ignore")
    if html_id:
        b = BeautifulSoup(html, 'html.parser')
        html = str(b.find(id=html_id))
    return html


def notify(name: str, watch_item: dict, ntfy_topic: str, reacheable: bool = True) -> None:
    """Uses ntfy.sh to send notification to user"""
    requests.post(
        "https://ntfy.sh/" + ntfy_topic,
        headers = {
            "Title": name,
            "Click": watch_item['url'],
            "Tags": "website-watcher",
        },
        data = 'Has triggered: ' + watch_item['url'] if reacheable else 'Could not reach: ' + watch_item['url']
    )


def invalid_watch_item_msg(name: str, watch_item: dict) -> str:
    """Validates a watch item"""

    if not isinstance(watch_item, dict):
        return f'Watch item "{name}" is not a dictionary'
    
    if not 'url' in watch_item:
        return f'Watch item "{name}" does not have a `url`'
    
    if not 'on' in watch_item or not watch_item['on'] in ['in', 'not_in', 'change']:
        return f'Watch item "{name}" does not have a valid `on`'
    
    if watch_item['on'] in ['in', 'not_in'] and not 'txt' in watch_item:
        return f'Watch item "{name}" does not have a `txt`'
    
    return None