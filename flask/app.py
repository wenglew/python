from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
import utils
import string
from jieba.analyse import extract_tags
# 创建一个flask对象
app = Flask(__name__)

# 通过匹配路由去匹配要执行的代码
@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/hello')
def hello():
    return 'Hello Flask!!'

@app.route('/login')
def login():
    return '''
    <form action="/show">
        username:<input name="username"><br>
        password:<input name="password"><br>
        <input type="submit">
    </form>
    '''

@app.route('/show')
def show():
    # 获取提交过来的用户名和密码
    username = request.values.get("username")
    password = request.values.get("password")
    print('username'+username+"password"+password)
    return f'username:{username}<br>password:{password}'

@app.route('/flask')
def flask():
    return render_template("test.html")

@app.route('/ajax',methods=["get","post"])
def ajax():
    name = request.values.get("name")
    age = request.values.get("age")
    print(name+":"+age)
    return "Successful"

# 获取当前系统时间
@app.route('/get_sys_time',methods=['get','post'])
def get_sys_time():
    dt = utils.get_sys_time()
    return dt


@app.route('/get_center1',methods=['get','post'])
def get_center1():
    # 获取数据库中我想要的数据
    res = utils.get_center1()
    # 把数据转换为json字符串
    return jsonify({"confirm":str(res[0]),"suspect":str(res[1]),"heal":str(res[2]),"dead":str(res[3])})

@app.route('/get_center2',methods=['get','post'])
def get_center2():
    datas = []
    res = utils.get_center2()
    for item in res:
        datas.append({"name":item[0],"value":str(item[1])})
    return jsonify({"data":datas})


@app.route('/get_left1',methods=['get','post'])
def get_left1():
    res = utils.get_left1()
    day,confirm,suspect,heal,dead = [],[],[],[],[]

    for tup in res:
        day.append(tup[0].strftime("%m-%d"))
        confirm.append(tup[1])
        suspect.append(tup[2])
        heal.append(tup[3])
        dead.append(tup[4])
    return jsonify({"day":day,"confirm":confirm,
                    "suspect":suspect,"heal":heal,
                    "dead":dead})

@app.route('/get_left2',methods=['get','post'])
def get_left2():
    res=utils.get_left2()
    day,confirm,suspect=[],[],[]

    for item in res:
        day.append(item[0].strftime("%m-%d"))
        confirm.append(item[1])
        suspect.append(item[2])

    return jsonify({"day":day,
                    "confirm":confirm,
                    "suspect":suspect})

@app.route('/get_right1',methods=['get','post'])
def get_right1():
    res=utils.get_right1()
    city,confirm=[],[]

    for item in res:
        city.append(item[0])
        confirm.append(str(item[1]))

    return jsonify({"city": city,"confirm":confirm})

@app.route('/get_right2',methods=['get','post'])
def get_right2():
    res=utils.get_right2()
    content = []
    for item in res:
        str=item[0].rstrip(string.digits)
        num=item[0][len(str):]
        str=extract_tags(str)
        for data in str:
            if not data.isdigit():
                content.append({"name":data,"value":num})

    return jsonify({"data":content})



if __name__ == '__main__':
    app.run()
