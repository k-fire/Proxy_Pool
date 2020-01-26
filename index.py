from flask import session, make_response, Flask, request, render_template
#定时任务需要
from flask_apscheduler import APScheduler
#定时任务配置
import os,sys
#动态载入模块
import importlib
import threading
#数据库交互
import pymysql
import requests
import time
import random
from geetest import GeetestLib
import json

geetest_id = "4a58e5052ce112b467d960"
geetest_key = "76ebebb658b2b8096659d"

###定时任务层
class Config(object):
    JOBS=[
        {
            'id':'call_spider',
            'func':'__main__:call_spider',
            'args': None,
            'trigger':'cron',
            'hour':'5,17',
            'minute':'1,1',
        },
        {
            'id':'check_validity',
            'func':'__main__:check_validity',
            'args': None,
            'trigger':'interval',
            'minutes':5
        },
        {
            'id':'del_all',
            'func':'__main__:del_all',
            'args': None,
            'trigger':'cron',
            'hour':'4,16',
            'minute':'59,59',
        },
        {
            'id':'count',
            'func':'__main__:count',
            'args': None,
            'trigger':'interval',
            'minutes':1
        }
    ]

app = Flask(__name__)
#为实例化的flask引入配置
app.config.from_object(Config())



#多线程调用全部爬虫
def call_spider():
    #连接数据库
    try:
        db = pymysql.connect("localhost","root","root","proxy" )
        print("\033[1;36m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 正在调用爬虫\033[0m")
        for filename in os.listdir('./spider/'):
            if ".py" in filename:
                name = filename.replace(".py","")
                get_proxy = threading.Thread(target=dynamic_import,args=(name,db))
                get_proxy.start()
                get_proxy.join()
        db.close()
        print("\033[1;36m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 调用爬虫完成\033[0m")
    except:
        print("\033[1;31m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 数据库相关错误！ \033[0m")
#动态导入第三方爬虫
def dynamic_import(name,db):
    global spider_status_list
    id = name.split('_')[0]
    try:
        proxy_spider = importlib.import_module("spider.%s"%(name))
        data = proxy_spider.main()
        if data:
            import_database(data,db,"all_proxy")
            for spider_status in spider_status_list:
                if spider_status['name'] == '数据源%s'%id:
                    spider_status['status'] = 'Yes'
        else:
            for spider_status in spider_status_list:
                if spider_status['name'] == '数据源%s'%id:
                    spider_status['status'] = 'No'
    except:
        for spider_status in spider_status_list:
            if spider_status['name'] == '数据源%s'%id:
                spider_status['status'] = 'No'



#检查有效性(从all_proxy验证存入 valid_proxy)
def check_validity():
    try:
        db = pymysql.connect("localhost","root","root","proxy" )
        cursor = db.cursor()
        ######################
        all_proxy_list = []
        sql = "SELECT * FROM all_proxy"
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            all_proxy_list.append(row[1])
        ######################
        valid_proxy_list = []
        sql = "SELECT * FROM valid_proxy"
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            valid_proxy_list.append(row[1])
        cursor.close()
        ######################
        length = len(all_proxy_list)
        print("\033[1;36m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 正在验证%s个代理\033[0m"%(length))
        #多线程批量验证代理
        threads = []
        global valid_proxy
        valid_proxy = []
        for i in range(0,length,10):
            if i < length-10:
                thread = threading.Thread(target=test_access,args=(all_proxy_list,valid_proxy_list,i,i+10,db))
                threads.append(thread)
            else:
                thread = threading.Thread(target=test_access,args=(all_proxy_list,valid_proxy_list,i,length,db))
                threads.append(thread)
        for valid_task in threads:
            valid_task.start()
        for valid_task in threads:
            valid_task.join()
        import_database(valid_proxy,db,"valid_proxy")
        db.close()
        global updata_time
        updata_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("\033[1;36m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 验证结束\033[0m")
    except:
        print("\033[1;31m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 读取or验证代理有效性错误！ \033[0m")



def test_access(all_proxy_list,valid_proxy_list,start_id,finish_id,db):
    global valid_proxy
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0','Content-Type':'application/x-www-form-urlencoded'}
    for i in all_proxy_list[start_id:finish_id]:
        if not i in valid_proxy_list:
            proxies = { "http": "http://" + i, "https": "https://" + i, }
            try:
                res = requests.get(url='http://m.baidu.com/',headers=headers,proxies=proxies,timeout=60)
                if res.status_code == 200:
                    valid_proxy.append(i)
            except:
                pass



#导入数据库
def import_database(data,db,table_name):
    cursor = db.cursor()
    for i in data:
        #插入前判断该条是否存在
        sql = "SELECT * FROM %s WHERE proxy = '%s'"%(table_name,i)
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        if not results:
            sql = "INSERT INTO %s(proxy) VALUES ('%s')"%(table_name,i)
            cursor.execute(sql)
    db.commit()
    cursor.close()


