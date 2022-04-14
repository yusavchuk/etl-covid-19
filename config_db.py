#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 16:31:30 2022

@author: yu_savchuk
"""

hostname = 'localhost'
username = 'yusavchuk'
password = 'mydatabase'



import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='yusavchuk',
    password='mydatabase')

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE covid_19")