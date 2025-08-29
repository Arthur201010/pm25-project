import pymysql
import requests

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
}
# 8/20 0:30:00

table_str = """ 
create table if not exists pm25(
id int auto_increment primary key,
site varchar(25),
county varchar(50),
pm25 int,
datacreationdate datetime,
itemunit varchar(20),
unique key site_time(site,datacreationdate)
)
"""
sqlstr = "insert ignore into pm25(site,county,pm25,datacreationdate,itemunit)\
      values(%s,%s,%s,%s,%s)"

url = "https://data.moenv.gov.tw/api/v2/aqx_p_02?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=datacreationdate%20desc&format=JSON"
conn, cursor = None, None


def open_db():
    global conn, cursor
    try:
        # conn = pymysql.connect(
        #     host="localhost", user="root", passwd="", port=3307, database="demo"
        # )
        conn = pymysql.connect(
            host="mysql-c87907a-arthur201010-4fba.j.aivencloud.com",
            user="avnadmin",
            password="AVNS_HWzrTchr2PZUlSOko5r",
            port=11977,
            database="defaultdb",
        )
        # print(conn)
        cursor = conn.cursor()
        # cursor.execute(table_str)
        # conn.commit()
        print("資料庫開啟成功!")
    except Exception as e:
        print(e)


def close_db():
    if conn is not None:
        conn.close()
        print("資料庫關閉結束!")


def get_opendata():  # 8/20 2:35:00
    values = None
    try:
        resp = requests.get(url, verify=False)
        if resp.status_code == 200:
            print("status_code=", resp.status_code)
            datas = resp.json()["records"]
            values = [
                list(data.values()) for data in datas if list(data.values())[2] != ""
            ]
        else:
            print(resp.status_code, "取得內容失敗")
    except Exception as e:
        print("錯誤", e)
    return values


def write_sql():
    try:
        values = get_opendata()
        if len(values) == 0:
            print("目前無資料")
            return
        size = cursor.executemany(sqlstr, values)
        conn.commit()
        print(f"寫入{size}筆資料成功")
    except Exception as e:
        print(e)


def get_from_mysql():  # 8/27 2:18:00  2:45:00
    try:
        open_db()
        sqlstr = "select max(datacreationdate) from pm25"
        cursor.execute(sqlstr)
        max_data = cursor.fetchone()
        print("最近時間:", max_data)

        sqlstr = (
            "select site,county,pm25,datacreationdate,"
            "itemunit from pm25 "
            "where datacreationdate=(select max(datacreationdate) from pm25);"
        )
        cursor.execute(sqlstr)
        # cursor.execute(sqlstr, (max_data,))
        datas = cursor.fetchall()
        # 去掉 id 當使用 (select * from pm25)時
        # datas = [data[1:0] for data in datas]

        return datas
    except Exception as e:
        print("雲端資料庫擷取失敗", e)
    finally:
        close_db()
    return None


# print(get_from_mysql())
# open_db()
# write_sql()
# close_db()
# print(get_opendata())
