import time
import pymysql
# 获取系统时间
def get_sys_time():
    # 当前时间
    dt = time.strftime("%Y-%m-%d %X")
    return dt


# 获取数据库连接
def get_conn():
    conn = pymysql.connect(
        host='49.234.76.76',
        user='itoffice',password='itoffice',
        database='cov',charset='utf8'
    )
    cursor = conn.cursor()
    return conn,cursor
# 释放资源
def close(conn,cursor):
    cursor.close()
    conn.close()

# 查询数据库数据
def query(sql,*args):
    conn,cursor = get_conn()
    cursor.execute(sql,args)
    res = cursor.fetchall()
    return res

# 获取center1
def get_center1():
    #查询详情表
    sql = "select sum(confirm)," \
          "(select suspect from history order by ds desc limit 1)," \
          "sum(heal)," \
          "sum(dead) " \
          "from details " \
          "where update_time=(select update_time from details order by update_time desc limit 1) "
    res = query(sql)
    # print(res)
    return res[0]


# 获取center2
def get_center2():
    sql = "select province,sum(confirm) from details " \
          "where update_time=(select update_time from details " \
          "order by update_time desc limit 1) " \
          "group by province"
    res = query(sql)
    print(res)
    return res

# 获取left1
def get_left1():
    sql = "select ds,confirm,suspect,heal,dead from history"
    res = query(sql)
    print(res)
    return res


if __name__ == "__main__":
    # get_center1()
    # get_center2()

    get_left1()

