from flask_paginate import Pagination, get_page_parameter
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy, Model
from member import member
from member_two import member_two
from current import *
from receipt import *
import pandas
import sqlalchemy
import json
from current import *
from flask import Flask, jsonify, request, render_template, Response, redirect, url_for, session, Blueprint, make_response
from app import app
from db_config import mysql  # import sql
import cv2
import time
from datetime import datetime
import socket
import io
import xlwt
import pdfkit


app.config['SQLALCHEMY_DATABASE_URI']="mysql://root:@localhost/car_trmp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Parking_log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(10), unique=True, nullable=False)
    province = db.Column(db.String(50), unique=True, nullable=False)
    img_face_in = db.Column(db.String(120), unique=True, nullable=False)
    img_license_plate_in = db.Column(
        db.String(80), unique=True, nullable=False)
    car_type = db.Column(db.String(20), unique=True, nullable=False)
    time_in = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_in = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    insert_by_in = db.Column(db.String(50), unique=True, nullable=False)
    insert_date_in = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)
    cancel = db.Column(db.String(80), unique=True, nullable=False)
    img_face_out = db.Column(db.String(120), unique=True, nullable=False)
    img_license_plate_out = db.Column(
        db.String(80), unique=True, nullable=False)
    time_out = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_out = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    time_total = db.Column(db.String(10), unique=True, nullable=False)
    discount_name = db.Column(db.String(50), unique=True, nullable=False)
    pay_fine = db.Column(db.Float, unique=True, nullable=False)
    amount = db.Column(db.Float, unique=True, nullable=False)
    discount = db.Column(db.Float, unique=True, nullable=False)
    earn = db.Column(db.Float, unique=True, nullable=False)
    changes = db.Column(db.Float, unique=True, nullable=False)
    insert_by_out = db.Column(db.String(120), unique=True, nullable=False)
    insert_date_out = db.Column(db.String(120), unique=True, nullable=False)
    reason = db.Column(db.String(120), unique=True, nullable=False)
    total_amount = db.Column(db.Float, unique=True, nullable=False)
    vat = db.Column(db.Float, unique=True, nullable=False)
    fines = db.Column(db.Float, unique=True, nullable=False)
    licenplate_out = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return '<Parking_log %r>' % self.Parking_log

# log = Parking_log.query.filter_by(id=1).first()
# print(log.license_plate)


path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

now = datetime.now()  # current date and time
year = now.strftime("%Y")
month = now.strftime("%m")
day = now.strftime("%d")
time = now.strftime("%H:%M:%S")
date_time = now.strftime("%m/%d/%Y, %H:%M:%S")


def find_camera(id):
    cameras = ['rtsp://admin:ap123456789@172.16.6.4/profile3',
               'rtsp://admin:ap123456789@172.16.6.5/profile3', 'rtsp://admin:ap123456789@172.16.6.3/profile3']
    return cameras[int(id)]

# camera = cv2.VideoCapture('rtsp://admin:Jpark*2020*@172.20.1.138')  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera


def gen_frames(camera_id):  # generate frame by frame from camera
    cam = find_camera(camera_id)
    cap = cv2.VideoCapture(cam)

    while True:
        # Capture frame-by-frame
        success, frame = cap.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # concat frame one by one and show result
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed/<string:id>/', methods=["GET"])
def video_feed(id):
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen_frames(id), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/monitor-in')  # checkin
def monitorin():
    cursor = mysql.connection.cursor()
    sql = 'select * from test_log where gate = 0'
    cursor.execute(sql)
    info = cursor.fetchone()
    car_out = info[2]  # license_plate

    cursor3 = mysql.connection.cursor()
    sql3 = 'select * from member where license_plate = %s'
    val = (car_out,)
    cursor3.execute(sql3, val)
    member = cursor3.fetchone()

    if member:
        mem_type = member[2]
        expiry_date = member[11]
        licenseP = info[2]
        time_in = str(info[8])+" "+str(info[7])
        dt = info[15]
        amount = info[26]

    else:
        mem_type = "visitors"
        expiry_date = "-"
        licenseP = " "
        time_in = str(info[8])
        date_in = str(info[7])

    return render_template('monitor-in.html', mem_type=mem_type, expiry_date=expiry_date, licenseP=licenseP, time_in=time_in, car_out=car_out)


