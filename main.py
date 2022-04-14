#!/usr/bin/bash python

#main dataset 'https://covid.ourworldindata.org/data/owid-covid-data.csv'
#dataset with lockdowns 'https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv'

#Before run the program in console you must enter this command 'chmod +x main.py'
#This command give permission to execute .sh files

import subprocess
import pandas as pd 
import mysql.connector
import matplotlib.pyplot as plt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication




class Data:
    """Some coments"""
    
    def __init__(self, mainfilename, extrafilename):
        self.mainfilename = mainfilename
        self.extrafilename = extrafilename
        
    def pull_files(self):
        subprocess.call(['sh', './pull_main_data.sh', self.mainfilename,
                         self.extrafilename])

    def create_df_main(self):
        
        file_cols = ['location', 'date', 'total_cases', 'new_cases', 'total_deaths',
                      'new_deaths', 'hosp_patients', 'total_tests', 'new_tests',
                      'people_vaccinated', 'people_fully_vaccinated', 'new_vaccinations',
                      'population']
        
        df_main = pd.DataFrame()
        
        full_df = pd.read_csv(self.mainfilename + '.csv', low_memory=False,
                              chunksize=50000)
        for chunk in full_df:
            chunk = chunk[file_cols]
            chunk['date'] = pd.to_datetime(chunk['date'], format='%Y-%m-%d')
            
            df_main = pd.concat([df_main, chunk])
        
        df_main.rename(columns={'location' : 'CountryName', 'date' : 'Date'},
                       inplace=True)

        return df_main
    
    def create_df_lockdown(self):
        
        lockdown_columns = ['CountryName', 'RegionName','Date', 'C1_School closing',
                            'C2_Workplace closing', 'C3_Cancel public events',
                            'C4_Restrictions on gatherings', 'C5_Close public transport',
                            'C6_Stay at home requirements', 'C7_Restrictions on internal movement',
                            'C8_International travel controls', 'E1_Income support']
        
        df_lockdown = pd.DataFrame()
        
        full_df = pd.read_csv(self.extrafilename + '.csv', low_memory=False,
                              chunksize=50000)
        for chunk in full_df:
            chunk = chunk[lockdown_columns]
            chunk = chunk[chunk['RegionName'].isnull()]
            chunk['Date'] = pd.to_datetime(chunk['Date'], format='%Y%m%d')
        
            df_lockdown = pd.concat([df_lockdown, chunk]) 
        
        df_lockdown.drop('RegionName', axis=1,inplace=True)
        
        return df_lockdown 
    
    def create_final_table(self):
        
        df_main = self.create_df_main()
        df_lockdown = self.create_df_lockdown()
        
        df_final = pd.merge(df_main, df_lockdown, how='inner', 
                             on=['CountryName', 'Date'])
        df_final.fillna(0, inplace=True)
        
        return df_final





class DataBase:
    
    def __init__(self, hostname, username, password, dbname='covid_19'):
        #Enter your personal hostname, username, password from mysql db
        self.hostname = hostname
        self.username = username
        self.password = password
        self.dbname = dbname
        
    
    def _connect_db(self):
        
        try:
            con_my = mysql.connector.connect(
                host=self.hostname,
                database = self.dbname,
                user=self.username,
                password=self.password)
            if con_my.is_connected():
                cursor = con_my.cursor()
                return cursor, con_my
        except Exception as exp:
            print('Connection refused:', exp)
            
            
            
    def create_db(self):
        
        try:
            con_my = mysql.connector.connect(
                host=self.hostname,
                user=self.username,
                password=self.password)
            print('Succesfully conected to mysql')
            
            if con_my.is_connected():
                cursor = con_my.cursor()
                create_query = f'''CREATE DATABASE {self.dbname}'''
                cursor.execute(create_query)
                print('Your db created')
                
            
        except Exception as exp:
            print('Connection refused:', exp)
            print('DataBase not created')
        
        finally:
            con_my.close()

    def create_table(self):
        cursor, con_my = self._connect_db()
        
        cursor.execute("CREATE TABLE covid_by_country(CountryName varchar(30),\
                Date DATE, total_cases int, new_cases int, total_deaths int,\
                new_deaths int, hosp_patients int, total_tests int,\
                new_tests int, people_vaccinated int, people_fully_vaccinated int,\
                new_vaccinations int, population int, C1_School_closing int, \
                C2_Workplace_closing int, C3_Cancel_public_events int,\
                C4_Restrictions_on_gatherings int, C5_Close_public_transport int,\
                C6_Stay_at_home_requirements int, C7_Restrictions_on_internal_movement int,\
                C8_International_travel_controls int, E1_Income_support int)")
        print('Table created')
        con_my.commit()    
        con_my.close()
        
    def fill_table(self, df):
        cursor, con_my = self._connect_db()
    
        insert_query = f"""INSERT INTO {self.dbname}.covid_by_country VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,\
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        for i, row in df.iterrows():
            cursor.execute(insert_query, tuple(row))
        
        con_my.commit()    
        con_my.close()
        
        
        

class Chart:
    
    def __init__(self, df, filename, ntop_countries=10):
        self.df = df
        self.filename = filename
        self.ntop_countries = ntop_countries
    
    def get_statistic(self):
        
        df = self.df.groupby('CountryName').max()[['total_deaths', 'population']]
        df['%_deaths_by_population'] = df['total_deaths'] / df['population'] * 100
        df.drop(['total_deaths', 'population'], axis=1, inplace=True)
        df.sort_values(by='%_deaths_by_population', inplace=True, ascending=False)
        df = df.head(self.ntop_countries).sort_values('%_deaths_by_population')
        
        return df
        
    def save_pdf(self):
        
        plt.savefig(self.filename +'.pdf')
    
    def create_chart(self):
        
        df_draw = self.get_statistic()
        df_draw['%_deaths_by_population'].plot(kind = 'barh')
        plt.xlabel('%_deaths_by_population')
        plt.title('Mortality statistics')
         

class Mail:
    
    def __init__(self, sender='youremailadress',
                 receiver='receiveremaladress',password='yourpassword'):
        #Enter in class construtor your personal/work email, 
        #receiver's email and your password from email
        
        self.sender = sender
        self.receiver = receiver
        self.password = password
        
    def send_mail(self, message, chart):
        
        try:
          
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender, self.password)
            
            msg = MIMEMultipart()
            msg['Subject'] = 'The highest mortality rate'
            msg['From'] = self.sender
            msg['To'] = self.receiver

            msg.attach(MIMEText(message, "plain"))
     
            with open(chart.filename + '.pdf', "rb") as f:
                attach = MIMEApplication(f.read(),_subtype="pdf")
            
            attach.add_header('Content-Disposition','attachment',
                              filename=chart.filename + '.pdf')

            msg.attach(attach)
            server.send_message(msg)
            print('Letter has been sent)))')

        except Exception as exp:
            print('Your password or email is incorrect')
            print(exp)
            


message = """
Hello, Dear boss.
I sent you mortality statistics per capita, as are you requested.
Chart in the attachment.

Respectfully, 
Savchuk Yuriy
Data Enginner
+38098475____
   
            """
            
if __name__ == '__main__':
    
    data = Data('maindata', 'lockdowns')
    data.pull_files()
    df_final = data.create_final_table()
    
    db = DataBase(hostname='localhost', username='yusavchuk', 
                  password='mydatabase')
    db.create_db()
    db.create_table()
    db.fill_table(df_final)
    
    graph = Chart(df_final, 'covidChart')
    graph.create_chart()
    graph.save_pdf()   
    
    mail = Mail()
    mail.send_mail(message, graph)



















