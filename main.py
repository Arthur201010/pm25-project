from flask import Flask, render_template, Response
from datetime import datetime
from pm25 import get_from_mysql, write_to_mysql, get_avg_pm25_mysql, get_pm25_by_county
import json

books = {
    1: {
        "name": "Python book",
        "price": 299,
        "image_url": "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/CN1/136/11/CN11361197.jpg&v=58096f9ck&w=348&h=348",
    },
    2: {
        "name": "Java book",
        "price": 399,
        "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/087/31/0010873110.jpg&v=5f7c475bk&w=348&h=348",
    },
    3: {
        "name": "C# book",
        "price": 499,
        "image_url": "https://im1.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/036/04/0010360466.jpg&v=62d695bak&w=348&h=348",
    },
}  # 8/22 2:10:00

app = Flask(__name__)


@app.route("/county-pm25/<county>")
def get_county_pm25(county):  # 9/3 0:40:00
    result = get_pm25_by_county(county)

    if len(result) == 0:
        return Response(
            json.dumps(
                {"result": "取得資料失敗", "message": f"無此({county})縣市資料"},
                ensure_ascii=False,
            )
        )
    site = [r[0] for r in result]
    pm25 = [float(r[1]) for r in result]
    count = len(site)
    datetime = result[0][2].strftime("%Y-%m-%d %H:%M:%S")
    print(datetime)

    return Response(
        json.dumps(
            {
                "county": county,
                "site": site,
                "pm25": pm25,
                "count": count,
                "datetime": datetime,
            },
            ensure_ascii=False,
        ),
        mimetype="application/json",
    )


@app.route("/avg-pm25")
def get_avg_pm25():  # 8/29 2:05:00
    result = get_avg_pm25_mysql()
    county = [r[0] for r in result]
    pm25 = [float(r[1]) for r in result]
    return Response(
        json.dumps({"county": county, "pm25": pm25}, ensure_ascii=False),
        mimetype="application/json",
    )


@app.route("/update-db")
def update_db():
    result = write_to_mysql()

    return json.dumps(result, ensure_ascii=False)


@app.route("/")
@app.route("/pm25")
def get_pm25():
    print("雲端資料下載.....")
    values, countys = get_from_mysql()
    # print(values)
    columns = ["站點名稱", "縣市", "PM2.5", "更新時間", "單位"]
    return render_template("pm25.html", columns=columns, values=values, countys=countys)


@app.route("/bmi/height=<h>&weight=<w>")
def get_bmi(h, w):
    bmi = round(eval(w) / (eval(h) / 100) ** 2, 2)
    return f"<h1>身高:{h} 體重:{w} <br>BMI:{bmi}</h1>"


@app.route("/books")
@app.route("/books/id=<int:id>")
def get_books(id=None):  # 8/22 1:00:00
    try:
        # books = {1: "Python book", 2: "Java book", 3: "Flask book"}
        if id == None:
            return render_template("books.html", books=books)
        return books[id]
    except Exception as e:
        return f"編號錯誤:{e}"


@app.route("/nowtime")
def now_time():
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(time)
    return time


def index():
    time = now_time()
    return render_template("index.html", t=time, name="Hans")


if __name__ == "__main__":
    app.run(debug=False)