@app.route('/monitor-out')  # checkout
def monitorout():
    cursor = mysql.connection.cursor()
    sql = 'select * from test_log where gate = 0'
    cursor.execute(sql)
    info = cursor.fetchone()
    car_out = info[2]  # license_plate

    cursor3 = mysql.connection.cursor()
    sql3 = 'select * from member where license_plate = %s'
    val = (car_out,)
    cursor3.execute(sql3, val)
    member1 = cursor3.fetchone()

    price ,excluding_vat ,vat = member()
    if member1:
        mem_type = member1[2]
        expiry_date = member1[11]
        licenseP = info[2]
        time_in = str(info[8])+" "+str(info[7])
        dt = info[15]
        amount = info[26]
        time_in = str(info[7])
        time_out = str(info[14])
        date_in = info[8]
        date_out = info[15]
        dateIn = str(date_in.day) + "/" + str(date_in.month) + \
            "/" + str(date_in.year)
        dateOut = str(date_out.day) + "/" + \
            str(date_out.month) + "/" + str(date_out.year)

    else:
        mem_type = "visitors"
        expiry_date = "-"
        licenseP = " "
        time_in = str(info[7])
        time_out = str(info[14])
        date_in = info[8]
        date_out = info[15]
        dateIn = str(date_in.day) + "/" + str(date_in.month) + \
            "/" + str(date_in.year)
        dateOut = str(date_out.day) + "/" + \
            str(date_out.month) + "/" + str(date_out.year)

    return render_template('monitor-out.html', price=price, time_out=time_out, dateOut=dateOut, car_out=car_out, dateIn=dateIn, time_in=time_in, mem_type=mem_type, expiry_date=expiry_date)


@app.route('/', methods=['GET', 'POST'])  # ระบบ Login
def login():
    error = None
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute(
            'select * from user_admin where user_name = %s AND pass_word = %s', (username, password))
        account = cursor.fetchone()
        session["roles"] = account[2]

        if account:
            now = datetime.now()
            session['username'] = request.form['username']
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            login_date = now.strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO login_history(user_name,user_ip,system,login_date,status) VALUES (%s, %s, %s, %s, %s)"
            val = (account[7], ip_address,
                   "ระบบลานจอดรถสวนรถไฟ", login_date, "signed in")
            cursor.execute(sql, val)
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('transaction'))
        else:
            sql = 'select * from user_admin where user_name = %s'
            cursor.execute(sql, (username,))
            account = cursor.fetchone()
            if account:
                error = 'Incorrect password!'
            else:
                error = 'Incorrect username!'

    return render_template('login.html', error=error)


@app.route('/showled')  # แสดงจำนวนรถที่ว่าง
def showled():
    if session['username'] != " ":
        mycursor = mysql.connection.cursor()
        query = "select * from parking"
        mycursor.execute(query)
        result = mycursor.fetchall()
        total_car = result[0][2]

    if total_car < 500:
        diff = 500 - total_car
        colored = {'color': 'green'}
    else:
        diff = "FULL"
        colored = {'color': 'red'}
    return render_template('showled.html', diff=diff, colored=colored)


@app.route('/car-in')  # ข้อมูลรถเข้าลานจอด
def car_in():
    if session['username'] != " ":
        return render_template('car-in.html')


@app.route('/car-out1', methods=["POST"])
def current():
    discount = request.form.get("discount")  # คูปอง
    fines = request.form.get("fines")  # ค่าปรับ
    original_amount = request.form.get(
        "original_amount")  # ค่าจอดรถรวม vat แล้ว
    receieve = request.form.get("receieve")  # เงินที่ได้รับ
    changes = request.form.get("changes")  # เงินทอน
    gate = request.form.get("gate") #id 
    excluding_vat = request.form.get("excluding_vat") #เงินจากการเอาไปลบภาษี
    vat = request.form.get("vat") # ภาษี

    cal_excluding_vat(excluding_vat, gate)
    cal_vat(vat, gate)
    cal_discount(discount, gate)
    cal_fines(fines, gate)
    cal_receieve(receieve,gate)
    cal_changes(changes,gate)
    cal_original_amount(original_amount,gate)
    TAX_ID = request.form.get("TAX_ID") 
    POS_ID = request.form.get("POS_ID") 
    REG_ID = request.form.get("REG_ID") 
    cashier_box = request.form.get("cashier_box") 
    user = request.form.get("user") 
    
    original_time_out = request.form.get("original_time_out") 
    original_time_total = request.form.get("original_time_total") 
    original_license_plate = request.form.get("original_car_out") 
    time_in = request.form.get("time_in") 
    date_in = request.form.get("date_in") 
    time_out = request.form.get("time_out") 
    date_out = request.form.get("date_out") 
    cashier_box = request.form.get("cashier_box") 
    today = datetime.today()
    
    record_receipt(TAX_ID, POS_ID, REG_ID, today, cashier_box,original_license_plate,original_amount ,date_in ,date_out, time_in, time_out,discount ,fines ,changes ,receieve ,user)
    
    return maindown()


