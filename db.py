import sqlite3
from flask import g



# from main import db

def connect_to_db():
    db = g.db = sqlite3.connect(r"C:\Users\Mishita Madnani\Akshay\Flask Project\testDB.db")
    db.row_factory = sqlite3.Row
    return db


def get_db():
    if not hasattr(g, "testDB"):
        g.testDB = connect_to_db()
    return g.testDB


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()