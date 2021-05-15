
from flask import Flask, render_template, request, flash, redirect, url_for,session
from flask_mysqldb import MySQL,MySQLdb
import bcrypt

app = Flask(__name__, template_folder="Templates")
app.secret_key = "caircocoders-ednalan-2020"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ram2'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'ram'
#app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password'].encode('utf-8')
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("select * from usermaster where Status=1 and Email=%s" ,(Email,))
        data = cur.fetchone()
        count = cur.rowcount
        if (count) > 0:
            if bcrypt.hashpw(Password, data['Password'].encode('utf-8'))== data['Password'].encode('utf-8'):
                session['Email']=request.form['Email']
                for r in data:
                    if (r[9] == 1):
                        cur.close()
                        return render_template('/ITAdmin/itadminhome.html')
                    elif (r[9] == 2):
                        cur.close()
                        return render_template('/Admin/adminhome.html')
                    elif (r[9] == 3):
                        cur.close()
                        return render_template('/Manager/mgrhome.html')
                    else:
                        cur.close()
                        return render_template('/Employee/emphome.html')
            else:
                flash('Invalid Email or Password!!')
                return render_template('/CommonPage/login.html')

        else:
            cur.close()
            flash("login failed")
            return render_template('/CommonPage/login.html')
    return render_template('/CommonPage/login.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('/CommonPage/login.html')

    # ADMIN HOME PAGE - CRUD OPERATIONS

@app.route('/adminhome')
def Index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM usermaster where Status=1 and userrole=4 ")
    data = cur.fetchall()
    cur.close()
    return render_template('/Admin/adminhome.html', usermaster=data)


@app.route('/home1')
def home1():
    return render_template('/Admin/adminhome.html')


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        flash("Data Inserted Successfully")
        details = request.form
        Name = details['Name']
        Designation = details['Designation']
        Department = details['Department']
        ManagerId = details['ManagerId']
        City = details['City']
        Email = details['Email']
        Mobile = details['Mobile']
        Address = details['Address']
        LoginName = details['LoginName']
        Password = details['Password'].encode('utf-8')
        hash_Password=bcrypt.hashpw(Password,bcrypt.gensalt())
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usermaster (Name,Designation,Department,ManagerId,City,Email,Mobile,Address,LoginName,Password,Status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (Name, Designation, Department, ManagerId, City, Email, Mobile, Address, LoginName, hash_Password,1))
        mysql.connection.commit()
        return redirect(url_for('Index'))


@app.route('/delete/<string:EmployeeId>', methods=['GET'])
def delete(EmployeeId):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("UPDATE usermaster SET status = 0 WHERE EmployeeId=%s", [EmployeeId])
    mysql.connection.commit()
    return redirect(url_for('Index'))


@app.route('/update', methods=['POST', 'GET'])
def update():
    if request.method == 'POST':
        details = request.form
        EmployeeId = details['EmployeeId']
        Name = details['Name']
        Designation = details['Designation']
        Department = details['Department']
        ManagerId = details['ManagerId']
        City = details['City']
        Email = details['Email']
        Mobile = details['Mobile']
        Address = details['Address']
        LoginName = details['LoginName']
        Password = details['Password']
        cur = mysql.connection.cursor()
        cur.execute(
            " UPDATE usermaster SET Name=%s ,Designation=%s , Department=%s , ManagerId=%s , City=%s , Email=%s , Mobile=%s , Address=%s , LoginName=%s , Password=%s WHERE EmployeeId=%s",
            (Name, Designation, Department, ManagerId, City, Email, Mobile, Address, LoginName, Password, EmployeeId))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('Index'))

    # ADMIN HOME PAGE - ADD HOLIDAY

@app.route('/holiday')
def holiday():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM holidaycalendermaster where Status=1")
    data = cur.fetchall()
    cur.close()
    return render_template('/Admin/holiday.html', holidaycalendermaster=data)


@app.route('/holidayinsert', methods=['POST'])
def holidayinsert():
    if request.method == 'POST':
        flash("Holiday Added")
        details = request.form
        EventName = details['EventName']
        Date = details['Date']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO holidaycalendermaster(EventName,Date,Status) VALUES(%s,%s,%s)", (EventName, Date,1))
        mysql.connection.commit()
    return redirect(url_for('holiday'))


@app.route('/holidayupdate', methods=['POST', 'GET'])
def holidayupdate():
    if request.method == 'POST':
        details = request.form
        EventName = details['EventName']
        Date = details['Date']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE holidaycalendermaster SET EventName=%s,Date=%s", (EventName, Date))
        flash("Holiday Updated")
        mysql.connection.commit()
    return redirect(url_for('holiday'))