@app.route('/car-out2', methods=["POST"])
def current2():
    discount = request.form.get("discount")  # คูปอง
    fines = request.form.get("fines")  # ค่าปรับ
    original_amount = request.form.get(
        "original_amount")  # ค่าจอดรถรวม vat แล้ว
    receieve = request.form.get("receieve")  # เงินที่ได้รับ
    changes = request.form.get("changes")  # เงินทอน
    gate = request.form.get("gate") #id 
    excluding_vat = request.form.get("excluding_vat") #เงินจากการเอาไปลบภาษี
    vat = request.form.get("vat") # ภาษี

    cal_excluding_vat(excluding_vat, gate)
    cal_vat(vat, gate)
    cal_discount(discount, gate)
    cal_fines(fines, gate)
    cal_receieve(receieve,gate)
    cal_changes(changes,gate)
    cal_original_amount(original_amount,gate)
    TAX_ID = request.form.get("TAX_ID") 
    POS_ID = request.form.get("POS_ID") 
    REG_ID = request.form.get("REG_ID") 
    cashier_box = request.form.get("cashier_box") 
    user = request.form.get("user") 
    
    original_time_out = request.form.get("original_time_out") 
    original_time_total = request.form.get("original_time_total") 
    original_license_plate = request.form.get("original_car_out") 
    time_in = request.form.get("time_in") 
    date_in = request.form.get("date_in") 
    time_out = request.form.get("time_out") 
    date_out = request.form.get("date_out") 
    cashier_box = request.form.get("cashier_box") 
    today = datetime.today()
    
    record_receipt(TAX_ID, POS_ID, REG_ID, today, cashier_box,original_license_plate,original_amount ,date_in ,date_out, time_in, time_out,discount ,fines ,changes ,receieve ,user)
    return maindown_two()


@app.route('/car-out1', methods=["GET"])  # ข้อมูลรถออกลานจอด
def maindown():
    if session['username'] != " ":
        price ,excluding_vat ,vat = member()
        user = session['username']
        cursor = mysql.connection.cursor()
        sql = 'select * from test_log where gate = 0'
        cursor.execute(sql)
        info = cursor.fetchone()
        
        car_out = info[2]  # license_plate
        province = info[3]
        gate = info[1]

        cursor3 = mysql.connection.cursor()
        sql3 = 'select * from member where license_plate = %s'
        val = (car_out,)
        cursor3.execute(sql3, val)
        member1 = cursor3.fetchone()

        if member1:
            name = member1[4]+" "+member1[5]
            mem_type = member1[2]
            expiry_date = member1[11]
            time_in = str(info[7])
            date_in = str(info[8])
            time_out = str(info[14])
            date_out = str(info[15])
            amount = price

        else:
            name = "-"
            mem_type = "visitors"
            expiry_date = "-"
            time_in = str(info[7])
            date_in = str(info[8])
            time_out = str(info[14])
            date_out = str(info[15])
            amount = info[19]
            
    return render_template('car-out1.html', date_in=date_in, date_out=date_out, user=user, excluding_vat=excluding_vat , vat=vat, gate=gate, province=province, name=name, mem_type=mem_type, expiry_date=expiry_date, time_in=time_in, time_out=time_out, amount=amount, car_out=car_out)



@app.route('/car-out2', methods=["GET"])  # ข้อมูลรถออกลานจอด
def maindown_two():
    if session['username'] != " ":
        user = session['username']
        price ,excluding_vat ,vat = member_two()

        cursor = mysql.connection.cursor()
        sql = 'select * from test_log where gate = 1'
        cursor.execute(sql)
        info = cursor.fetchone()
        car_out = info[2]  # license_plate
        province = info[3]
        gate = info[1]
        cursor3 = mysql.connection.cursor()
        sql3 = 'select * from member where license_plate = %s'
        val = (car_out,)
        cursor3.execute(sql3, val)
        member1 = cursor3.fetchone()

        if member1:
            name = member1[4]+" "+member1[5]
            mem_type = member1[2]
            expiry_date = member1[11]
            time_in = str(info[7])
            date_in = str(info[8])
            time_out = str(info[14])
            date_out = str(info[15])
            amount = price

        else:
            name = "-"
            mem_type = "visitors"
            expiry_date = "-"
            time_in = str(info[7])
            date_in = str(info[8])
            time_out = str(info[14])
            date_out = str(info[15])
            amount = info[19]

    return render_template('car-out2.html', date_in=date_in, date_out=date_out, user=user, excluding_vat=excluding_vat , vat=vat, gate=gate, province=province, name=name, mem_type=mem_type, expiry_date=expiry_date, time_in=time_in, time_out=time_out, amount=amount, car_out=car_out)


