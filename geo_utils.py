import math

# Notes:
# Lat: first URL argument, south (-90) -> north (90)
# Lng: second URL argument, west (-180) -> east (180) [Europe-centered]
# Zoom: third URL argument, <=21

# Calculates meters per one pixel (on a specific zoom level and latitude).
# Source: https://gis.stackexchange.com/questions/7430/what-ratio-scales-do-google-maps-zoom-levels-correspond-to
def get_meters_per_px(lat, zoom):
    return 156543.03392 * math.cos(lat * math.pi / 180) / (2 ** zoom)

# Calculates the great circle distance in metres using the Haversine formula.
def get_distance(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    d_lat = lat2 - lat1 
    d_lng = lng2 - lng1 
    a = math.sin(d_lat/2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lng/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    radius = 6371  # Radius of earth in kilometers.
    return c * radius * 1000

# Uses the Haversine distance between two very close points to approximate the lat/lng increment 
# corresponding to a given pixel increment (on a given zoom level and latitude).
def get_latlng_inc_for_px_inc(lat, zoom, px_inc):
    eps = 0.0001
    lng = 0
    meters_per_px = get_meters_per_px(lat, zoom)
    meters_per_lat = get_distance(lat - eps/2, lng, lat + eps/2, lng) * (1 / eps)
    meters_per_lng = get_distance(lat, lng - eps/2, lat, lng + eps/2) * (1 / eps)

    meters_inc = px_inc * meters_per_px
    lat_inc = meters_inc / meters_per_lat
    lng_inc = meters_inc / meters_per_lng
    return lat_inc, lng_inc