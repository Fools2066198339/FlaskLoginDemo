import base64
import hashlib
import os
import random
import string
import time

import face_recognition
import pymysql
from flask import Flask, request, jsonify

app = Flask(__name__)
# 连接数据库，返回一个数据库连接对象，用connection变量来储存
connection = pymysql.connect(host="127.0.0.1", port=3306, user="root", passwd="123456", db="face_login")
cursor = connection.cursor()


@app.route('/')
def index():
    return '''
                <script>
                    window.location.href="/static/index.html";
                </script>'''


@app.route("/register", methods=["POST"])
def register():
    # 获取到前端表单发送的用户名，密码和文件
    username = request.form.get("username")
    password = request.form.get("password")
    face_img = request.files.get("face_img")

    # 根据用户名生成人脸识别基准文件的新文件名
    face_img_name = username + os.path.splitext(face_img.filename)[-1]
    # 将文件保存在项目的FaceBaseImg文件夹下,使用绝对路径保存
    face_img_abspath = os.path.dirname(os.path.abspath(__file__)) + "/FaceBaseImg/" + face_img_name
    face_img.save(face_img_abspath)

    # 调用face_recognition库来检测用户上传图片是否有人脸特征，如果有人脸，保存用户信息到数据库，保存人脸识别基准图片
    face_recognition_img = face_recognition.load_image_file(face_img)
    print(face_recognition_img)
    face_recognition_img_location = face_recognition.face_locations(face_recognition_img)
    print(face_recognition_img_location)
    if face_recognition_img_location:
        # 创建一个16位的随机字符串作为盐值
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 16))
        # 将密码明文和盐值进行拼接
        passwordAndSalt = password + salt
        # 调用sha256函数来将拼接好的字符串转换位hash值
        hash_password = hashlib.sha256(passwordAndSalt.encode()).hexdigest()
        sql = "insert into user values (null,'%s','%s','%s','%s')" % (username, hash_password, salt, face_img_name)
        cursor.execute(sql)
        connection.commit()
        # 返回一个字符串，弹窗，并使用js跳转到新页面
        return '''
                <script>
                    alert('恭喜您，注册成功')
                    window.location.href="/static/index.html";
                </script>'''
    else:
        return '''
                <script>
                    alert('注册失败，请重新输入！')
                    window.location.href="/static/register.html";
                </script>'''


@app.route("/passwordLogin", methods=["POST"])
def passwordLogin():
    username = request.form.get("username")
    password = request.form.get("password")

    sql = "select * from user where username = '%s' " % username
    cursor.execute(sql)
    user = cursor.fetchone()
    if user:
        # 从数据库里查找到的用户密码
        selected_password = user[2]
        salt = user[3]

        hash_password = hashlib.sha256((password + salt).encode()).hexdigest()
        if selected_password == hash_password:
            return '''
                <script>
                    alert('恭喜您，登录成功')
                    window.location.href="/static/user-list.html";
                </script>
            '''
    else:
        return '''
                <script>
                    alert('登录失败，密码错误或者没有该用户')
                    window.location.href="/static/register.html";
                </script>'''


# 人脸识别登陆的路由
@app.route("/faceLogin", methods=["POST"])
def face_login():
    username = request.form.get("username")
    face_login_img = request.form.get("face_login_img")[22:]
    print(face_login_img)
    sql = "select * from user where username = '%s'" % username
    cursor.execute(sql)
    user = cursor.fetchone()
    # 根据索引获取基准图片的路径
    face_base_img_filename = user[4]
    # 构建人脸识别对比图像的文件名和路径
    face_login_img_filename = username + time.strftime("%Y %m %d %H %M %S", time.localtime()) + ".png"
    face_base_img_path = os.path.dirname(os.path.abspath(__file__)) + "/FaceBaseImg/" + face_base_img_filename
    face_login_img_path = os.path.dirname(os.path.abspath(__file__)) + "/FaceLoginImg/" + face_login_img_filename

    with open(face_login_img_path, "wb") as f:
        f.write(base64.b64decode(face_login_img))

    # 根据数据库里获取得到的人脸识别基准图像的路径来加载图片
    face_recognition_base_img = face_recognition.load_image_file(face_base_img_path)
    face_recognition_login_img = face_recognition.load_image_file(face_login_img_path)
    if not face_recognition.face_locations(face_recognition_login_img):
        return "0"
    # 调用face_recognition库将图片转化为特征值
    face_recognition_base_img_code = face_recognition.face_encodings(face_recognition_base_img)
    face_recognition_login_img_code = face_recognition.face_encodings(face_recognition_login_img)

    compare_result = face_recognition.compare_faces([face_recognition_base_img_code[0]],
                                                    face_recognition_login_img_code[0], 0.49)
    if compare_result[0]:
        return "1"
    else:
        return "0"


# 验证用户名，如果没有该用户，请重新输入，如果存在该用户，则跳转到人脸识别页面
@app.route("/verifyUsername", methods=["POST"])
def verifyUsername():
    username = request.form.get("username")
    sql = "select * from user where username = '%s'" % username
    cursor.execute(sql)
    user = cursor.fetchone()
    if user:
        # 如果找到了用户，跳转到faceLogin页面进行人脸识别，同时带上username这个参数
        return "<script> window.location.href='/static/faceLogin.html?username=%s' </script>" % username
    else:
        return '''<script>
                    alert('没有该用户！请重新输入！')
                    window.location.href="/static/verifyUsername.html";
                </script>'''


# 用来向前端返回用户列表
@app.route("/requestUser", methods=["GET"])
def listUser():
    sql = "select * from user "
    cursor.execute(sql)
    users = cursor.fetchall()

    return jsonify(users)


# 用来删除用户
@app.route("/deleteUser", methods=["GET"])
def deleteUser():
    user_id = request.args.get("id")
    sql = "delete from user where id = '%s'" % user_id
    cursor.execute(sql)
    connection.commit()

    return "<script>alert('删除成功');window.location.href='/static/user-list.html'</script> "


# 通过用户名用户
@app.route("/userEdit", methods=["GET"])
def userSearch():
    user_name = request.args.get("usr")
    print(user_name)
    sql = "select * from user where username ='%s'" % user_name
    cursor.execute(sql)
    user = cursor.fetchall()
    print(jsonify(user))
    return jsonify(user)

# 修改用户信息
@app.route("/userSet",methods=["POST"])
def userSet():
    username = request.form.get("username")
    password = request.form.get("pass")
    print(username,password)
    if username and password:
        sql = "update user set username='%s',password='%s' " % (username,password)
        cursor.execute(sql)
        connection.commit()
        return '''<script>
                    alert('用户修改成功！')
                    window.location.href="/static/user-list.html";
                </script>'''
    else:
        return  '''<script>
                    alert('用户修改失败！')
                    window.location.href="/static/user-list.html";
                </script>'''

if __name__ == '__main__':
    app.run()
