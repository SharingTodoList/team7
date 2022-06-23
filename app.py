import pymongo
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@sparta.xob7d.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta

SECRET_KEY = 'SPARTA'

import jwt
import datetime
import hashlib
from datetime import datetime, timedelta


@app.route('/')
def login():
    return render_template("login.html")


# 가입
@app.route('/register', methods=['POST'])
def api_register():
    id_receive = request.form['username_give']
    pw_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    db.member.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


    # 중복체크


@app.route('/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    print(username_receive)
    exists = bool(db.member.find_one({"id": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/check_nick', methods=['POST'])
def check_nick():
    nickname_receive = request.form['nickname_give']
    print(nickname_receive)
    exists = bool(db.member.find_one({"nick": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 로그인
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    print(username_receive)
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.member.find_one({'id': username_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }

        # print(payload)
        # print(SECRET_KEY)
        # print(jwt.encode(payload, SECRET_KEY, algorithm='HS256'))

        # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # 강의에서는 위의코드이나 https://fusiondeveloper.tistory.com/31 에서는 에러가 날때
        # 파이썬 버전에 따라 다른데 .decode('utf-8')을 지워줘도 된다고 한다.
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 지난 todolist
@app.route("/listExTodo")
def listExTodo():
    return render_template("listExTodo.html")


# 지난 todolist
@app.route('/showOldTodo', methods=['POST'])
def listExTodo_list():
    # id_receive = request.form['id_give']
    date_receive = request.form['date_give']
    # print(id_receive)
    print(date_receive)

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(payload['id'])

    # todo = list(db.todo.find({{"id":"park"},}, {'_id':False}))
    todo = list(db.todo.find({"id": payload['id'], 'date': date_receive}, {'_id': False}).sort(
        [("time", 1), ("detail", pymongo.DESCENDING)]))
    print(todo)
    return jsonify({'todo': todo})


# 나의 즐겨찾기
@app.route("/myfavorites")
def listMyfavorites():

    return render_template("myfavorites.html")


# 즐겨찾기조회
@app.route('/showMyFavorites', methods=['POST'])
def listMyfavorites_list():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    print(payload['id'])

    favorites = list(db.favorites.find({"id": payload['id']}, {'_id':False}).sort([("addperson",1)]))
    print(favorites)
    return jsonify({'favorites': favorites})


@app.route('/basic')
def basic():
    return render_template("basic.html")


@app.route('/main')
def main():
    return render_template("main.html")


@app.route('/logout')
def logout():
    return render_template("logout.html")

@app.route('/memberpage')
def memberpage():
    return render_template('memberpage.html')


@app.route('/todolist')
def todolist():
    return render_template('todolist.html')

@app.route('/make_member')
def make_member():
    return render_template('make_member.html')



@app.route("/bucket", methods=["POST"])
def bucket_post():
    bucket_receive = request.form['bucket_give']
    time_receive = request.form['time_give']
    # tag_receive = request.form['tag_give']
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    print(payload['id'])
    bucket_list = list(db.todo.find({}, {'_id': False}))
    count = len(bucket_list) + 1

    doc = {
        'id' : payload['id'],
        'seq': count,
        'date': datetime.today().strftime("%Y-%m-%d"),
        'time': time_receive,
        'detail': bucket_receive,
        # 'tag': tag_receive,

        'status': 0,

    }

    db.todo.insert_one(doc)
    return jsonify({'msg': '등록완료!'})


@app.route("/bucket/done", methods=["POST"])
def bucket_done():
    seq_receive = request.form['seq_give']
    db.todo.update_one({'seq': int(seq_receive)}, {'$set': {'status': 1}})
    return jsonify({'msg': '버킷완료!'})


@app.route("/bucket/back", methods=["POST"])
def bucket_back():
    seq_receive = request.form['seq_give']
    db.todo.update_one({'seq': int(seq_receive)}, {'$set': {'status': 0}})
    return jsonify({'msg': '버킷취소!'})


@app.route("/bucket/delete", methods=["POST"])
def bucket_delete():
    seq_receive = request.form['seq_give']
    db.todo.delete_one({'seq': int(seq_receive)})
    return jsonify({'msg': '버킷삭제!'})


@app.route("/bucketlist", methods=["POST"])
def bucketlist():

    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    print(payload['id'])
    id = payload['id']
    # bucket_list = list(db.todo.find({{"id": "park"}, }, {'_id': False}))
    bucket_list = list(db.todo.find({ }, {'_id': False}))
    # bucket_list = list(db.todo.find({{"id": id} }, {'_id': False})) 그사람이 적은것만 나오게 수정해야됨

    return jsonify({'buckets': bucket_list})


# 메인 조회
@app.route("/get_posts", methods=['POST'])
def get_posts():
    token_receive = request.cookies.get('mytoken')
    date_receive = request.form['date_give']
    print(date_receive)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        posts = list(db.todo.find({"date": date_receive}).sort("date", -1).limit(20))
        # posts = list(db.todo.find({{}, }, {'_id': False}).sort("date", -1).limit(20))

        for post in posts:
            post["_id"] = str(post["_id"])
            post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
            post["heart_by_me"] = bool(
                db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
            print(posts)
        return jsonify({"result": "success", "msg": "포스팅을 가져왔습니다.", "posts": posts})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.likes.find_one({"username": payload["nick"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info("nick"),
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))

#멤버페이지
@app.route('/memberpage', methods=["GET"])
def member():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    memberlist = list(db.todo.find({'id': payload['id']}, {'_id': False}))
    user_info = list(db.member.find({'id': payload['id']}, {'_id': False}))

    return jsonify({'memberlist': memberlist, 'user_info': user_info})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
