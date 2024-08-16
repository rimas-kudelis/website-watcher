import json, sys, re, requests, hashlib
from bs4 import BeautifulSoup


def should_notify(watch_item: dict) -> bool:
    """Determines if user should be notified of change/insertion/deletion"""
    
    # If we can't get the html, return None to notify as unreachable
    try:
        url = watch_item['url']
        response = requests.get(url) # verify = False to ignore SSL errors
        html = response.text
    except:
        return None
    
    # Check if the text is in the html (case insensitive)
    is_in = False
    if 'txt' in watch_item:
        is_in = re.search(watch_item['txt'], html, re.IGNORECASE) is not None

    if watch_item['on'] == 'in':
        return is_in
    
    elif watch_item['on'] == 'not_in':
        return not is_in

    elif watch_item['on'] == 'change':

        to_hash = response.content

        if watch_item.get('html_id'):

            b = BeautifulSoup(html, 'html.parser')
            sec = b.find(id = watch_item['html_id'])
            if sec is None:
                print(f'Could not find html_id for {watch_item["url"]}')
                return None
            to_hash = sec.encode()
        
        old_hash = watch_item.get('hash')
        new_hash = hashlib.sha256(to_hash).hexdigest()
        print(f'\tOld hash: {old_hash} New hash: {new_hash} Same: {old_hash == new_hash}')

        notify = (old_hash is not None) and (old_hash != new_hash)
        watch_item['hash'] = new_hash
        return notify
    
def notify(name: str, watch_item: dict, ntfy_topic: str, reacheable: bool = True) -> None:
    """Uses ntfy.sh to send notification to user"""
    print(f'\tNotifying "{name}" \tReachable: {reacheable}')
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
    
    if watch_item.get('repeat', 'once') not in ['once', 'forever']:
        return f'Watch item "{name}" does not have a valid `repeat`'
    
    return None


if __name__ == '__main__':

    # Get ntfy topic from first command line arg
    if len(sys.argv) <= 1:
        print('Please provide a ntfy topic as the first command line argument')
        exit()
    ntfy_topic = sys.argv[1]
    print(f'Using ntfy topic "{ntfy_topic}"')

    # Read settings
    watch_items = {}
    try:
        with open('watch.json','r') as f:
            watch_items = json.loads(f.read())
            print(f'Read {len(watch_items)} watch items')
    except:
        print('Could not read watch.json')
        exit()

    to_del = []
    for name, watch_item in watch_items.items():

        print(f'Checking "{name}":')

        # Validate watch item
        msg = invalid_watch_item_msg(name, watch_item)
        if msg:
            print(msg)
            continue

        # Notify user if necessary
        should = should_notify(watch_item)
        
        if should:
            print(f'\tNOTIFY: YES')
            notify(name, watch_item, ntfy_topic)

            # Delete watch item if it should only be checked once
            if watch_item.get('repeat', 'once') == 'once':
                to_del.append(name)
                print(f'\tDeleted "{name}"')

        elif should is None:
            print(f'\tNOTIFY: ERR')
            notify(name, watch_item, ntfy_topic, reacheable = False)
        else:
            print(f'\tNOTIFY: NO')
    
    # Delete watch items that should only be checked once
    for name in to_del:
        del watch_items[name]
        
    # Overwrite watch.json with updated watch_items
    with open('watch.json','w+') as f:
        f.write(json.dumps(watch_items, indent = 4))
