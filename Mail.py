#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 17:07:55 2022

@author: yu_savchuk
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
sender = 'aruy.savchuk.work@gmail.com'
receiver = 'aruy11@ukr.net'
password='30l04ivyurahsr'
message = """From: From Person <from@fromdomain.com>
To: To Person <to@todomain.com>
Subject: SMTP e-mail test

This is a test e-mail message.
"""
'''
msg = MIMEMultipart()
msg.attach(MIMEText(open("/home/yu_savchuk/petProject/covidChart.pdf", mode='rb').read()))



email = yagmail.SMTP(user=sender, password='30l04ivyurahsr')
email.send(to='aruy11@ukr.net', subject='Only for check', 
           contents=message,
           attachments=msg)

'''
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()

    
server.login(sender, password)
        # Craft message (obj)
msg = MIMEMultipart()

message = 'what \nSend from Hostname: flsjfdl'
msg['Subject'] = 'It is only checj'
msg['From'] = sender
msg['To'] = receiver
        # Insert the text to the msg going by e-mail
msg.attach(MIMEText(message, "plain"))
        # Attach the pdf to the msg going by e-mail
with open("/home/yu_savchuk/petProject/covidChart.pdf", "rb") as f:
            #attach = email.mime.application.MIMEApplication(f.read(),_subtype="pdf")
    attach = MIMEApplication(f.read(),_subtype="pdf")
attach.add_header('Content-Disposition','attachment',
                  filename="/home/yu_savchuk/petProject/covidChart.pdf")
msg.attach(attach)
        # send msg
server.send_message(msg)
