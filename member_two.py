import mysql.connector
import datetime
from datetime import date
from priceList_two import cal_Price_two, get_hour

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="car_trmp"
)


def member_two():
    mycursor_member = mydb.cursor()
    mycursor_member.execute(
        "select member.expiry_date, member.type, member.license_plate FROM member INNER JOIN test_log ON member.license_plate = test_log.license_plate WHERE test_log.gate = 1 ORDER BY date_out DESC, time_out DESC LIMIT 1")
    myresult = mycursor_member.fetchall()

    if len(myresult) == 0:
        return cal_Price_two()

    for (expiry_date, type, license_plate) in myresult:
        if type == 'member':
            expiry_year = expiry_date.year
            expiry_month = expiry_date.month
            expiry_day = expiry_date.day

            now = datetime.datetime.now()

            now_year = now.year
            now_month = now.month
            now_day = now.day

            expiry_date = date(expiry_year, expiry_month, expiry_day)
            now_date = date(now_year, now_month, now_day)
            expiry = expiry_date - now_date
            expiry = expiry.days
            expiration = 'หมดอายุ'
            still_expire = '0'
            # เช็ค แค่หมดอายุรึยัง ยังไม่ได้เช็คเพคเกจ
            vat = 0
            excluding_vat = 0

            expiry_1 = still_expire if expiry > 0 else cal_Price_two()
            return expiry_1 ,vat,excluding_vat

        elif type == 'VIP':
            price = "0"
            return price,vat,excluding_vat
    return 'error'

# print(member_two())
