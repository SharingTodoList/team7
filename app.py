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
def main():
    return render_template("login.html")


@app.route('/register', methods=['POST'])
def api_register():
    id_receive = request.form['username_give']
    pw_receive = request.form['password_give']
    nickname_receive = request.form['nickname_give']

    # print(id_receive)

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    # print(id_receive)
    # print(pw_hash)
    # print(pw_receive)
    # print(nickname_receive)
    db.member.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success'})


@app.route('/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    # print(username_receive)
    exists = bool(db.member.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.member.find_one({'id': username_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }

        print(payload)
        print(SECRET_KEY)
        print(jwt.encode(payload, SECRET_KEY, algorithm='HS256'))

        # token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # 강의에서는 위의코드이나 https://fusiondeveloper.tistory.com/31 에서는 에러가 날때
        # 파이썬 버전에 따라 다른데 .decode('utf-8')을 지워줘도 된다고 한다.
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/base')
def base():
    return render_template('base.html')


@app.route('/todolist')
def todolist():
    return render_template('todolist.html')

@app.route('/mypage')
def mypage():
    return render_template('mypage.html')


@app.route("/bucket", methods=["POST"])
def bucket_post():
    bucket_receive = request.form['bucket_give']
    time_receive=request.form['time_give']
    tag_receive=request.form['tag_give']
    
    bucket_list=list(db.todo.find({}, {'_id':False}))
    count= len(bucket_list)+1

    doc = {
        'seq':count,
        'date':datetime.today().strftime("%Y-%m-%d"),
        'time':time_receive,
        'detail':bucket_receive,
        'tag':tag_receive,
        
        'status':0,
        
    }

    db.todo.insert_one(doc)
    return jsonify({'msg': '등록완료!'})


@app.route("/bucket/done", methods=["POST"])
def bucket_done():
    seq_receive = request.form['seq_give']
    db.todo.update_one({'seq': int(seq_receive)}, {'$set': {'status': 1}})
    return jsonify({'msg': '버킷완료!'})

@app.route("/bucket/back",methods=["POST"])
def bucket_back():
    seq_receive = request.form['seq_give']
    db.todo.update_one({'seq': int(seq_receive)}, {'$set': {'status': 0}})
    return jsonify({'msg': '버킷취소!'})

@app.route("/bucket/delete",methods=["POST"])
def bucket_delete():
    seq_receive = request.form['seq_give']
    db.todo.delete_one({'seq': int(seq_receive)})
    return jsonify({'msg': '버킷삭제!'})


@app.route("/bucket", methods=["GET"])
def bucket_get():
    bucket_list = list(db.todo.find({}, {'_id': False}))
    
    return jsonify({'buckets': bucket_list})






@app.route('/logout')
def logout():
    return render_template("logout.html")


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)


