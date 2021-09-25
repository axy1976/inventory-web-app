import MySQLdb
from flask import Flask, render_template, redirect, url_for, request
from MySQLdb.cursors import Cursor
from flask_mysqldb import MySQL
from datetime import datetime
import yaml

app = Flask(__name__)

# DATABASE Configuration
db = yaml.load(open('db.yaml'), Loader=yaml.FullLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
 
mysql = MySQL(app)

def __fetching(str_qury):
    try:
        cursor = mysql.connection.cursor()
        resultValues = cursor.execute(str_qury)
        if resultValues >= 0:
            Result = cursor.fetchall()
            msg = ""
        else:
            msg = "Table is empty "
        return [Result,msg]
    except:
        msg = "Database Connectivity Error "
        return [[],msg]

@app.route("/")
def index():
    return redirect("/product")

@app.route("/product")
def product():
    arg = __fetching("select * from product")
    return render_template("index.html", args = arg[0], messages = arg[1])

@app.route("/location")
def location():
    arg = __fetching("select * from location")
    return render_template("location.html", args = arg[0], messages = arg[1])

def __productbalance():
    results = []
    datas = (__fetching("select * from productmovement"))[0]
    if datas :
        for j,data in enumerate(datas):
            if datas[0][0] == data[0]:
                results.append([j+1,data[4],data[3],data[5],data[0]])
            else:
                if data[2] != "" and data[3] != "":
                    temp = data[5]
                    for i,val in enumerate(results):
                        if val[2] == data[2] and val[1] == data[4]:
                            if val[3] >= temp:
                                val[3] = val[3] - temp
                                results[i][3] = val[3]
                                temp = 0
                            if val[3] == 0:
                                results.remove(val)
                        if temp == 0:
                            results.append([j+1,data[4],data[3],data[5],data[0]])
                            break
                elif data[2] != "" and data[3] == "":
                    temp = data[5]
                    for i,val in enumerate(results):
                        if val[2] == data[2] and val[1] == data[4]:
                            if val[3] >= temp:
                                val[3] = val[3] - temp
                                results[i][3] = val[3]
                                temp = 0
                            if val[3] == 0:
                                results.remove(val)
                        if temp == 0:
                            break
                elif data[2] == "" and data[3] != "":
                    flag = True
                    for i,val in enumerate(results):
                        if val[2] == data[3] and val[1] == data[4]:
                            val[3] = val[3] + data[5]
                            results[i][3] = val[3]
                            flag = False
                    if flag:
                        results.append([j+1,data[4],data[3],data[5],data[0]])
    return results


@app.route("/movements")
def movements():
    arg1 = __fetching("select * from product")
    arg2 = __fetching("select * from location")
    arg3 = __fetching("select * from productmovement")
    return render_template("movements.html", ProductDetails = arg1[0], LocationList = arg2[0], Movements = arg3[0], ProductBalance = __productbalance(), messages = arg1[1])

def __queries(qry,args):
    Message = ""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(qry,args)
        mysql.connection.commit()
        cursor.close()
    except MySQLdb.IntegrityError:
        Message = "Duplicate data cannot be accepted here "
    except:
        Message = "Database Connectivity Error "
    return Message

@app.route("/AddProduct", methods=['GET', 'POST'])
def AddProduct():
    Message = ""
    if request.method == 'POST':
        pid = request.form["txtpid"]
        Message = __queries("INSERT INTO product VALUES (%s)",[pid])
    return render_template('./index.html',args = (__fetching("SELECT * FROM product"))[0], messages = Message)
        
@app.route("/UpdateProduct", methods=['GET', 'POST'])
def UpdateProduct():
    Message = ""
    if request.method == 'POST':
        oldpid = request.form["oldproduct"]
        newpid = request.form["newproduct"]
        Message = __queries("UPDATE product SET product_id = %s WHERE product_id = %s",[newpid,oldpid])
    return render_template('./index.html',args = (__fetching("SELECT * FROM product"))[0],messages = Message)
    
@app.route("/DeleteProduct", methods=['GET','POST'])
def DeleteProduct():
    if request.method == 'POST':
        dpid = request.form['dpid']
        __queries("DELETE FROM product WHERE product_id = %s",[dpid])
    return redirect('/product')

@app.route("/AddLocation", methods=['GET', 'POST'])
def AddLocation():
    Message = ""
    if request.method == 'POST':
        lid = request.form["txtlid"]
        Message = __queries("INSERT INTO location VALUES (%s)",[lid])
    return render_template('./location.html',args = (__fetching("SELECT * FROM location"))[0] ,messages = Message)
        
@app.route("/UpdateLocation", methods=['GET', 'POST'])
def UpdateLocation():
    Message = ""
    if request.method == 'POST':
        oldlid = request.form["oldlocation"]
        newlid = request.form["newlocation"]
        Message = __queries("UPDATE location SET location_id = %s WHERE location_id = %s",[newlid,oldlid])
    return render_template('./location.html',args = (__fetching("SELECT * FROM location"))[0] ,messages = Message)
    
@app.route("/DeleteLocation", methods=['GET','POST'])
def DeleteLocation():
    if request.method == 'POST':
        dlid = request.form['dlid']
        __queries("DELETE FROM location WHERE location_id = %s",[dlid])
    return redirect('/location')

def __balancer(froml,tol,pid,qnty):
    datas = __productbalance()
    if froml == "" and tol != "":
        return "SUCCESS"
    elif froml != "":
        if datas:
            for data in datas:
                if data[2] == froml and data[1] == pid and data[3] >= qnty:
                    return "SUCCESS"
            return pid+" is not availabel at "+froml
        else:
            return pid+" is not availabel at "+froml
    else:
        return "!! Invalid Entry !!"

@app.route("/AddMovement", methods=['GET', 'POST'])
def AddMovement():
    Message = ""
    timestamp = datetime.now()
    if request.method == 'POST':
        froml = request.form['fromlocation']
        tol = request.form['tolocation']
        pid = request.form['productid']
        qty = request.form['txtqty']
        result = __balancer(froml,tol,pid,int(qty))
        if result == "SUCCESS":
            Message = __queries("INSERT INTO productmovement (timestamp,from_location,to_location,product_id,qty)VALUES(%s,%s,%s,%s,%s)",[timestamp,froml,tol,pid,qty])
        else:
            Message = result
    return render_template('/movements.html',ProductDetails = (__fetching("SELECT * FROM product"))[0], LocationList = (__fetching("SELECT * FROM location"))[0], Movements = (__fetching("SELECT * FROM productmovement"))[0], ProductBalance = __productbalance() ,messages = Message)
    
@app.route("/UpdateMovement", methods=['GET', 'POST'])
def UpdateMovement():
    Message = ""
    timestamp = datetime.now()
    if request.method == 'POST':
        mid = request.form['movementid']
        froml = request.form['fromlocation']
        tol = request.form['tolocation']
        pid = request.form['productid']
        qty = request.form['txtqty']
        Message = __queries("UPDATE productmovement SET timestamp=%s,from_location=%s,to_location=%s,product_id=%s,qty=%s WHERE movement_id = %s",[timestamp,froml,tol,pid,qty,mid])
    return render_template('/movements.html',ProductDetails = (__fetching("SELECT * FROM product"))[0], LocationList = (__fetching("SELECT * FROM location"))[0], Movements = (__fetching("SELECT * FROM productmovement"))[0], ProductBalance = __productbalance() ,messages = Message)
    
@app.route("/DeleteMovement", methods=['GET', 'POST'])
def DeleteMovement():
    if request.method == 'POST':
        mid = request.form['movementid']
        __queries("DELETE FROM productmovement WHERE movement_id = %s",[mid])
    return redirect('/movements')

# app.run(host='localhost', port=5000)