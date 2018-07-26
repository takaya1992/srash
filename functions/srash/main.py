import searchengine

def handle(event, context):
    engine = searchengine.SearchEngineFactory.create(event['search_engine'])
    if engine is None:
        # TODO: error をイイカンジにする
        return {message: '"search_engine" is not found.'}
    
    pager = engine.search(event['keyword'])
    entry = None
    for page in pager:
        entry = page.find_entry(event['domain'])
        if entry is not None:
            break
    return {
        'search_engine': event['search_engine'],
        'entry': entry.to_dict()
    }
