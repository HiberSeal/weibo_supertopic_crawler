import requests
import json
import time
import random
from dateutil import parser
from datetime import datetime
from urllib.parse import urlencode
import pymysql.cursors
from dbutils.pooled_db import PooledDB

base_url = 'https://m.weibo.cn/api/container/getIndex?'
headers = {
    'Host': 'm.weibo.cn',
    'Referer': 'https://m.weibo.cn/p/index?extparam=%E8%8C%89%E8%8E%89%E7%99%BD%E7%8E%AB%E7%91%B0&containerid=1008081f90f24694784f763d6c5b789a54c0d2&luicode=20000174',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}
# 创建连接池
pool = PooledDB(
    creator=pymysql,  # 指定创建数据库连接对象的方式
    host='localhost',
    user='root',
    password='123456',
    database='rosemin',
    charset='utf8mb4'  # 微博内容中存在emoji 编码设置utf8mb4
)
count = 0  # 计数器


def crawler(since_id=None):
    try:
        params = {
            'extparam': '%E8%8C%89%E8%8E%89%E7%99%BD%E7%8E%AB%E7%91%B0',
            'containerid': '1008081f90f24694784f763d6c5b789a54c0d2_-_sort_time',
            'luicode': '20000174',
            'since_id': since_id
        }
        print('\n本次since_id:', since_id)
        url = base_url + urlencode(params)
        s = requests.session()
        s.keep_alive = False
        response = s.get(url, headers=headers)
        # 睡会吧~
        rand_num = random.uniform(1, 3)
        time.sleep(rand_num)
        if response.status_code == 200:
            text = response.text
            json_result = json.loads(text)
            # 最后一页往后没有内容时ok=0, 返回False, 结束循环
            if json_result['ok'] == 0:
                print('到达最后一页')
                return False
            since_id = str(json_result['data']['pageInfo']['since_id'])
            print('下次since_id:', since_id)
            # 这里默认处理的都是card_type=9
            cards = json_result['data']['cards']
            cards_count = len(cards)
            con = pool.connection()
            cur = con.cursor()
            for i in range(cards_count):
                mblog = json_result['data']['cards'][i]['mblog']
                userid = mblog['user']['id']
                bid = mblog['bid']
                weibo_url = "https://weibo.com/" + str(userid) + "/" + bid
                exist_sql = "SELECT EXISTS(SELECT 1 FROM weibo_supertopic WHERE weibo_url = '{}');".format(weibo_url)
                cur.execute(exist_sql)
                exist_result = cur.fetchone()
                # 数据库中已存在weibo_url与之一致的数据, 返回False, 结束循环;
                # 也可将以下三行注释，则会继续检查在该条已入库数据，之后的数据，是否均已入库
                if exist_result[0] == 1:
                    print('数据库中数据已存在')
                    return False, ''
                if exist_result[0] == 0:
                    create_at = mblog['created_at'] # twitter_time格式的字符串
                    date = parser.parse(create_at)  # datetime
                    post_time = date.strftime("%Y-%m-%d %H:%M:%S")  # 自定时间格式的字符串
                    poster = mblog['user']['screen_name']
                    # 用户地区字段可能会不存在
                    if 'region_name' in mblog:
                        region_name = mblog['region_name']
                    else:
                        region_name = None
                    reposts_count = mblog['reposts_count']
                    comments_count = mblog['comments_count']
                    attitudes_count = mblog['attitudes_count']
                    content = mblog['text']
                    # 如果内容前面带有“茉莉和白玫瑰”的超话标识，就去掉它
                    if content[:8] == '<a  href':
                        content = content[427:]
                    # 数据入库
                    insert_sql = "INSERT INTO weibo_supertopic(post_time, poster, region, content, reposts_count, comments_count, attitudes_count, weibo_url) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
                    data = (post_time, poster, region_name, content, reposts_count, comments_count, attitudes_count, weibo_url)
                    cur.execute(insert_sql, data)
                    con.commit()
                    global count
                    count += 1
                    print('已提交', count, '条数据')
            cur.close()
            con.close()
            # 返回True, 继续请求下一页; since_id:用于找到请求的下一页
            return True, since_id
    except Exception as e:
        print('Error:', e)


if __name__ == '__main__':
    start_time = time.time()
    for page in range(99999):
        if page == 0:
            # the_tuple = crawler('4858615070197709') # 卡在此处
            the_tuple = crawler()
        elif the_tuple is not None and the_tuple[0]:
            the_tuple = crawler(the_tuple[1])
        else:
            break
    elapsed_time = time.time() - start_time
    print(f"运行时间：{elapsed_time:.2f} 秒")
    print(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

