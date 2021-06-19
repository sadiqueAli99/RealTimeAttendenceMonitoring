from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_mysqldb import MySQL
import bcrypt
import datetime
import uuid

app = Flask(__name__, template_folder="Templates")
app.secret_key = "many random bytes"
userID = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'ram2'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'ram'
mysql = MySQL(app)

# LOGIN
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password'].encode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usermaster WHERE Status=1 AND Email=%s", ( Email,))
        data = cur.fetchone()
        count = cur.rowcount
        if count > 0:
            global userID
            userID = data[0]
            if bcrypt.hashpw(Password, data[12].encode('utf-8')) == data[12].encode('utf-8'):
                session['Email'] = request.form['Email']
                if data[10] == 1:
                    cur.close()
                    flash("login success", 'success')
                    return render_template('/ITAdmin/itadminhome.html',usermaster=data)
                elif data[10] == 2:
                    cur.close()
                    flash("login success", 'success')
                    return render_template('/Admin/admindetails.html', usermaster=data)
                elif data[10] == 3:
                    cur.close()
                    flash("login success", 'success')
                    return render_template('/Manager/managerdetails.html',usermaster=data)
                else:
                    cur.close()
                    flash("login success", 'success')
                    return render_template('/Employee/emphome.html',usermaster=data)
            else:
                flash("Invalid Email or Password!!",'danger')
                return render_template('/CommonPage/login.html',usermaster=data)
        else:
            cur.close()
            flash("login failed",'danger')
            return render_template('/CommonPage/login.html')
    return render_template('/CommonPage/login.html')

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    if 'login' in session:
        return redirect('/')
    if request.method == 'POST':
        Email = request.form['Email']
        token = str(uuid.uuid4())
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM usermaster WHERE Email=%s",[Email])
        if res > 0:
            data = cur.fetchone()
            cur = mysql.connection.cursor()
            cur.execute("UPDATE usermaster SET token=%s WHERE Email=%s",[token,Email])
            mysql.connection.commit()
            cur.close()
            flash("Email already sent to your Email",'success')
            return redirect('/reset')
        else:
            flash("User not Found",'danger')
    return render_template('/CommonPage/forgot.html')

@app.route('/reset/<string:token>',methods=['GET','POST'])
def reset(token):
    if 'login' in session:
        return redirect('/')
    if request.method == 'POST':
        # Password = request.form['Password'].encode('utf-8')
        Password = request.form['Password'].encode('utf-8')
        Con_Password = request.form['Con_Password'].encode('utf-8')
        hash_Password = bcrypt.hashpw(Password, bcrypt.gensalt())
        token1 = str(uuid.uuid4())
        if Password != Con_Password:
            flash("Password do not Match","danger")
            return redirect('/reset')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usermaster WHERE token=%s", [token])
        user = cur.fetchone()
        if user:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE usermaster SET token=%s , Password=%s  WHERE token=%s", [token1, hash_Password,token ])
            mysql.connection.commit()
            cur.close()
            flash("Your Password Sucessfulluy Updated", 'success')
            return redirect('/')
        else:
            flash("Your token is Invalid", 'danger')
            return redirect('/')
    return render_template('/CommonPage/reset.html')

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
    cur.execute("SELECT * FROM userrolemaster order by UserRole ")
    Userrolemaster = cur.fetchall()
    cur.close()
    return render_template('/Admin/adminhome.html', usermaster=data, userrolemaster=Userrolemaster)

@app.route('/mydetails2')
def mydetails2():
    cur = mysql.connection.cursor()
    print(userID)
    cur.execute("SELECT * FROM usermaster WHERE Status=%s AND UserRole=%s AND EmployeeID=%s",(1,2,userID))
    data = cur.fetchall()
    cur.close()
    return render_template('/Admin/admindetails.html', usermaster=data)

@app.route('/home1')
def home1():
    return render_template('/Admin/adminhome.html')

