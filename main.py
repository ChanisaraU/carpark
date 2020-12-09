from member import member
from current import *

# from current import cal_current
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
import json
# path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)


def find_camera(id):
    cameras = ['rtsp://admin:ap123456789@172.16.6.4',
               'rtsp://admin:ap123456789@172.16.6.5']
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


@app.route('/checkin')  # checkin
def checkin():
    cursor = mysql.connection.cursor()
    sql = 'select * from test_log where id = 0'
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

    return render_template('checkin.html', mem_type=mem_type, expiry_date=expiry_date, licenseP=licenseP, time_in=time_in, car_out=car_out)


@app.route('/checkout')  # checkout
def checkout():
    cursor = mysql.connection.cursor()
    sql = 'select * from test_log where id = 0'
    cursor.execute(sql)
    info = cursor.fetchone()
    car_out = info[2]  # license_plate

    cursor3 = mysql.connection.cursor()
    sql3 = 'select * from member where license_plate = %s'
    val = (car_out,)
    cursor3.execute(sql3, val)
    member1 = cursor3.fetchone()

    price = member()
    print(price)
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

    return render_template('checkout.html', price=price, time_out=time_out, dateOut=dateOut, car_out=car_out, dateIn=dateIn, time_in=time_in, mem_type=mem_type, expiry_date=expiry_date)


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
        if account:
            now = datetime.now()
            session['username'] = request.form['username']
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            login_date = now.strftime('%Y-%m-%d %H:%M:%S')
            sql = "INSERT INTO login_history(user_name,user_ip,system,login_date,status) VALUES (%s, %s, %s, %s, %s)"
            val = (account[8], ip_address,
                   "ระบบลานจอดรถสวนรถไฟ", login_date, "signed in")
            cursor.execute(sql, val)
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('car_in'))
        else:
            sql = 'select * from user_admin where user_name = %s'
            cursor.execute(sql, (username,))
            account = cursor.fetchone()
            if account:
                error = 'Incorrect password!'
            else:
                error = 'Incorrect username!'

    return render_template('login.html', error=error)


@app.route('/home')  # หน้า Dashboard
def dashboard():
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
    return render_template('home.html', diff=diff, colored=colored)


@app.route("/livesearch", methods=["POST", "GET"])
def livesearch():
    if request.method == 'POST':
        searchbox = request.form.get("text")
        print(searchbox)
        cursor = mysql.connection.cursor()
        # This is just example query , you should replace field names with yours
        query = "select * from parking_log where license_plate LIKE '{}%'".format(
            searchbox)
        cursor.execute(query)
        result = cursor.fetchall()
        if result :
         #  license_plate = result[0][2]
         time = str(result[0][8])
         time_total = str(result[0][17])
         name = " "
         memtype = " "
         expi = " "
         cs = mysql.connection.cursor()
         q = "select * from member where license_plate LIKE '{}%'".format(
            searchbox)
         cs.execute(q)
         mem = cs.fetchall()
         if mem :
          name = mem[0][3]+" "+mem[0][4]+" "+mem[0][5]
          memtype = mem[0][2]
          expi = mem[0][11]
          print(name)
        else :
         time = " "
         time_total = " "
         name = " "
         memtype = " "
         expi = " "

        return jsonify(time, time_total, name, memtype, expi)
        # return jsonify(result)
    # else:
    #     mycursor = mysql.connection.cursor()
    #     cursor2 = mysql.connection.cursor()
    #     query2 = "select * from parking_log order by time_in DESC,date_in DESC"
    #     cursor2.execute(query2)
    #     data = cursor2.fetchall()
    #     sql = "INSERT INTO lately_comein(id,license_plate,province,car_type,img_license_plate_in,time_in,date_in,img_license_plate_out) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
    #     val = (data[0][0], data[0][2], data[0][3], data[0][5],
    #            data[0][6], data[0][7], data[0][8], data[0][13])
    #     mycursor.execute(sql, val)
    #     mysql.connection.commit()
    #     mycursor.close()
    #     return 'success'


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
def current1():
    discount = request.form.get("discount")  # คูปอง
    fines = request.form.get("fines")  # ค่าปรับ
    original_amount = request.form.get(
        "original_amount")  # ค่าจอดรถรวม vat แล้ว
    receieve = request.form.get("receieve")  # เงินที่ได้รับ
    changes = request.form.get("changes")  # เงินทอน

    cal_discount(discount)
    cal_fines(fines)
    cal_receieve(receieve)
    cal_changes(changes)

    return maindown()