#定时清空数据库
def del_all():
    try:
        print("\033[1;36m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 开始清空数据库\033[0m")
        db = pymysql.connect("localhost","root","root","proxy" )
        cursor = db.cursor()
        sql1 = "DELETE FROM all_proxy"
        sql2 = "DELETE FROM valid_proxy"
        cursor.execute(sql1)
        cursor.execute(sql2)
        db.commit()
        cursor.close()
        db.close()
        print("\033[1;36m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 数据库清空完毕\033[0m")
    except:
        print("\033[1;31m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 读取or验证代理有效性错误！ \033[0m")


def count():
    try:
        global all_count,valid_count
        db = pymysql.connect("localhost","root","root","proxy")
        cursor = db.cursor()
        sql = "SELECT count(*) FROM all_proxy"
        cursor.execute(sql)
        results = cursor.fetchall()
        all_count = results[0][0]
        #########################
        sql = "SELECT count(*) FROM valid_proxy"
        cursor.execute(sql)
        results = cursor.fetchall()
        valid_count = results[0][0]
        #########################
        db.close()
    except:
        print("\033[1;31m"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 数量刷新失败！ \033[0m")


def random_get_proxy(count):
    try:
        global valid_count
        db = pymysql.connect("localhost","root","root","proxy")
        cursor = db.cursor()
        sql = "SELECT count(*) FROM valid_proxy"
        cursor.execute(sql)
        results = cursor.fetchall()
        valid_count = results[0][0]
        #############################
        sql = "SELECT * FROM valid_proxy"
        cursor.execute(sql)
        proxy_tuple = cursor.fetchall()
        proxy_list = set()
        if count <= valid_count:
            while True:
                id = random.randint(0,valid_count-1)
                proxy = proxy_tuple[id][1]
                proxy_list.add(proxy)
                if len(proxy_list) == count:
                    break
            cursor.close()
            db.close()
            return proxy_list
        else:
            proxy_list = {'超过最大数量'}
            return proxy_list
    except:
        return proxy_list


###视图层

@app.route('/',methods=['GET','POST'])
def index():
    global updata_time,all_count,valid_count,spider_status_list
    if request.method == 'POST':
        gt = GeetestLib(geetest_id, geetest_key)
        challenge = request.form[gt.FN_CHALLENGE]
        validate = request.form[gt.FN_VALIDATE]
        seccode = request.form[gt.FN_SECCODE]
        status = session[gt.GT_STATUS_SESSION_KEY]
        user_id = session["user_id"]
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)
        if result:
            try:
                count = int(request.values.get('count'))
                if 1 <= count <= 100:
                    proxy_list = random_get_proxy(count)
                    proxy_list = '\n'.join(proxy_list)
                    return render_template('index.html',all_count=all_count,valid_count=valid_count,updata_time=updata_time,proxy_list=proxy_list,spider_status_list=spider_status_list)
                else:
                    return render_template('index.html',all_count=all_count,valid_count=valid_count,updata_time=updata_time,proxy_list={'请输入0~100的整数'},spider_status_list=spider_status_list)
            except:
                return render_template('index.html',all_count=all_count,valid_count=valid_count,updata_time=updata_time,proxy_list={'请输入0~100的整数'},spider_status_list=spider_status_list)
        else:
            return render_template('index.html',all_count=all_count,valid_count=valid_count,updata_time=updata_time,proxy_list={'请先完成滑动验证！'},spider_status_list=spider_status_list)

    else:
        return render_template('index.html',all_count=all_count,valid_count=valid_count,updata_time=updata_time,spider_status_list=spider_status_list)



@app.route('/about_me/')
def about_me():
    return render_template('about_me.html')

####################以下为滑动验证
@app.route('/captcha', methods=["GET"])
def get_captcha():
    user_id = 'proxy'
    gt = GeetestLib(geetest_id, geetest_key)
    status = gt.pre_process(user_id)
    session[gt.GT_STATUS_SESSION_KEY] = status
    session["user_id"] = user_id
    response_str = gt.get_response_str()
    return response_str



if __name__ == '__main__':
    os.system("")
    global updata_time,all_count,valid_count,spider_status_list
    updata_time,all_count,valid_count = '无','无','无'
    spider_status_list = []
    print("[@]开始初始化.")
    for filename in os.listdir('./spider/'):
        if ".py" in filename:
            spider_status = {}
            id = filename.split('_')[0]
            spider_status['name'] = '数据源%s'%id
            spider_status['status'] = 'None'
            spider_status_list.append(spider_status)
    print("[@]检测到%s个数据源"%(len(spider_status_list)))
    # 实例化APScheduler
    scheduler=APScheduler()
    # 把任务列表放进flask
    scheduler.init_app(app)
    # 启动任务列表
    scheduler.start()
    #!!!debug开启会导致定时任务双倍进行
    try:
        if sys.argv[1] == "reload":
            print("[@]重新初始化中...")
            del_all()
            call_spider()
    except:
        pass
    count()
    app.secret_key = 'i-like-proxy'
    app.run(host="0.0.0.0", port=6)