report_header_definition = {
    "": {
        "api": "",
        "title": "",
        "header": []
    },
    "car": {
        "api": "/report/table-car/datatable",
        "title": ["รายงานการเข้าออกของรถ"],
        "header": [
            "ลำดับ",
            "ประเภท",
            "ทะเบียนรถ",
            "เวลาเข้า",
            "เจ้าหน้าที่ขาออก",
            "เวลาออก",
            "ชม.จอด",
            "ชม.โปรโมชั่น",
            "ชม.ลด",
            "ชม.จ่าย",
            "ค่าปรับบัตรหาย",
            "รายได้",
            "ส่วนลด"
        ]
    },
    "salestax": {
        "api": "/report/table-salestax/datatable",
        "title": ["รายงานภาษีขาย"],
        "header": [
            "ลำดับ",
            "เลขที่ใบกำกับภาษี",
            "หมายเลขบัตร",
            "ทะเบียนรถ",
            "วันที่เข้า",
            "เวลาเข้า",
            "เจ้าหน้าที่ขาออก",
            "ตำแหน่งทำรายการ",
            "วันที่ออก",
            "เวลาออก",
            "ค่าปรับ",
            "ค่าบริการ",
            "ภาษีมูลค่าเพิ่ม",
            "รวม"
        ]
    },
    "outcar": {
        "api": "/report/outcar/datatable",
        "title": ["รายงานรถค้าง"],
        "header": [
            "ลำดับ",
            "ประเภท",
            "ทะเบียนรถ",
            "วันเวลาเข้า"
        ]
    },
    "staff": {
        "api": "/report/table-staff/datatable",
        "title": ["รายงานการทำงานของเจ้าหน้าที่"],
        "header": [
            "ลำดับ",
            "ชื่อเจ้าหน้าที่",
            "เวลาเข้า",
            "เวลาออก",
            "รายได้",
            "ส่วนลด"
        ]
    },
    "member_income": {
        "api": "/report/table_member_income/datatable",
        "title": ["รายงานรายได้จากสมาชิก"],
        "header": [
            "ลำดับ",
            "ชื่อ - นามสกุล",
            "ทะเบียนรถ",
            "เลขที่ใบเสร็จ",
            "วันที่ชำระ",
            "วันหมดอายุ",
            "รายได้",
            "เจ้าหน้าที่"
        ]
    },
}


@app.route('/report', methods=['GET', 'POST'])  # รายงาน
def report():
    if session['username'] != " ":
        if request.method == "POST":
            report_list = request.form.get("reports")
            if report_list != None:
                return render_template("report.html", report_list=report_list)

        report_name = request.args.get('reports') #รับค่ามาจาก ตัวเลือกหน้า report id="mySelect" name="reports"
        if not report_name:
            report_name = list(report_header_definition.keys())[0]
        table_header = report_header_definition[report_name]['header']
        title = report_header_definition[report_name]['title']
        api = report_header_definition[report_name]['api']
        # api_param = "?"

        # api_param = "&"
        # params = []
        # if date_in:
        #     params.append("date_in=" + date_in) # date_in=2020-10-10
        # if date_out:
        #     params.append("date_out=" + date_out) # date_out=2020-10-10

        # api_param += "&".join(params)

        # ?date_in=2020-10-10&date_out=2020-10-10

        # &date_in=2020-10-10&date_out=2020-10-10

    return render_template("report.html", table_header=table_header, api=api, title=title)


@app.route('/report-dash')  # รายงาน
def reportdash():
    if session['username'] != " ":
        legend = "Data A"
        cursor = mysql.connection.cursor()
        try:
            cursor.execute("select amount from parking_log")
            rows = cursor.fetchall()
            labels = list()
            i = 0
            for row in rows:
                labels.append(row[i])

            cursor.execute("select date_out from parking_log")
            rows = cursor.fetchall()
            # Convert query to objects of key-value pairs
            values = list()
            i = 0
            for row in rows:
                values.append(row[i])
            mysql.connection.commit()
            cursor.close()

        except:
            print("Error: Unable to fetch items")
        return render_template('report-dash.html', values=values, labels=labels, legend=legend)


@app.route('/transaction', methods=['GET', 'POST'])
def transaction():
    if session['username'] != " ":
        roles = request.args.get('roles', None)
        page = request.args.get(get_page_parameter(), type=int, default=1)
        limit = 5
        offset = page*limit-limit
        cursor = mysql.connection.cursor()
        cursor.execute("select * from parking_log")
        result = cursor.fetchall()
        total = len(result)
        now = datetime.now().strftime('%Y-%m-%d')
        cur = mysql.connection.cursor()
        que = "select * from parking_log ORDER By time_in DESC,date_in DESC LIMIT %s OFFSET %s"
        cur.execute(que, (limit, offset))
        data = cur.fetchall()
        cur.close()

        pagination = Pagination(page=page, per_page=limit,
                                total=total, record_name='transaction', css_framework='bootstrap4')
        return render_template('transaction.html', roles=roles, pagination=pagination, transaction=data, data=[{'in_out': 'เข้า'}, {'in_out': 'ออก'}], type=[{'typecar': 'รถยนต์ส่วนบุคคล'}, {'typecar': 'รถแท๊กซี่'}, {'typecar': 'รถจักรยานยนต์'}])