@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        details = request.form
        Name = details['Name']
        Designation = details['Designation']
        Department = details['Department']
        ManagerId = details['ManagerId']
        City = details['City']
        Email = details['Email']
        Mobile = details['Mobile']
        Address = details['Address']
        UserRole = details['UserRole']
        LoginName = details['LoginName']
        Password = details['Password'].encode('utf-8')
        hash_Password=bcrypt.hashpw(Password,bcrypt.gensalt())
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usermaster WHERE Status=1 AND Name=%s", [Name])
        count = cur.rowcount
        if count > 0:
            flash("Name Already Existed",'danger')
            return redirect(url_for('Index'))
        cur.execute("SELECT * FROM usermaster WHERE Status=1 AND Email=%s", [Email])
        count = cur.rowcount
        if count > 0:
            flash("Email Already Existed",'danger')
            return redirect(url_for('Index'))
        cur.execute("SELECT * FROM usermaster WHERE Status=1 AND Mobile=%s", [Mobile])
        count = cur.rowcount
        if count > 0:
            flash("Number Already Existed",'danger')
            return redirect(url_for('Index'))
        else:
            cur.execute(
                "INSERT INTO usermaster (Name,Designation,Department,ManagerId,City,Email,Mobile,Address,UserRole,LoginName,Password,Status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (Name, Designation, Department, 1, City, Email, Mobile, Address, UserRole, LoginName,
                 hash_Password, 1))
            mysql.connection.commit()
            flash("Data Inserted Successfully",'success')
    return redirect(url_for('Index'))

@app.route('/delete/<string:EmployeeId>', methods=['GET'])
def delete(EmployeeId):
    flash("Record Has Been Deleted Successfully",'success')
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
        UserRole = details['UserRole']
        # LoginName = details['LoginName']
        # Password = details['Password']
        cur = mysql.connection.cursor()
        cur.execute(
            " UPDATE usermaster SET Name=%s ,Designation=%s , Department=%s , ManagerId=%s , City=%s , Email=%s , Mobile=%s , Address=%s ,UserRole=%s WHERE EmployeeId=%s",
            (Name, Designation, Department, ManagerId, City, Email, Mobile, Address, UserRole, EmployeeId))
        flash("Data Updated Successfully",'success')
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
        flash("Holiday Added",'success')
        details = request.form
        EventName = details['EventName']
        Date = details['Date']
        Year = details['Year']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO holidaycalendermaster(EventName,Date,Year,Status) VALUES(%s,%s,%s,%s)", [EventName, Date,Year,1,])
        mysql.connection.commit()
    return redirect(url_for('holiday'))


@app.route('/holidayupdate', methods=['POST', 'GET'])
def holidayupdate():
    if request.method == 'POST':
        details = request.form
        HolidayId=details['HolidayId']
        EventName = details['EventName']
        Date = details['Date']
        Year = details['Year']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE holidaycalendermaster SET EventName=%s,Date=%s, Year=%s WHERE HolidayId=%s", [EventName, Date, Year,HolidayId])
        flash("Holiday Updated",'success')
        mysql.connection.commit()
    return redirect(url_for('holiday'))

@app.route('/holidaydelete/<string:HolidayId>', methods=['GET'])
def holidaydelete(HolidayId):
    flash("Holiday Deleted",'success')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE holidaycalendermaster SET status=0 WHERE HolidayId =%s", [HolidayId])
    mysql.connection.commit()
    return redirect(url_for('holiday'))

    # MANAGER HOME PAGE - EMPLOYEE DETAILS

@app.route('/employeedetails')
def employeedetails():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM usermaster where Status=1")
    data = cur.fetchall()
    cur.close()
    return render_template('/Manager/mgrhome.html', usermaster=data)

@app.route('/mydetails3')
def mydetails3():
    cur = mysql.connection.cursor()
    print(userID)
    cur.execute("SELECT * FROM usermaster WHERE Status=%s AND UserRole=%s AND EmployeeID=%s",(1,3,userID))
    data = cur.fetchall()
    cur.close()
    return render_template('/Manager/managerdetails.html', usermaster=data)


@app.route('/pendingleave')
def pendingleave():
    cur = mysql.connection.cursor()
    cur.execute("SELECT leaves.leaveId , usermaster.Name, leaves.LeaveRequestDate , leaves.FromDate , leaves.ToDate , leaves.NumberofDays , leaves.Reason , leaves.LeaveApprovalStatus FROM leaves INNER JOIN usermaster ON leaves.EmployeeId = usermaster.EmployeeID WHERE LeaveApprovalStatus=0")
    data = cur.fetchall()
    cur.close()
    return render_template('/Manager/pendingleave.html', leaves=data)

@app.route('/accept/<string:leaveId>', methods=['GET'])
def accept(leaveId):
    flash("Leave Has Been Accepted Successfully",'success')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE leaves SET LeaveApprovalStatus=1  WHERE leaveId=%s", [leaveId])
    mysql.connection.commit()
    return redirect(url_for('pendingleave'))

