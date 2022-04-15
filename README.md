# etl-covid-19
This project simulates ETL process: extract data from two different .csv files, transform these and load to MySQL database. In addition, you can create chart which contains informations about countries' mortality per capita and send this chart to your email.

All code you need is contained in main.py file. But project contains one more exra file - 
pull_main_data.sh. This shell script pull .csv files from two different resourses. More informations about these .csv files you can get from these references: 

1. https://github.com/owid/covid-19-data/tree/master/public/data
2. https://github.com/OxCGRT/covid-policy-tracker

Before run main.py, please carefully read comments which I left in file.
Good luck.
