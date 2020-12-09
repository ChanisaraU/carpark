import mysql.connector
import datetime
import math
from datetime import datetime, timedelta, date, time

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="car_trmp"
)

def get_hour(delta):
    return delta.seconds/3600


def cal_Price():
    mycursor = mydb.cursor()
    # mycursor.execute("select date_in,time_in,date_out, TIME_FORMAT(time_out, '%T') as time_out from parking_log ORDER BY date_out DESC, time_out DESC LIMIT 1")
    mycursor.execute(
        "select date_in,time_in,date_out, TIME_FORMAT(time_out, '%T') as time_out from test_log where id = 0")
    myresult = mycursor.fetchall()
    if not myresult[0][1]:
        y = list(myresult[0])
        y[1] = '00:00:00'
        myresult[0] = tuple(y)
        # print(myresult)

    if not myresult[0][3]:
        y = list(myresult[0])
        y[3] = '00:00:00'
        myresult[0] = tuple(y)
        # print(myresult)

    for (date_in, time_in, date_out, time_out) in myresult:
        checkHourIn = str(time_in).split(":")
        if len(checkHourIn[0])== 1 :
            checkHourIn[0]= "0"+checkHourIn[0]
            time_in = checkHourIn[0]+":"+checkHourIn[1]+":"+checkHourIn[2]

        checkHourOut = str(time_out).split(":")
        if len(checkHourOut[0])== 1 :
            checkHourOut[0]= "0"+checkHourOut[0]
            time_out = checkHourOut[0]+":"+checkHourOut[1]+":"+checkHourOut[2]

        if date_in and time_in and date_out and time_out:
            date_in = datetime.fromisoformat(
                "{0} {1}".format(date_in, time_in))
            date_out = datetime.fromisoformat(
                "{0} {1}".format(date_out, time_out))

            price = 0
            tmp = None
            last = False
            while(date_in < date_out and not last):
                tmp = date_in
                if date_in.hour < 4:
                    first4 = date_in.replace(
                        hour=4, minute=0, second=0, microsecond=0)
                    first_delta = first4 - date_in if (not last) and (
                        date_in.day != date_out.day or date_out.hour >= 4) else date_out - date_in
                    first_delta_hour = math.ceil(get_hour(first_delta))
                    if first4 <= date_out or last or date_in.day == date_out.day:
                        price += first_delta_hour * 20

                    date_in = first4
                else:
                    first_mid = date_in.replace(
                        hour=0, minute=0, second=0, microsecond=0)
                    first_mid += timedelta(days=1)

                    first_delta = first_mid - \
                        date_in if (not last) and (date_in.day != date_out.day) else date_out - date_in
                    first_delta_hour = get_hour(first_delta)
                    if first_mid <= date_out or last or date_in.day == date_out.day:
                        if first_delta_hour > 4:
                            price += 60
                        elif first_delta_hour > 0.5:
                            price += 20
                    date_in = first_mid

                if date_in >= date_out and not last:
                    last = True
            cal_amount(price)  # ค่าเงินจอดรถ
            
        # print(price)  # ค่าเงินจอดรถที่มีค่าส่วนลด กับค่าปรับแล้ว
        vat = price * 0.07
        total_amount = price + vat
        total_amount = '{0:.2f}'.format(float(total_amount))
        cal_vat(vat)
        cal_total_amount(total_amount)
        return total_amount


def cal_amount(price):
    mycursor = mydb.cursor()
    sql_parking = "update parking_log set amount = %s where license_plate = 'กข45678'"
    val = (price,)
    mycursor.execute(sql_parking, val)
    mydb.commit()
    mycursor.close()


def cal_vat(vat):
    mycursor = mydb.cursor()
    sql_parking = "update parking_log set vat = %s where license_plate = 'กข45678'"
    val = (vat,)
    mycursor.execute(sql_parking, val)
    mydb.commit()
    mycursor.close()


def cal_total_amount(total_amount):
    mycursor = mydb.cursor()
    sql_parking = "update parking_log set total_amount = %s where license_plate = 'กข45678' "
    val = (total_amount,)
    mycursor.execute(sql_parking, val)
    mydb.commit()
    mycursor.close()


# print(cal_Price())
