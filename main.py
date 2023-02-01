from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from db import *
import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testDB.db'

db = SQLAlchemy(app)


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), unique=False, nullable=False)
    last_name = db.Column(db.String(20), unique=False, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Name : {self.first_name}, Age: {self.age}"


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/create_customer", methods=["POST", "GET"])
def create_customer():
    if request.method == "POST":
        db = get_db()
        record = db.execute("INSERT INTO customers (name) values (?)", [request.form['name']])
        db.commit()
    return render_template("createCustomer.html")


@app.route("/create_order", methods=["POST", "GET"])
def create_order():
    db = get_db()
    customer_cursor = db.execute("select * from customers;")
    customers = customer_cursor.fetchall()
    if request.method == "POST":
        print(request.form, "---")
        # db = get_db()
        x = db.execute("INSERT INTO orders (order_no, customer_id, order_date) values (?, ?, ?)", [request.form['order_no'], request.form['customer'], request.form['order_date']])
        db.commit()
        order_id = x.lastrowid
        for i in range(int(request.form['inputs'])):
            db.execute("INSERT INTO orders_items (order_id, item_name, value) values (?, ?, ?)", [order_id, request.form[f'name{i+1}'], request.form[f'price{i+1}']])
            db.commit()
        print(x.fetchone(), x.lastrowid, "latest")
    return render_template("createOrder.html", customers = customers)


@app.route("/get_order", methods=["GET"])
def get_order():
    db = get_db()
    orderItem_cursor = db.execute("SELECT printf('%,d', sum(value)) as total_value, oi.order_id , o.order_no, STRFTIME('%d/%m/%Y', o.order_date)  as order_date, c.name  FROM orders_items oi join orders o on o.id = oi.order_id join customers c on c.id = o.customer_id group by oi.order_id ORDER BY o.order_date;")
    orderItem = orderItem_cursor.fetchall()
    orders = [dict(i) for i in orderItem]
    return render_template("showOrder.html", orders = orders)


@app.route("/get_top_10", methods=["GET"])
def get_top_10():
    db = get_db()
    orderItem_cursor = db.execute("SELECT sum(value) as total_value, c.name  FROM orders_items oi join orders o on o.id = oi.order_id join customers c on c.id = o.customer_id GROUP BY o.customer_id ORDER BY total_value DESC limit 10;")
    orderItem = orderItem_cursor.fetchall()
    orders = [dict(i) for i in orderItem]
    for i in orders:
        i["total_value"] = f'{i["total_value"]:,}'
    return render_template("showTop10Customers.html", orders = orders)


@app.route("/get_recent_buyers", methods=["GET"])
def get_recent_buyers():
    db = get_db()
    customer_cursor = db.execute("SELECT * from customers;")
    customers = customer_cursor.fetchall()
    customer_ls = []
    for i in customers:
        orders_cursor = db.execute(f"SELECT order_date from orders where customer_id={i['id']};")
        orders = orders_cursor.fetchall()
        defaultDate = (datetime.datetime.today() - datetime.timedelta(days=30))
        isRecent = True
        for j in orders:
            if datetime.datetime.strptime(j["order_date"], '%Y-%m-%d') <= defaultDate:
                isRecent = False
        if isRecent:
            customer_ls.append(i)
    return render_template("recentCustomers.html", customers = customer_ls)


 
if __name__ == "__main__":
    app.run(debug=True)