# @app.route('/transaction', methods=['GET', 'POST'])  # รายการรถเข้า-ออกสะสม
# def listcar():
#     if session['username'] != " ":
#         now = datetime.now()
#         today = now.strftime('%Y-%m-%d')
#         cursor = mysql.connection.cursor()
#         query = "select * from parking_log where date_in = %s order by time_in DESC,date_in DESC"
#         cursor.execute(query, (today,))
#         resultt = cursor.fetchall()
#         return render_template('transaction.html', result=resultt, data=[{'in_out': 'เข้า'}, {'in_out': 'ออก'}], type=[{'typecar': 'รถยนต์ส่วนบุคคล'}, {'typecar': 'รถแท๊กซี่'}, {'typecar': 'รถจักรยานยนต์'}])


@app.route('/addcar', methods=['GET', 'POST'])  # รายการรถเข้า-ออกสะสม
def addcar():
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    cursor = mysql.connection.cursor()
    query = "select * from parking_log where date_in = %s order by time_in DESC,date_in DESC"
    cursor.execute(query, (today,))
    resultt = cursor.fetchall()
    cursor2 = mysql.connection.cursor()
    in_out = request.form.get('comp_select')
    province = request.form.get('province')
    typecar = request.form.get('typecar')
    carregis = request.form.get('carregis')
    timeinout = request.form.get('timeinout')
    motive = request.form.get('motive')
    amountmoney = request.form.get('amountmoney')
    cursor2 = mysql.connection.cursor()
    if in_out == 'เข้า':
        sql = "INSERT INTO parking_log(id,license_plate,province,time_in,car_type) VALUES (%s, %s, %s, %s, %s)"
        val = (in_out, carregis, province, timeinout, typecar)
        cursor2.execute(sql, val)
        mysql.connection.commit()
        cursor2.close()
    return render_template('transaction.html', result=resultt, data=[{'in_out': 'เข้า'}, {'in_out': 'ออก'}], type=[{'typecar': 'รถยนต์ส่วนบุคคล'}, {'typecar': 'รถแท๊กซี่'}, {'typecar': 'รถจักรยานยนต์'}])


@app.route('/edit', methods=["POST", "GET"])
def edit():
    cursor2 = mysql.connection.cursor()
    id = request.values.get('id')
    car_regis = request.values.get('carregis_')
    province = request.values.get('province_')
    typecar = request.values.get('typecar_')

    sql = "UPDATE parking_log SET license_plate = %s, province= %s ,car_type= %s WHERE id = %s"
    val = (car_regis, province, typecar, id)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    cursor = mysql.connection.cursor()
    query = "select * from parking_log where date_in = %s order by time_in DESC,date_in DESC"
    cursor.execute(query, (today,))
    resultt = cursor.fetchall()
    return render_template('transaction.html', result=resultt, data=[{'in_out': 'เข้า'}, {'in_out': 'ออก'}], type=[{'typecar': 'รถยนต์ส่วนบุคคล'}, {'typecar': 'รถแท๊กซี่'}, {'typecar': 'รถจักรยานยนต์'}])


# Export to Excel :: Transaction
@app.route('/download/report/excel')
def download_report():
    cursor = mysql.connection.cursor()
    query = "select id, code, license_plate, province, car_type, insert_by_in, insert_date_in, cancel, time_total, discount_name, pay_fine, amount, discount, earn, reason from parking_log"
    cursor.execute(query)
    result = cursor.fetchall()

    # Output in bytes
    output = io.BytesIO()
    # Create Workbook Object
    workbook = xlwt.Workbook()
    # Add a sheet
    sh = workbook.add_sheet('Transaction Report')

    # Add headers
    sh.write(0, 0, 'ลำดับ')
    sh.write(0, 1, 'เลขสมาชิก')
    sh.write(0, 2, 'เลขทะเบียนรถ')
    sh.write(0, 3, 'จังหวัด')
    sh.write(0, 4, 'ประเภทรถ')
    sh.write(0, 5, 'ผู้ใช้ระบบขาเข้า')
    sh.write(0, 6, 'วันที่คีย์ข้อมูลเข้าระบบขาเข้า')
    sh.write(0, 7, 'กรณียกเลิกจากระบบ')
    sh.write(0, 8, 'เวลาทั้งหมดที่จอด')
    sh.write(0, 9, 'ชื่อส่วนลด')
    sh.write(0, 10, 'ค่าปรับบัตรหาย')
    sh.write(0, 11, 'ค่าจอดสุทธิ')
    sh.write(0, 12, 'ส่วนลดทั้งหมด')
    sh.write(0, 13, 'จำนวนเงินที่ได้รับ')
    sh.write(0, 14, 'สาเหตุ')

    idx = 0
    for row in result:
        sh.write(idx+1, 0, row[0])
        sh.write(idx+1, 1, row[1])
        sh.write(idx+1, 2, row[2])
        sh.write(idx+1, 3, row[3])
        sh.write(idx+1, 4, row[4])
        sh.write(idx+1, 5, row[5])
        sh.write(idx+1, 6, row[6])
        sh.write(idx+1, 7, row[7])
        sh.write(idx+1, 8, row[8])
        sh.write(idx+1, 9, row[9])
        sh.write(idx+1, 10, row[10])
        sh.write(idx+1, 11, row[11])
        sh.write(idx+1, 12, row[12])
        sh.write(idx+1, 13, row[13])
        sh.write(idx+1, 14, row[14])
        idx += 1
    workbook.save(output)
    output.seek(0)

    return Response(output, mimetype="application/ms-excel", headers={"Content-Disposition": "attachment;filename=transaction_report.xls"})


