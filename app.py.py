import sqlite3
import razorpay
import smtplib
from datetime import datetime as dt
time=dt.now()
key_id="key_id"
key_secret="key_secret"  
from flask import Flask, redirect, request, render_template, url_for 

app=Flask(__name__,template_folder="templates",static_folder="static")  

@app.route('/')
def home():
    return render_template("index1.html")

@app.route('/form',methods=['GET','POST'])
def get_details():
    if(request.method=='POST' and request.form.get("username")!="" and request.form.get("amount")!=0 and request.form.get("email")!="" and len(request.form.get("contact"))==10 ):
        username=request.form.get("username")
        email=request.form.get("email")
        contact=request.form.get("contact")
        amount=int(request.form.get("amount"))   
        return redirect(url_for("checkout",amount=amount,username=username,contact=contact,email=email))
    return render_template("form1.html")

@app.route('/checkout/<int:amount>/<username>/<int:contact>/<email>',methods=['GET','POST']) 
def checkout(amount,username,contact,email):  
    client=razorpay.Client(auth=(key_id,key_secret)) 
    param={
        "amount":amount*100,
        "currency": "INR",
        "receipt": "donation",
        "partial_payment":False
        }    
    conn=sqlite3.connect("database.db")  
    id=int(conn.execute("select id from user order by id desc limit 1;").fetchone()[0])
    conn.execute(f"insert into user Values({id+1},'{username}',{amount},'{email}',{contact},'{time}');") 
    conn.commit()
    conn.close()
    order=client.order.create(data=param) 
    return render_template("pay1.html",order=order,username=username,contact=contact,email=email)

@app.route('/success',methods=['GET','POST']) 
def success(): 
    #extracting data from database 
    conn=sqlite3.connect("database.db")
    receiver_email=conn.execute("select email from user order by id desc limit 1; ")
    amount=conn.execute("select amount from user order by id desc limit 1; ").fetchone()[0] 
    name=conn.execute("select name from user order by id desc limit 1; ").fetchone()[0]
    mailto=receiver_email.fetchone()[0] 
    conn.commit()
    conn.close()  

    #sending email  for the payment done
    password="your_app_password" 
    email="your_email" 
    connection=smtplib.SMTP("smtp.gmail.com")
    connection.starttls()
    connection.login(user=email,password=password)
    connection.sendmail(from_addr=email,to_addrs=mailto,msg=f"Subject:Invoice\n\nThank you very much completing the Payment and being a change in someone's life.\nInvoice\nName:{name}\nAmount paid:Rs.{amount}\nTransaction id: 1234567890\nHave a nice day! ")
    connection.close()  
    return render_template("success.html",amount=amount)

app.run(debug = True)
