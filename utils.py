import requests, os

def write_to_cache(path_to_cached: str, html: str) -> None:
    os.makedirs('cache', exist_ok = True)
    with open(path_to_cached, 'w+') as f:
        f.write(html)

def get_html(url: str) -> str:
    """Gets HTML content with requests"""
    response = requests.get(url) # verify = False to ignore SSL errors
    html = response.content.decode("utf-8", "ignore")
    return html

def get_html_id_content(html: str, html_id: str) -> str:
    """Gets content of the first html element with id `html_id`"""
    return html.split(f'id="{html_id}"')[1].split('>')[1].split('</')[0]


def notify(name: str, watch_item: dict, ntfy_topic: str) -> None:
    """Uses ntfy.sh to send notification to user"""
    requests.post(
        "https://ntfy.sh/" + ntfy_topic,
        headers = {
            "Title": name,
            "Tags": "website-watcher",
        },
        data = 'Has triggered: ' + watch_item['url']
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