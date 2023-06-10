import requests
from pyproj import Proj, transform
import math

WGS84 = { 'proj':'latlong', 'datum':'WGS84', 'ellps':'WGS84', }
TM128 = { 'proj':'tmerc', 'lat_0':'38N', 'lon_0':'128E', 'ellps':'bessel',
   'x_0':'400000', 'y_0':'600000', 'k':'0.9999',
   'towgs84':'-146.43,507.89,681.46'}

def haversine(lat1, lon1, lat2, lon2):
    # 지구 반지름 (단위: km)
    radius = 6371

    # 위도와 경도를 라디안 단위로 변환
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # 위도 및 경도 차이 계산
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine 공식을 이용하여 거리 계산
    a = math.sin(dlat/2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = radius * c

    return distance

def tm128_to_wgs84(x, y):
   return transform( Proj(**TM128), Proj(**WGS84), x, y )

def get_restaurants(lat, lng, _range):
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json'
    Authorization = '85a1a288cdf674303be8da8618c71dc7'
    
    #address = get_address(lat, lng)

    result = {}
    pre_response = 0

    page, size = 1, 15

    while True :
        headers = {
            'Authorization': "KakaoAK " + Authorization
        }
        params = {
            'query': ' 음식점',
            'x': lat,
            'y': lng,
            'category_group_code': 'FD6',
            'page': page,
            'size': size,
            'sort': 'distance',
            'radius': _range * 1000
        }

        real_response = requests.get(url, headers=headers, params=params).json()
        if not 'documents' in real_response or real_response == pre_response :
            #print(real_response)
            break
        else :
            res = real_response['documents']

        pre_response = real_response
        
        for i in range(len(res)) :
            title = res[i]['place_name']
            category = res[i]['category_name'][6:]
            rlat, rlng = float(res[i]['x']), float(res[i]['y'])

            result[title] = {'category' : category, 'latitude' : rlat, 'longitude' : rlng, 'distance' : haversine(lat, lng, rlat, rlng)}
        
        page += 1
    return result



def get_address(lat, lon):
    client_id = 'wokfay6q1u'  # 네이버 API 클라이언트 ID
    client_secret = '0J0AgTolPxk4qbCQCoCLtoLxMSRRdoATDJZzDV8w'  # 네이버 API 클라이언트 시크릿

    coords = str(lat)+', '+str(lon)
    output = "json"
    orders = 'addr'
    endpoint = "https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc"
    url = f"{endpoint}?coords={coords}&output={output}&orders={orders}"

    # 헤더
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }

    res = requests.get(url, headers=headers)
    data = res.json()
    si = data['results'][0]['region']['area1']['name']
    gu = data['results'][0]['region']['area2']['name']
    dong = data['results'][0]['region']['area3']['name']
    num = data['results'][0]['land']['number1']

    result = si+' '+gu+' '+dong+' '+num

    return result

def get_direction(start, goal,waypoint_list):
    client_id = 'wokfay6q1u'  # 네이버 API 클라이언트 ID
    client_secret = '0J0AgTolPxk4qbCQCoCLtoLxMSRRdoATDJZzDV8w'  # 네이버 API 클라이언트 시크릿

    if len(waypoint_list) <= 5 :
        url = "https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving"
    else :
        url = "https://naveropenapi.apigw.ntruss.com/map-direction-15/v1/driving"
    
    way = ""
    for item in waypoint_list :
        way += item + "|"
    way = way[:-1]

    # 헤더
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }
    params = {
            'start': start,
            'goal': goal,
            'waypoints': waypoint_list,
            'option': 'trafast',
            'lang': 'ko'
        }

    res = requests.get(url, headers=headers, params=params).json()

    if 'route' in res :
        result = res['route']['trafast'][0]['path']
    else :
        result = res['message']
    return result

if __name__ == '__main__' :
    result = get_restaurants(126.95832,37.49489,3)
    print(result)