@app.route('/member-detail', methods=['GET', 'POST'])
def memberdetail():
    if session['username'] != " ":
        # โชว์เฉพาะ Member
        page = request.args.get(get_page_parameter(), type=int, default=1)
        limit = 10
        offset = page*limit-limit
        cursor = mysql.connection.cursor()
        cursor.execute("select * from member where type='Member'")

        result = cursor.fetchall()
        total = len(result)
        cur = mysql.connection.cursor()
        que = "select * from member where type='Member' LIMIT %s OFFSET %s"
        cur.execute(que, (limit, offset))
        data = cur.fetchall()
        cur.close()
        pagination = Pagination(page=page, per_page=limit,
                                total=total, record_name='mdetail', css_framework='bootstrap4')

        # โชว์เฉพาะ VIP
        page2 = request.args.get(get_page_parameter(), type=int, default=1)
        limit2 = 10
        offset2 = page2*limit2-limit2
        cursor2 = mysql.connection.cursor()
        cursor2.execute("select * from member where type='VIP'")

        result2 = cursor.fetchall()
        total2 = len(result2)
        cur2 = mysql.connection.cursor()
        que2 = "select * from member where type='VIP' LIMIT %s OFFSET %s"
        cur2.execute(que2, (limit, offset2))
        data2 = cur2.fetchall()
        cur2.close()
        pagination2 = Pagination(page2=page2, per_page=limit2, total=total2, record_name2='vdetail', css_framework='bootstrap4')

        return render_template('member-detail.html', pagination=pagination, mdetail=data, pagination2=pagination2, vdetail=data2)


@app.route('/addmember', methods=["POST", "GET"])
def addmember():
    cursor = mysql.connection.cursor()
    query = "select * from member where type='Member'"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor2 = mysql.connection.cursor()
    title_name = request.form.get('title_name')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    license_plate = request.form.get('license_plate')
    province = request.form.get('province_')
    member_package = request.form.get('member_package')
    # position = request.form.get('position')
    cursor2 = mysql.connection.cursor()
    sql = "INSERT INTO member(id, title_name, first_name, last_name, phone, license_plate, province, member_package) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (title_name, first_name, last_name, phone,
           license_plate, province, member_package)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()
    return render_template('member-detail.html', result=result)


@app.route('/remember', methods=["POST", "GET"])
def remember():
    cursor2 = mysql.connection.cursor()
    id = request.values.get('id')
    title_name = request.values.get('title_name_')
    first_name = request.values.get('first_name_')
    last_name = request.values.get('last_name_')
    phone = request.values.get('phone_')
    license_plate = request.values.get('license_plate_')
    province = request.values.get('province_')
    member_package = request.values.get('member_package_')
    position = request.values.get('position_')
    remark = request.values.get('remark_')

    sql = "UPDATE member SET title_name=%s, first_name=%s, last_name=%s, phone=%s, license_plate=%s, province=%s, member_package= %s, position= %s, remark= %s WHERE id = %s"
    val = (title_name, first_name, last_name, phone, license_plate,
           province, member_package, position, remark, id)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()
    cursor = mysql.connection.cursor()
    query = "select * from member where type='VIP'"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('member-detail.html', result=result)


@app.route('/editmember', methods=["POST", "GET"])
def editmember():
    cursor2 = mysql.connection.cursor()
    id = request.values.get('id')
    title_name = request.values.get('title_name_')
    first_name = request.values.get('first_name_')
    last_name = request.values.get('last_name_')
    phone = request.values.get('phone_')
    license_plate = request.values.get('license_plate_')
    province = request.values.get('province_')
    member_package = request.values.get('member_package_')
    position = request.values.get('position_')
    remark = request.values.get('remark_')

    sql = "UPDATE member SET title_name=%s, first_name=%s, last_name=%s, phone=%s, license_plate=%s, province=%s, member_package= %s, position= %s, remark= %s WHERE id = %s"
    val = (title_name, first_name, last_name, phone, license_plate,
           province, member_package, position, remark, id)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()
    cursor = mysql.connection.cursor()
    query = "select * from member where type='VIP'"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('member-detail.html', result=result)


@app.route('/addvip', methods=["POST", "GET"])
def addvip():
    cursor = mysql.connection.cursor()
    query = "select * from member where type='VIP'"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor2 = mysql.connection.cursor()
    title_name = request.form.get('title_name')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    license_plate = request.form.get('license_plate')
    province = request.form.get('province_')
    member_package = request.form.get('member_package')
    # position = request.form.get('position')
    cursor2 = mysql.connection.cursor()
    sql = "INSERT INTO member(id, title_name, first_name, last_name, phone, license_plate, province, member_package) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (title_name, first_name, last_name, phone,
           license_plate, province, member_package)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()
    return render_template('member-detail.html', result=result)


