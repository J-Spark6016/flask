from flask import Flask, render_template, request
from myfunctions import get_restaurants, get_direction
import random

app = Flask(__name__)

user_data = {}
category = ['한식', '중식', '일식', '양식', '패스트푸드', '도시락', '치킨', '간식', '술집']

def error_page(msg) : # 오류 페이지!
    return render_template("error.html", msg=msg)

### ------------------- 페이지 전송 ---------------------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/search')
def search():
    return render_template("search.html")

@app.route('/load', methods=['POST','GET'])
def load():
    ip = request.remote_addr

    if request.method == 'POST':
        data = request.get_json()  # 전송된 입력값 JSON 데이터 가져오기
        user_data[ip] = data
        print(data)
    
    if ip in user_data :
        if not 'list' in user_data[ip] :
            return render_template("load.html", msg="위치정보를 받아오는 중입니다.", GetLoc = 1.0)
        else :
            return render_template("load.html", msg="분석중입니다.", GetLoc = 0.0)
    else : # 진행중인 ip가 없을 때
        return error_page("잘못된접근입니다!")
    
@app.route('/result', methods=['POST','GET'])
def result():
    ip = request.remote_addr

    if request.method == 'POST':
        data = request.get_json() # 전송된 위치 데이터 가져오기
        if not 'loction' in user_data[ip] :
            user_data[ip]['location'] = data
            user_data[ip]['dict'] = get_restaurants(user_data[ip]['location']['longitude'],user_data[ip]['location']['latitude'], float(user_data[ip]['range']))

            user_data[ip]['list'] = [{} for i in range(len(category))]
            user_data[ip]['max_title'] = ""

            for key in user_data[ip]['dict'] :
                for i in range(len(user_data[ip]['list'])) : # dict에서 카테고리를 구별해 list에 넣는 작업
                    if user_data[ip]['cb'+str(i+1)] == True and 'category' in user_data[ip]['dict'][key]:
                        if category[i] in user_data[ip]['dict'][key]['category'] :
                            del user_data[ip]['dict'][key]['category']
                            user_data[ip]['list'][i][key] = user_data[ip]['dict'][key] # dict 에서 list로 요소 이동
            del user_data[ip]['dict'] # 'dict 필요 없어졌으니 삭제

            user_data[ip]['dict_w'],max_item = {}, 17 # api에서 지원하는 경유지 15개 + 출발지 1개 + 목적지 1개
            for i in range(len(category)) :
                for item in user_data[ip]['list'][i] :
                    user_data[ip]['dict_w'][item] = (1/user_data[ip]['list'][i][item]['distance']) * (random.randint(8,15)/10) # 거리 가중치 * 랜덤 가중치
            
            user_data[ip]['dict_w'] = [[key, value] for key, value in sorted(user_data[ip]['dict_w'].items(), key=lambda x: x[1], reverse=True)] # Value에 대해 내림차순으로 정렬
            user_data[ip]['dict_w'] = user_data[ip]['dict_w'][:max_item] # 상위 max_item개 까지 슬라이싱

            for i in range(len(user_data[ip]['list'])) :
                for j in range(len(user_data[ip]['dict_w'])) :
                    if user_data[ip]['dict_w'][j][0] in user_data[ip]['list'][i] : # list에서 user_data[ip]['dict_w']로 정보 받아오기
                        user_data[ip]['dict_w'][j][1] = user_data[ip]['list'][i][user_data[ip]['dict_w'][j][0]]
            
            way_points = [] # 경유지 설정하기
            for i in range(len(user_data[ip]['dict_w'])-2) :
                j = i+1
                way_points.append(str(user_data[ip]['dict_w'][j][1]['latitude'])+','+str(user_data[ip]['dict_w'][j][1]['longitude']))

            user_data[ip]['route'] = get_direction(str(user_data[ip]['dict_w'][0][1]['latitude'])+','+str(user_data[ip]['dict_w'][0][1]['longitude']), str(user_data[ip]['dict_w'][-1][1]['latitude'])+','+str(user_data[ip]['dict_w'][-1][1]['longitude']),way_points) # 경로 불러오기

            #print(len(way_points))

            #print(user_data[ip]['dict_w'])
    
    if ip in user_data and 'route' in user_data[ip] :
        return render_template("result.html", am=[len(user_data[ip]['list'][i]) for i in range(len(category))], maa=len(user_data[ip]['dict_w']))
    else : # 진행중인 ip와 위치정보가 없을 때
        return error_page("잘못된접근입니다!")
    
@app.route('/map')
def map():
    ip = request.remote_addr
    
    if ip in user_data and 'location' in user_data[ip] :
        return render_template("map.html"
                               , lat=user_data[ip]['location']['latitude']
                               , lon=user_data[ip]['location']['longitude']
                               , route=user_data[ip]['route']
                               , mark=[[user_data[ip]['dict_w'][i][1]['latitude'], user_data[ip]['dict_w'][i][1]['longitude']] for i in range(len(user_data[ip]['dict_w']))])
    else : # 진행중인 ip와 위치정보가 없을 때
        return error_page("잘못된접근입니다!")

