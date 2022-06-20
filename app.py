from flask import Flask, render_template

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:sparta@sparta.xob7d.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta


@app.route('/')
def main():
    return render_template("base.html")

@app.route('/mypage')
def mypage():
    return render_template("mypage.html")

@app.route('/logout')
def logout():
    return render_template("logout.html")



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)