@app.route('/editvip', methods=["POST", "GET"])
def editvip():
    cursor2 = mysql.connection.cursor()
    id = request.values.get('id')
    title_name = request.values.get('title_name_')
    first_name = request.values.get('first_name_')
    last_name = request.values.get('last_name_')
    phone = request.values.get('phone_')
    license_plate = request.values.get('license_plate_')
    province = request.values.get('province_')
    member_package = request.values.get('member_package_')
    position = request.values.get('position_')
    remark = request.values.get('remark_')

    sql = "UPDATE member SET title_name=%s, first_name=%s, last_name=%s, phone=%s, license_plate=%s, province=%s, member_package= %s, position= %s, remark= %s WHERE id = %s"
    val = (title_name, first_name, last_name, phone, license_plate,
           province, member_package, position, remark, id)
    cursor2.execute(sql, val)
    mysql.connection.commit()
    cursor2.close()
    cursor = mysql.connection.cursor()
    query = "select * from member where type='VIP'"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('member-detail.html', result=result)


@app.route('/newmember-receipt')
def newmember_receipt():
    cursor = mysql.connection.cursor()
    query = "select * from member"
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template('comp/newmember-receipt.html')


@app.route('/logout', methods=["POST", "GET"])
def logout():
    mycursor = mysql.connection.cursor()
    now = datetime.now()
    logout_date = now.strftime('%Y-%m-%d %H:%M:%S')

    sql = "UPDATE login_history SET status = 'signed out', logout_date= %s WHERE user_name = %s"
    val = (logout_date, session['username'])
    mycursor.execute(sql, val)
    mysql.connection.commit()
    session.pop('username', None)
    return redirect(url_for('login'))


# @app.route('/invoice')
# def invoice():
#     rendered = render_template("reports/invoice.html")
#     options = {'disable-smart-shrinking': ''}
#     pdf = pdfkit.from_string(
#         rendered, False, configuration=config, options=options)
#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = 'inline;filename=invoice.pdf'
#     return response


@app.route('/receipt')
def receipt():
    cursor = mysql.connection.cursor()
    query = "select * from receipt ORDER BY id DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    tax_id = result[1]
    pos_id = result[2]
    reg_id = result[3]
    cashier = result[4]
    cashier_box = cashier_box = result[5]
    today_date_time = result[6]
    now = datetime.now()
    no = year+month+day
    date_now = now.strftime('%Y-%m-%d %H:%M:%S')
    license_plate= result[8]
    time_in = str(result[11])
    date_in = str(result[9])
    time_out = str(result[12])
    date_out = str(result[10])

    receieve = result[12]
    discount = result[13]
    changess = result[14]
    amount = result[15]
    fines = result[16]
    
    return render_template('comp/receipt.html', no=no, date_now=date_now, tax_id=tax_id ,pos_id=pos_id,reg_id=reg_id,today_date_time=today_date_time,cashier_box=cashier_box ,license_plate=license_plate ,amount=amount ,time_out=time_out ,date_out=date_out ,date_in=date_in ,time_in=time_in ,discount=discount,fines=fines ,changess=changess ,receieve=receieve ,cashier=cashier)
>>>>>>> 2382bb8 ([mint2] แก้ไขรายละเอียดเล็กๆ)


@app.route('/receipt_two')
def receipt_two():
    cursor = mysql.connection.cursor()
    query = "select * from receipt"
    cursor.execute(query)
    result = cursor.fetchone()
    tax_id = result[1]
    pos_id = result[2]
    reg_id = result[3]
    cashier = result[4]
    cashier_box = cashier_box = result[5]
    today_date_time = result[6]
    now = datetime.now()
    no = year+month+day
    date_now = now.strftime('%Y-%m-%d %H:%M:%S')
    license_plate= result[8]
    time_in = str(result[11])
    date_in = str(result[9])
    time_out = str(result[12])
    date_out = str(result[10])
    
    receieve = result[12]
    discount = result[13]
    changess = result[14]
    amount = result[15]
    fines = result[16]

    return render_template('comp/receipt_two.html', no=no, date_now=date_now, tax_id=tax_id ,pos_id=pos_id,reg_id=reg_id,today_date_time=today_date_time,cashier_box=cashier_box ,license_plate=license_plate ,amount=amount ,time_out=time_out ,date_out=date_out ,date_in=date_in ,time_in=time_in ,discount=discount,fines=fines ,changess=changess ,receieve=receieve ,cashier=cashier)



@app.route('/slip-report')
def slip():
    return render_template('reports/slip-report.html')


@app.route('/admit-report')
def admit():
    return render_template('reports/admit-report.html')


