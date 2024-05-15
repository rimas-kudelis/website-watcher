import json, os, sys, re
import utils
from bs4 import BeautifulSoup


def should_notify(watch_item: dict) -> bool:
    """Determines if user should be notified of change/insertion/deletion"""
    
    # If we can't get the html, return None to notify as unreachable
    try:
        html = utils.get_html(watch_item['url'], watch_item.get('html_id'))
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
        
        str_url = watch_item['url'].replace('/', '_')
        path_to_cached = os.path.join('cache', str_url) 

        def html_section(html: str) -> str:
            """Returns the section of the html that we want to compare"""
            if watch_item.get('html_id'):
                b = BeautifulSoup(html, 'html.parser')
                return str(b.find(id = watch_item['html_id']))
            return html

        # If we've cached the page, we notify if there are differences
        if os.path.exists(path_to_cached):
            with open(path_to_cached, 'r') as f:
                cached = html_section(f.read())

            # But we still write the new page to the cache
            utils.write_to_cache(path_to_cached, html)
                
            return cached != html_section(html)
        
        # Otherwise we just save the page and don't notify
        else:
            utils.write_to_cache(path_to_cached, html)
            return False


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

    for name, watch_item in watch_items.items():

        # Validate watch item
        msg = utils.invalid_watch_item_msg(name, watch_item)
        if msg:
            print(msg)
            continue

        # Notify user if necessary
        should = should_notify(watch_item)
        if should:
            print(f'- NOTIFY: YES\tITEM: "{name}"')
            utils.notify(name, watch_item, ntfy_topic)
        elif should is None:
            print(f'- NOTIFY: ERR\tITEM: "{name}"')
            utils.notify(name, watch_item, ntfy_topic, reacheable = False)
        else:
            print(f'- NOTIFY: NO\tITEM: "{name}"')