@app.route('/reject/<string:leaveId>', methods=['GET'])
def reject(leaveId):
    flash("Leave Has Been Rejected Successfully",'success')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE leaves SET LeaveApprovalStatus=2  WHERE leaveId =%s", [leaveId])
    mysql.connection.commit()
    return redirect(url_for('pendingleave'))

@app.route('/monthlyattendance')
def monthlyattendance():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM monthlyattendancedashboard where Status=1 ")
    data = cur.fetchall()
    cur.close()
    return render_template('/Manager/monthlyattendance.html', monthlyattendancedashboard=data)

@app.route('/yearlyattendance')
def yearlyattendance():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM yearlyattendancedashboard where Status=1 ")
    data = cur.fetchall()
    cur.close()
    return render_template('/Manager/yearlyattendance.html', yearlyattendancedashboard=data)

@app.route('/home2')
def home2():
    return render_template('/Manager/mgrhome.html')

    # EMPLOYEE HOME PAGE

@app.route('/mydetails4')
def mydetails4():
    cur = mysql.connection.cursor()
    print(userID)
    cur.execute("SELECT * FROM usermaster WHERE Status=%s AND UserRole=%s AND EmployeeID=%s",(1,4,userID))
    data = cur.fetchall()
    cur.close()
    return render_template('/Employee/emphome.html', usermaster=data)

@app.route('/leave')
def leave():
    cur = mysql.connection.cursor()
    cur.execute("SELECT leaves.EmployeeId , usermaster.Name, leaves.LeaveRequestDate , leaves.FromDate , leaves.ToDate , leaves.NumberofDays , leaves.Reason , leaves.LeaveApprovalStatus FROM leaves INNER JOIN usermaster ON leaves.EmployeeId = usermaster.EmployeeID WHERE leaves.EmployeeId=%s",[userID])
    data = cur.fetchall()
    cur.close()
    return render_template('/Employee/leave.html', leaves=data)

@app.route('/leaveinsert', methods=['POST'])
def leaveinsert():
    curtime = datetime.datetime.now()  # current date
    formatted = curtime.strftime('%Y-%m-%d')  # convert your date in a string format before inserting it to your database
    if request.method == 'POST':
        flash("Leave Added",'success')
        details = request.form
        FromDate = details['FromDate']
        ToDate = details['ToDate']
        NumberofDays = details['NumberofDays']
        Reason = details['Reason']
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO leaves(EmployeeId,LeaveRequestDate,FromDate,ToDate,NumberofDays,Reason) VALUES(%s,%s,%s,%s,%s,%s)",
            (userID, formatted, FromDate, ToDate, NumberofDays, Reason))
        mysql.connection.commit()
    return redirect(url_for('leave'))

@app.route('/home3')
def home3():
    return render_template('/Employee/emphome.html')

# IT ADMIN HOME PAGE
@app.route('/itadminhome')
def itadminhome():
    cur = mysql.connection.cursor()
    cur.execute("SELECT  * FROM camra where status=1")
    data = cur.fetchall()
    cur.close()
    return render_template('/ITAdmin/itadminhome.html', camra=data)


@app.route('/mydetails1')
def mydetails1():
    cur = mysql.connection.cursor()
    print(userID)
    cur.execute("SELECT * FROM usermaster WHERE Status=%s AND UserRole=%s AND EmployeeID=%s",(1,1,userID))
    data = cur.fetchall()
    cur.close()
    return render_template('/ITAdmin/itadmindetails.html', usermaster=data)


@app.route('/Camerainsert', methods=['POST'])
def Camerainsert():
    if request.method == 'POST':
        flash("Data Inserted Successfully",'success')
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
    flash("Record Has Been Deleted Successfully",'success')
    cur = mysql.connection.cursor()
    cur.execute("UPDATE camra SET status=0  WHERE CamaraID=%s", [CamaraID])
    mysql.connection.commit()
    return redirect(url_for('itadminhome'))

@app.route('/Cameraupdate', methods=['POST', 'GET'])
def Cameraupdate():
    if request.method == 'POST':
        details = request.form
        CamaraID=details['CamaraID']
        CameraName = details['CameraName']
        Location = details['Location']
        cur = mysql.connection.cursor()
        cur.execute(
            " UPDATE camra SET CameraName=%s ,Location=%s  WHERE CamaraID=%s ",
            (CameraName, Location,CamaraID))
        flash("Data Updated Successfully",'success')
        mysql.connection.commit()
    return redirect(url_for('itadminhome'))

@app.route('/home')
def home():
    return render_template('/ITAdmin/itadminhome.html')

if __name__ == "__main__":
    app.run(debug=True)
