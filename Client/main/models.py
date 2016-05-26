import sqlite3 as sqlite
from main.logger import *


# ----------------------------- Update token to IP Table -------------------------
def update_ip(token, server_addr):
    try:
        con = sqlite.connect("Client.db")
        cur = con.cursor()
        sql = "UPDATE IP SET token=?, server_addr=? WHERE id = 1"
        cur.execute(sql, (token, server_addr))
        con.commit()
        con.close()
    except sqlite.DatabaseError as e:
        logger.error(e.message)


# ----------------------------- Update token to IP Table -------------------------
def update_camera(shuttercount):
    try:
        con = sqlite.connect("Client.db")
        cur = con.cursor()
        sql = "UPDATE Camera SET shttercount=? WHERE id = 1"
        cur.execute(sql, (shuttercount,))
        con.commit()
        con.close()
    except sqlite.DatabaseError as e:
        logger.error(e.message)


# ---------------------------- Get Ip settings ----------------------------------------
def get_ip():
    data = " "
    try:
        con = sqlite.connect("Client.db")
        cur = con.cursor()
        result = cur.execute("select token, update_time, server_addr from IP")
        data = result.fetchone()
        con.close()
        return data
    except sqlite.DatabaseError as e:
        logger.error(e.message)
        return data


# ----------------------------- Get shutter count to IP Table -------------------------
def get_camera():
    data = " "
    try:
        con = sqlite.connect("Client.db")
        cur = con.cursor()
        sql = "SELECT shttercount FROM Camera"
        result = cur.execute(sql)
        data = result.fetchone()
        logger.debug(data)
        con.close()
        return data
    except sqlite.DatabaseError as e:
        logger.error(e.message)
        return data


# ------------------------- Detect if Table is empty or not. --------------------------
def detect_empty_db():
    con = sqlite.connect("Client.db")
    cur = con.cursor()
    result = cur.execute("select * from Users LIMIT 1")
    flag = result.fetchone()
    if flag:
        # Update
        flag = False
    else:
        # Insert
        flag = True
    return flag


# -------------------------- Get username and password -------------------------------------
def get_user_id():
    user_data = " "
    try:
        con = sqlite.connect("Client.db")
        cur = con.cursor()
        result = cur.execute("select username, password from Users LIMIT 1")
        user_data = result.fetchone()
        return user_data
    except sqlite.DatabaseError as e:
        logger.error(e.message)
        return user_data


# -------------------------- Update username and password -------------------------------------
def update_user_id(username, password):
    try:
        con = sqlite.connect("Client.db")
        cur = con.cursor()
        sql = "UPDATE Users SET username=?, password=? WHERE id = 1"
        cur.execute(sql, (username, password))
        con.commit()
        con.close()
    except sqlite.DatabaseError as e:
        logger.error(e.message)


# -------------------------- Initialize the tables -------------------------------------
def insert_user_id():
    username = 'admin'
    password = '123456'
    try:
        con = sqlite.connect("Client.db")
        cur = con.cursor()
        sql = "INSERT INTO Users(username, password) VALUES(?,?)"
        cur.execute(sql, (username, password))
        con.commit()
        sql = "INSERT INTO Camera(shttercount) VALUES(?)"
        cur.execute(sql, (" ",))
        con.commit()
        sql = "INSERT INTO IP(token, server_addr, update_time) VALUES(?, ?, ?)"
        cur.execute(sql, (" ", " ", " "))
        con.commit()
        con.close()
    except sqlite.DatabaseError as e:
        logger.error(e.message)
