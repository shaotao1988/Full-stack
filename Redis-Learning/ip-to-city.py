import csv, json

def ip_to_score(ip_address):
    score = 0
    for v in ip_address.split('.'):
        score = score*256 + int(v, 10)
    return score

def import_ips_to_redis(conn, filename):
    csv_file = csv.reader(open(filename, 'r'))
    for count, row in enumerate(csv_file):
        start_ip = row[0] if row else ''
        if 'i' in start_ip.lower():
            continue
        if '.' in start_ip:
            start_ip = ip_to_score(start_ip)
        elif start_ip.isdigit():
            start_ip = int(start_ip)
        else:
            continue

        # One city may have multipe entry in the csv file, create unique city id.
        city_id = row[2] + '_' + str(count)
        conn.zadd('ip2cityid', city_id, start_ip)

def import_cities_to_redis(conn, filename):
    for row in csv.reader(open(filename, 'rb')):
        if len(row) < 4 or not row[0].isdigit():
            continue
        row = [i.decode('latin-1') for i in row]
        city_id = row[0]
        country = row[1]
        region = row[2]
        city = row[3]
        conn.hset('cityid2city', city_id, json.dumps([city, region, country]))

def find_city_by_ip(conn, ip_address):
    if isinstance(ip_address, str):
        ip_address = ip_to_score(ip_address)

    # find the largest one that is less or equal than the given ip
    city_id = conn.zrevrangebyscore('ip2cityid', ip_address, 0, start = 0, num = 1)

    if not city_id:
        return None
    
    city_id = city_id[0].partition('_')[0]
    return json.load(conn.hget('cityid2city', city_id))

if __name__ == '__main__':
    import redis
    conn = redis.Redis()
    import_ips_to_redis(conn, 'GeoLiteCity-Blocks.csv')
    import_cities_to_redis(conn, 'GeoLiteCity-Location.csv')

    print(find_city_by_ip(conn, 28548044))