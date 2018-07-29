import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')

import searchengine

def lambda_handler(event, context):
    engine = searchengine.SearchEngineFactory.create(event['search_engine'])
    if engine is None:
        raise Exception('"search_engine" is not found.')

    result = {
        'search_engine': event['search_engine'],
        'domain': event['domain'],
        'keyword': event['keyword'],
        'entry': None
    }

    pager = engine.search(event['keyword'])
    entry = None
    for page in pager:
        entry = page.find_entry(event['domain'])
        if entry is not None:
            break
    if entry is None:
        return result
    
    result['entry'] = entry.to_dict()
    return result