@app.route('/holidaydelete/<string:HolidayId>', methods=['GET'])
def holidaydelete(HolidayId):
    flash("Holiday Deleted")
    cur = mysql.connection.cursor()
    cur.execute("UPDATE holidaycalendermaster SET status=0 WHERE HolidayId =%s", (HolidayId))
    mysql.connection.commit()
    return redirect(url_for('holiday'))

    # MANAGER HOME PAGE - EMPLOYEE DETAILS

@app.route('/employeedetails')
def employeedetails():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM usermaster where Status=1 and userrole=4 ")
    data = cur.fetchall()
    cur.close()
    return render_template('/Manager/mgrhome.html', usermaster=data)


@app.route('/pendingleave')
def pendingleave():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM leaves where LeaveApprovalStatus=0 ")
    data = cur.fetchall()
    cur.close()
    return render_template('/Manager/pendingleave.html', leaves=data)

@app.route('/accept/<string:leaveId>', methods=['GET'])
def accept(leaveId):
    flash("Leave Has Been Accepted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("UPDATE leaves SET LeaveApprovalStatus=1  WHERE leaveId=%s", (leaveId))
    mysql.connection.commit()
    return redirect(url_for('pendingleave'))

@app.route('/reject/<string:leaveId>', methods=['GET'])
def reject(leaveId):
    flash("Leave Has Been Rejected Successfully")
    cur = mysql.connection.cursor()
    cur.execute("UPDATE leaves SET LeaveApprovalStatus=2  WHERE leaveId =%s", (leaveId))
    mysql.connection.commit()
    return redirect(url_for('pendingleave'))


@app.route('/home2')
def home2():
    return render_template('/Manager/mgrhome.html')

    # EMPLOYEE HOME PAGE


@app.route('/mydetails', methods=['GET'])
def mydetails():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usermaster where Status=1 and userrole=4")
    data = cur.fetchall()
    cur.close()
    return render_template('/Employee/emphome.html', usermaster=data)


@app.route('/leave')
def leave():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM leaves")
    data = cur.fetchall()
    cur.close()
    return render_template('/Employee/leave.html', leaves=data)


@app.route('/leaveinsert', methods=['POST'])
def leaveinsert():
    if request.method == 'POST':
        flash("Leave Added")
        details = request.form
        EmployeeId = details['EmployeeId']
        LeaveRequestDate = details['LeaveRequestDate']
        FromDate = details['FromDate']
        ToDate = details['ToDate']
        NumberofDays = details['NumberofDays']
        Reason = details['Reason']
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO leaves(EmployeeId,LeaveRequestDate,FromDate,ToDate,NumberofDays,Reason) VALUES(%s,%s,%s,%s,%s,%s)",
            (EmployeeId, LeaveRequestDate, FromDate, ToDate, NumberofDays, Reason))
        mysql.connection.commit()
    return redirect(url_for('leave'))


@app.route('/home3')
def home3():
    return render_template('/Employee/emphome.html')

@app.route('/leaveaccept')
def leaveaccept():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM leaves where LeaveApprovalStatus=1")
    data = cur.fetchall()
    cur.close()
    return render_template('/Employee/acceptedleave.html', leaves=data)

@app.route('/leavereject')
def leavereject():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM leaves where LeaveApprovalStatus=2")
    data = cur.fetchall()
    cur.close()
    return render_template('/Employee/rejectedleave.html', leaves=data)


# IT ADMIN HOME PAGE
@app.route('/itadminhome')
def itadminhome():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM camra where status=1")
    data = cur.fetchall()
    cur.close()
    return render_template('/ITAdmin/itadminhome.html', camra=data)


@app.route('/Camerainsert', methods=['POST'])
def Camerainsert():
    if request.method == 'POST':
        flash("Data Inserted Successfully")
        details = request.form
        CameraName = details['CameraName']
        Location = details['Location']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO camra (CameraName,Location,status) VALUES (%s,%s,%s)",
            (CameraName, Location,1))
        mysql.connection.commit()
        return redirect(url_for('itadminhome'))


@app.route('/Cameradelete/<string:CamaraID>', methods=['GET'])
def Cameradelete(CamaraID):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("UPDATE camra SET status=0  WHERE CamaraID=%s", (CamaraID))
    mysql.connection.commit()
    return redirect(url_for('itadminhome'))


@app.route('/Cameraupdate', methods=['POST', 'GET'])
def Cameraupdate():
    if request.method == 'POST':
        details = request.form
        CameraName = details['CameraName']
        Location = details['Location']
        cur = mysql.connection.cursor()
        cur.execute(
            " UPDATE camra SET CameraName=%s ,Location=%s ",
            (CameraName, Location))
        flash("Data Updated Successfully")
        mysql.connection.commit()
        return redirect(url_for('itadminhome'))

@app.route('/home')
def home():
    return render_template('/ITAdmin/itadminhome.html')


if __name__ == "__main__":
    app.run(debug=True)
