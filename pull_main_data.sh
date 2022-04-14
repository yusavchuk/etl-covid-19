#!/usr/bin/bash

wget "https://covid.ourworldindata.org/data/owid-covid-data.csv" 
mv owid-covid-data.csv $1.csv

wget "https://raw.githubusercontent.com/OxCGRT/covid-policy-tracker/master/data/OxCGRT_latest.csv"
mv OxCGRT_latest.csv $2.csv
