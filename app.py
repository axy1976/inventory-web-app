from flask import Flask, render_template, redirect, url_for, request
from MySQLdb.cursors import Cursor
from flask_mysqldb import MySQL
from datetime import datetime
import yaml

app = Flask(__name__)

# DATABASE Configuration
db = yaml.load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
 
mysql = MySQL(app)

@app.route("/")
def index():
    cursor = mysql.connection.cursor()
    resultValues = cursor.execute("select * from product")
    if resultValues >= 0:
        Products = cursor.fetchall()
    resultValues = cursor.execute("select * from location")
    if resultValues >= 0:
        locations = cursor.fetchall()
    resultValues = cursor.execute("select * from productmovement")
    if resultValues >= 0:
        movements = cursor.fetchall()
    return render_template("index.html",ProductDetails = Products, LocationList = locations, Movements = movements)

@app.route("/AddProduct", methods=['GET', 'POST'])
def AddProduct():
    if request.method == 'POST':
        pid = request.form["txtpid"]
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO product VALUES (%s)",[pid])
        mysql.connection.commit()
        cursor.close()
    return redirect('/')
        
@app.route("/UpdateProduct", methods=['GET', 'POST'])
def UpdateProduct():
    if request.method == 'POST':
        oldpid = request.form["oldproduct"]
        newpid = request.form["newproduct"]
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE product SET product_id = %s WHERE product_id = %s",[newpid,oldpid])
        mysql.connection.commit()
        cursor.close()
    return redirect('/')
    
@app.route("/DeleteProduct", methods=['GET','POST'])
def DeleteProduct():
    if request.method == 'POST':
        dpid = request.form['dpid']
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM product WHERE product_id = %s",[dpid])
        mysql.connection.commit()
        cursor.close()
    return redirect('/')

@app.route("/AddLocation", methods=['GET', 'POST'])
def AddLocation():
    if request.method == 'POST':
        lid = request.form["txtlid"]
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO location VALUES (%s)",[lid])
        mysql.connection.commit()
        cursor.close()
    return redirect('/#nav-location')
        
@app.route("/UpdateLocation", methods=['GET', 'POST'])
def UpdateLocation():
    if request.method == 'POST':
        oldlid = request.form["oldlocation"]
        newlid = request.form["newlocation"]
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE location SET location_id = %s WHERE location_id = %s",[newlid,oldlid])
        mysql.connection.commit()
        cursor.close()
    return redirect('/#nav-location')
    
@app.route("/DeleteLocation", methods=['GET','POST'])
def DeleteLocation():
    if request.method == 'POST':
        dlid = request.form['dlid']
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM location WHERE location_id = %s",[dlid])
        mysql.connection.commit()
        cursor.close()
    return redirect('/#nav-location')

@app.route("/AddMovement", methods=['GET', 'POST'])
def AddMovement():
    timestamp = datetime.now()
    if request.method == 'POST':
        froml = request.form['fromlocation']
        tol = request.form['tolocation']
        pid = request.form['productid']
        qty = request.form['txtqty']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO productmovement (timestamp,from_location,to_location,product_id,qty)VALUES(%s,%s,%s,%s,%s)",[timestamp,froml,tol,pid,qty])
        mysql.connection.commit()
        cursor.close()
    return redirect('/#nav-movement')

@app.route("/UpdateMovement", methods=['GET', 'POST'])
def UpdateMovement():
    timestamp = datetime.now()
    if request.method == 'POST':
        mid = request.form['movementid']
        froml = request.form['fromlocation']
        tol = request.form['tolocation']
        pid = request.form['productid']
        qty = request.form['txtqty']
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE productmovement SET timestamp=%s,from_location=%s,to_location=%s,product_id=%s,qty=%s WHERE movement_id = %s",[timestamp,froml,tol,pid,qty,mid])
        mysql.connection.commit()
        cursor.close()
    return redirect('/#nav-movement')

@app.route("/DeleteMovement", methods=['GET', 'POST'])
def DeleteMovement():
    if request.method == 'POST':
        mid = request.form['movementid']
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM productmovement WHERE movement_id = %s",[mid])
        mysql.connection.commit()
        cursor.close()
    return redirect('/#nav-movement')

# app.run(host='localhost', port=5000)