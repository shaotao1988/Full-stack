
# default page time out: 5min
PAGE_TIME_OUT = 300

def cache_request(conn, request, callback):
    # if can't be cached, use the callback to handle request
    if not can_cache(conn, request):
        return callback(request)

    page_key = 'cache:' + hash_request(request)
    content = conn.get(page_key)

    # if content hasn't been cached, generate the content and cache it
    if not content:
        content = callback(request)
        conn.setex(page_key, content, PAGE_TIME_OUT)

    return content

def can_cache(conn, request):
    '''
    check if the request is retrieving item information
    only the item with high enough view count can be cached.
    '''
    item_id = extract_item_id(request)
    if not item_id or is_dynamic(request):
        return False
    
    rank = conn.zrank('viewed:', item_id)
    return rank is not None and rank < 10000

def extract_item_id(request):
    return True

def is_dynamic(request):
    return False
    
# convert request to hash string
def hash_request(request):
    return 'test-hash'
