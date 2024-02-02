import json, os, sys
import utils


def should_notify(watch_item: dict) -> bool:
    """Determines if user should be notified of change/insertion/deletion"""
    
    # If we can't get the html, we don't notify
    try:
        html = utils.get_html(watch_item['url'], watch_item.get('html_id'))
    except:
        return False
    
    if watch_item['on'] == 'in':
        return watch_item['txt'] in html
    
    elif watch_item['on'] == 'not_in':
        return watch_item['txt'] not in html

    elif watch_item['on'] == 'change':
        
        str_url = watch_item['url'].replace('/', '_')
        path_to_cached = os.path.join('cache', str_url) 

        # If we've cached the page, we notify if there are differences
        if os.path.exists(path_to_cached):
            with open(path_to_cached, 'r') as f:
                cached = f.read()

            # But we still write the new page to the cache
            utils.write_to_cache(path_to_cached, html)
                
            return cached != html
        
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
        if should_notify(watch_item):
            print(f'- NOTIFY: YES\tITEM: "{name}"')
            utils.notify(name, watch_item, ntfy_topic)
        else:
            print(f'- NOTIFY: NO\tITEM: "{name}"')
