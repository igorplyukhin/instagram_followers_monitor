import csv
import json
import math
from pprint import pprint
import subprocess
import time


with open('followers.json', 'r') as f:
    followers = json.load(f)

command_template = """curl 'https://www.instagram.com/{username}/?__a=1' -H 'pragma: no-cache' -H 'cookie: ds_user_id=5802924775; mid=Wlcy5QAEAAHjIpWdSStiUxb6Alq2; mcd=3; fbm_124024574287414=base_domain=.instagram.com; shbid=12189; ig_cb=1; datr=8RwpW26vPMlKFy71tY9xUaXL; csrftoken=ablLyNKzr5IEJDf96RKcb1JCLfvpmqKF; csrftoken=vHscIy3LQ3wFWnasxFramXjivISwDrB7; sessionid=5802924775%3AhVW56t3YGfTxF7%3A16; rur=VLL; shbts=1553170380.1821196; urlgen="{{\"89.17.61.234\": 201825\054 \"185.79.103.87\": 202173\054 \"176.59.45.101\": 12958}}:1h73B8:aAY7VtjjYv8-9hdmyWGOnOU9fBQ"' -H 'x-ig-app-id: 936619743392459' -H 'accept-encoding: gzip, deflate, br' -H 'accept-language: en-GB,en;q=0.9,en-US;q=0.8,ru;q=0.7' -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36' -H 'accept: */*' -H 'cache-control: no-cache' -H 'authority: www.instagram.com' -H 'x-requested-with: XMLHttpRequest' -H 'x-instagram-gis: dca0d7a694ce95c68bdb9298443cd7aa' -H 'referer: https://www.instagram.com/kukhterinaev/' --compressed > temp.json"""

index = 0
followers_filled = []
for user in followers:
    subprocess.run(command_template.format(username=user['username']), shell=True, capture_output=True)
    with open('temp.json', 'r') as f:
        try:
            data = json.load(f)
        except:
            print(f'проблема с парсингом JSON в {user["username"]}')
            continue
    
    if 'graphql' not in data:
        time.sleep(5)
        print(f'нет graphql в ответе сервера, ответ: {data}')
        continue
    photos_edges = data['graphql']['user']['edge_owner_to_timeline_media']
    last_photos_posted_in_one_day = False
    if photos_edges and len(photos_edges['edges']) > 2:
        last_photos_posted_at = [photos_edges['edges'][i]['node']['taken_at_timestamp'] for i in range(3)]
        difference = int(math.fabs(min(last_photos_posted_at) - max(last_photos_posted_at)))
        if difference < 86400:
            last_photos_posted_in_one_day = True

    user['follows'] = data['graphql']['user']['edge_follow']['count']
    user['posts'] = data['graphql']['user']['edge_owner_to_timeline_media']['count']
    user['biography'] = data['graphql']['user']['biography']
    user['last_photos_posted_in_one_day'] = last_photos_posted_in_one_day
    followers_filled.append(user)

    print(f'Итерация {index}/{len(followers)}')
    time.sleep(0.5 if index % 10 != 0 else 3)
    if index % 10 == 0:
        with open(f'filled/followers_filled_{index}.json', 'w') as f:
            json.dump(followers_filled, f)
    index += 1

with open('followers_filled.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Имя', 'Username', 'Подписан на', 'Постов', 'Био', 'Последние фото в 1 день'])
    for user in followers_filled:
        full_name = user["full_name"].replace('"', "")
        bio = user["biography"].replace('"', "")
        writer.writerow([
            full_name,
            user["username"],
            user["follows"],
            user["posts"],
            bio,
            1 if user["last_photos_posted_in_one_day"] else 0
        ])

print('#готоводело')
