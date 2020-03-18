"""
1.热搜入库
2.历史入库
3.详细入库
"""
from selenium.webdriver import Chrome
import time
import utils
import requests
from bs4 import BeautifulSoup
import json
#爬取热搜
def get_hotdata():
    url="https://voice.baidu.com/act/newpneumonia/newpneumonia/?from=osari_pc_1#tab2"

    brower=Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
    brower.get(url)
    html=brower.page_source

    #存放爬到的数据
    hotdata=[]






#模拟浏览器点击
    btn=brower.find_element_by_xpath('//*[@id="ptab-2"]/div[1]/div/p/a')
    btn.click()
    time.sleep(1)

    btn=brower.find_element_by_xpath('//*[@id="ptab-0"]/div/div[2]/section/div')
    btn.click()
    time.sleep(1)


#获取数据
    content=brower.find_elements_by_xpath('//*[@id="ptab-0"]/div/div[2]/section/a/div/span[2]')
    print(len(content))
    for item in content:
        print(item.text)
        hotdata.append(item.text)

    return hotdata

#热搜数据入库
def insert_hotdata():
    #获取数据库连接
    conn,cursor=utils.get_conn()
    sql='insert into hotsearch(dt,content) values (%s,%s)'
    datas=get_hotdata()
    #获取当前时间戳
    dt=time.strftime("%Y-%m-%d %X")
    for item in datas:
        cursor.execute(sql,(dt,item))
        conn.commit()


    print('数据插入成功')
    utils.close(conn,cursor)

#获取历史数据
def get_history():
    history={}
    url="https://view.inews.qq.com/g2/getOnsInfo?name=disease_other"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
    }
    resp=requests.get(url,headers)
    jsondata=resp.text
    #把json字符串转换为字典
    datas=json.loads(jsondata)


    data=json.loads(datas['data'])

    for day in data['chinaDayList']:
        #时间
        dt='2020.'+day['date']
        tup = time.strptime(dt, "%Y.%m.%d")
        dt = time.strftime("%Y-%m-%d %X", tup)

        #确诊
        confirm=day['confirm']
        #疑似
        suspect=day['suspect']
        #出院
        heal=day['heal']
        #死亡
        dead=day['dead']

        history[dt]={"confirm":confirm,"suspect":suspect,"heal":heal,"dead":dead}



    for dayadd in data['chinaDayAddList']:
        dt = '2020.' + dayadd['date']
        tup = time.strptime(dt, "%Y.%m.%d")
        dt = time.strftime("%Y-%m-%d %X", tup)
        confirm_add = dayadd['confirm']
        suspect_add = dayadd["suspect"]
        heal_add=dayadd["heal"]
        dead_add=dayadd["dead"]

        history[dt].update({"confirm_add":confirm_add,
                            "suspect_add":suspect_add,
                            "heal_add":heal_add,
                            "dead_add":dead_add})

        print(history)
        for item in history.keys():
            print(item)
            print(history[item])
    return history

def insert_history():
    conn,cursor=utils.get_conn()
    history=get_history()
    sql='insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    for k,v in history.items():
        cursor.execute(sql, [k, v.get("confirm"), v.get("confirm_add"),
                             v.get("suspect"), v.get("suspect_add"),
                             v.get("heal"), v.get("heal_add"),
                             v.get("dead"), v.get("dead_add")])
        conn.commit()

    print("数据插入成功")
    utils.close(conn,cursor)

# def update_history():
#     conn, cursor = utils.get_conn()
#     history = get_history()
#     print(f"{time.asctime()}开始更新历史数据")
#     sql="insert into history values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
#     sql_query="select confirm from history where ds=%s"
#     for k,v in history.items():
#         if not cursor.execute(sql_query,k):
#             cursor.execute(sql,[k,v.get("confirm"),v.get("confirm_add"),v.get("suspect"),
#                                 v.get("suspect_add"),v.get("heal"),v.get("heal_add"),
#                                 v.get("dead"),v.get("dead_add")])
#         conn.commit()
#     print(f"{time.asctime()}历史数据更新完毕")
#     utils.close(conn,cursor)

def get_details():
    #列表
    details = []
    url = "https://view.inews.qq.com/g2/getOnsInfo?name=disease_h5"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36"
    }
    resp = requests.get(url,headers)
    jsondata=resp.text
    datas=json.loads(jsondata)
    data=json.loads(datas['data'])
    # for item in data.keys():
    #     print(item)
    #     print(data[item])
    #更新时间
    updatetime=data['lastUpdateTime']
    #中国
    contry=data['areaTree'][0]
    #省份
    provinces=contry['children']
    for province in provinces:
        pro_name=province['name']
        for city in province['children']:
            #城市名字
            city_name=city['name']
            confirm=city['total']['confirm']
            #新增确诊
            confirm_add=city['today']['confirm']
            heal=city['total']['heal']
            dead=city['total']['dead']
            #print(city_name)
            details.append([updatetime,pro_name,city_name,confirm,confirm_add,heal,dead])

    print(details)
    return details

#details入库
def insert_details():
    conn,cursor = utils.get_conn()
    details = get_details()
    # 执行插入数据
    sql = 'insert into details(update_time,province,city,confirm,confirm_add,heal,dead) values(%s,%s,%s,%s,%s,%s,%s)'
    # 查询数据库中的数据是否需要更新，如果需要更新就更新，不需要就提示
    sql_query = 'select %s=(select update_time from details order by id desc limit 1)'
    cursor.execute(sql_query,details[0][0])
    if not cursor.fetchone()[0]:
        print("开始更新数据！")
        for item in details:
            cursor.execute(sql,item)
            conn.commit()

        print("数据更新成功！")
    else:
        print("已经是最新数据，不需要更新！")

def update_details():
    conn, cursor = utils.get_conn()
    details = get_details()
    sql="insert into details(update_time,province,city,confirm,confirm_add,heal,dead) values(%s,%s,%s,%s,%s,%s,%s)"
    sql_query='select %s=(select update_time from details order by id desc limit 1)'
    cursor.execute(sql_query,details[0][0])
    if not cursor.fetchone()[0]:
        print(f"{time.asctime()}开始更新最新数据")
        for item in details:
            cursor.execute(sql,item)
        conn.commit()
        print(f"{time.asctime()}更新最新数据完毕")
    else:
        print(f"{time.asctime()}已是最新数据")

    utils.close(conn,cursor)


if __name__=="__main__":
    #get_hotdata()
    #insert_hotdata()
    #get_history()
    insert_history()
    #update_history()
    #get_details()
    #insert_details()
    #update_details()