@app.route('/car-out2', methods=["POST"])
def current2():
    discount = request.form.get("discount")  # คูปอง
    fines = request.form.get("fines")  # ค่าปรับ
    original_amount = request.form.get(
        "original_amount")  # ค่าจอดรถรวม vat แล้ว
    receieve = request.form.get("receieve")  # เงินที่ได้รับ
    changes = request.form.get("changes")  # เงินทอน

    cal_discount(discount)
    cal_fines(fines)
    cal_receieve(receieve)
    cal_changes(changes)

    return maindown()


@app.route('/car-out1', methods=["GET"])  # ข้อมูลรถออกลานจอด
def maindown1():
    if session['username'] != " ":
        price = member()

        cursor = mysql.connection.cursor()
        sql = 'select * from test_log where id = 0'
        cursor.execute(sql)
        info = cursor.fetchone()
        car_out = info[2]  # license_plate
        province = info[3]

        cursor3 = mysql.connection.cursor()
        sql3 = 'select * from member where license_plate = %s'
        val = (car_out,)
        cursor3.execute(sql3, val)
        member1 = cursor3.fetchone()

        if member1:
            name = member1[4]+" "+member1[5]
            mem_type = member1[2]
            expiry_date = member1[11]
            time_in = str(info[8])+" "+str(info[7])
            dt = info[15]
            time_out = str(dt.day) + "/" + str(dt.month) + \
                "/" + str(dt.year)+" "+str(info[14])
            amount = info[26]

        else:
            name = "-"
            mem_type = "visitors"
            expiry_date = "-"
            time_in = str(info[7])
            time_out = str(info[14])
            amount = info[26]

    return render_template('car-out1.html', name=name, mem_type=mem_type, expiry_date=expiry_date, time_in=time_in, time_out=time_out, amount=amount, car_out=car_out ,province=province)


@app.route('/car-out2', methods=["GET"])  # ข้อมูลรถออกลานจอด
def maindown2():
    if session['username'] != " ":
        price = member()

        cursor = mysql.connection.cursor()
        sql = 'select * from test_log where id = 0'
        cursor.execute(sql)
        info = cursor.fetchone()
        car_out = info[2]  # license_plate
        province = info[3]

        cursor3 = mysql.connection.cursor()
        sql3 = 'select * from member where license_plate = %s'
        val = (car_out,)
        cursor3.execute(sql3, val)
        member1 = cursor3.fetchone()

        if member1:
            name = member1[4]+" "+member1[5]
            mem_type = member1[2]
            expiry_date = member1[11]
            time_in = str(info[8])+" "+str(info[7])
            dt = info[15]
            time_out = str(dt.day) + "/" + str(dt.month) + \
                "/" + str(dt.year)+" "+str(info[14])
            amount = info[26]

        else:
            name = "-"
            mem_type = "visitors"
            expiry_date = "-"
            time_in = str(info[7])
            time_out = str(info[14])
            amount = info[26]

    return render_template('car-out2.html', name=name, mem_type=mem_type, expiry_date=expiry_date, time_in=time_in, time_out=time_out, amount=amount, car_out=car_out, province=province)


@app.route('/report')  # รายงาน
def report():
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
        return render_template('report.html', values=values, labels=labels, legend=legend)


@app.route('/transaction', methods=['GET', 'POST'])  # รายการรถเข้า-ออกสะสม
def listcar():
    if session['username'] != " ":
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        cursor = mysql.connection.cursor()
        query = "select * from parking_log where date_in = %s order by time_in DESC,date_in DESC"
        cursor.execute(query, (today,))
        resultt = cursor.fetchall()
        return render_template('transaction.html', result=resultt, data=[{'in_out': 'เข้า'}, {'in_out': 'ออก'}], type=[{'typecar': 'รถยนต์ส่วนบุคคล'}, {'typecar': 'รถแท๊กซี่'}, {'typecar': 'รถจักรยานยนต์'}])


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


@app.route('/invoice')
def invoice():
    rendered = render_template("comp/invoice.html")
    options = {'disable-smart-shrinking': ''}
    pdf = pdfkit.from_string(
        rendered, False, configuration=config, options=options)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline;filename=output.pdf'
    return response


@app.route('/receipt')
def receipt():
    return render_template('comp/receipt.html')


if __name__ == "__main__":
    app.run(host='localhost')