@app.route('/inout-report')
def inout():
    rendered = render_template("reports/inout-report.html")
    options = {'disable-smart-shrinking': ''}
    pdf = pdfkit.from_string(
        rendered, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=inout-report.pdf'
    return response


@app.route('/pro-inout-report')
def proinout():
    rendered = render_template("reports/pro-inout-report.html")
    options = {'disable-smart-shrinking': ''}
    pdf = pdfkit.from_string(
        rendered, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=pro-inout-report.pdf'
    return response

>>>>>>> 2382bb8 ([mint2] แก้ไขรายละเอียดเล็กๆ)

    return render_template('comp/receipt.html', no=no, date_now=date_now, tax_id=tax_id, pos_id=pos_id, reg_id=reg_id, today_date_time=today_date_time, cashier_box=cashier_box, license_plate=license_plate, amount=amount, datetime_out=datetime_out, datetime_in=datetime_in, discount=discount, fines=fines, changess=changess, receieve=receieve, cashier=cashier)


@app.route('/shift-report')
def shift():
    if session['username'] != " ":
        user = session['username']
        cursor = mysql.connection.cursor()  # เวลา user login
        query = "select * from login_history where user_name = '" + \
            user + "'"+" ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        datein = result[4]

        cursor1 = mysql.connection.cursor()  # รายได้
        sql = "select *,sum(amount) FROM receipt where cashier = '"+user + "'"
        cursor1.execute(sql,)
        info = cursor1.fetchone()
        amount = info[17]

        cursor4 = mysql.connection.cursor()  # ส่วนลด
        sql4 = "select *,sum(discount) FROM receipt where cashier = '"+user + "'"
        cursor4.execute(sql4,)
        info4 = cursor4.fetchone()
        discount = info4[17]

        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        today = year+"-"+month+"-"+day

        cursor2 = mysql.connection.cursor()  # รถออกจาก user คนนี้
        sql2 = "select *,count(id) FROM receipt where cashier = '" + \
            user+"'"+"and"+" "+"datetime_out = "+"'"+today+"'"
        cursor2.execute(sql2,)
        info2 = cursor2.fetchone()        
        count = info2[19]
        
        cursor3 = mysql.connection.cursor() #รถเข้าทั้งหมดวันนี้
        sql3 = "select *,count(id) from parking_log where date_in = "+"'"+today+"'"
        cursor3.execute(sql3,)
        info3 = cursor3.fetchone()
        car_in = info3[25]


        stale = car_in - count  # รถคงค้างของ user นั้นๆ

        return render_template('reports/shift-report.html', car_in=car_in, stale=stale, discount=discount, count=count, amount=amount, datein=datein, user=user, date_time=date_time)

@app.route('/report/table-car')
def table_car():
    return render_template('table-report/table_car.html')


@app.route('/report/table-car/datatable')
def table_car_datatable():
    cursor = mysql.connection.cursor()
    sql = 'select id, member_type, license_plate, time_in, cashier, time_out, time_total, time_promotion, time_discount, time_grand, fines, amount, discount from parking_log'
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data


@app.route('/report/table-salestax/datatable')
def table_salestax_datatable():
    cursor = mysql.connection.cursor()
    sql = 'select receipt.id, receipt.tax_id, member.card_no, receipt.license_plate, date(receipt.datetime_in), time(receipt.datetime_in), receipt.cashier, receipt.cashier_box, date(receipt.datetime_out), time(receipt.datetime_out), receipt.fines, receipt.amount, receipt.vat, receipt.total from receipt inner join member on receipt.id = member.id'
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data

# ต้องกำหนดเงื่อนไขก่อน


@app.route('/report/outcar/datatable')
def table_outcar_datatable():


@app.route('/report/table_member_income/datatable')
def table_member_datatable():
    cursor = mysql.connection.cursor()
    sql = 'select * from member'
    cursor.execute(sql)
    info = cursor.fetchall()
    data = jsonify({'data': info})
    return data


@app.route('/report/table-vat/datatable')
def table_vat_datatable():
    cursor = mysql.connection.cursor()
    sql = 'select id, member_type, license_plate, timestamp(date_in, time_in) as datetime from parking_log where licenplate_out = ""'
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data


@app.route('/report/table-staff/datatable')
def table_staff_datatable():
    cursor = mysql.connection.cursor()
    sql = 'select id, user_name, login_date, logout_date, time(hour(login_date))+time(hour(logout_date)) as amount, discount from login_history'
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data


@app.route('/report/table_member_income/datatable')
def table_member_datatable():
    cursor = mysql.connection.cursor()
    sql = 'select id, concat(first_name, " ", last_name) as fname, license_plate, member_receipt_no, pay_date, expiry_date, grand_amount, cashier from member'
    cursor.execute(sql)
    info = cursor.fetchall()
    out = []
    for element in info:
        newelement = []
        for x in element:
            newelement.append(str(x))
        out.append(newelement)
    data = jsonify({'data': out})
    return data

if __name__ == "__main__":
    app.run(debug=True)
