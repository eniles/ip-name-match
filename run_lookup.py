#!/usr/bin/env python
import sys
from datetime import *
import urllib
import json
import time
import re
#import pandas
import psycopg2
import mycreds


def get_info(adress):
    #print("************************************************")

    api = "http://freegeoip.net/json/" + adress
    try:
        result = urllib.urlopen(api).read()
        result = str(result) 
        #result = result[2:len(result)-3]
        result = json.loads(result)
    except Exception as e:
        print("Could not find: ", address)
        print(e)
        print(result)
        return None

    print(adress)
    print("IP: ", result["ip"])
    print("Country Name: ", result["country_name"])
    print("Country Code: ", result["country_code"])
    print("Region Name: ", result["region_name"])
    print("Region Code: ", result["region_code"])
    print("City: ", result["city"])
    print("Zip Code: ", result["zip_code"])
    print("Latitude: ", result["latitude"])
    print("Longitude: ", result["longitude"])
    print("Location link: " + "http://www.openstreetmap.org/#map=11/" + str(result["latitude"]) +"/" + str(result["longitude"]))
    return result

def redshift_query_getter(query):
    #Return data from str query from Redshift
    start = datetime.now()
    #Obtaining the connection to RedShift
    connection_string = "dbname='" + mycreds.redshift_db['dbname'] + "' port='5439' user='" + mycreds.redshift_db['user'] + "' password='" + mycreds.redshift_db['pass'] + "' host='" + mycreds.redshift_db['dburl'] + "'";
    print "Connecting to \n        ->%s" % (connection_string)
    conn = psycopg2.connect(connection_string);
    cur = conn.cursor()

    ## DO THE THINGS
    cur.execute(query)
    for row in cur.fetchall():
        print(row)    

    cur.close();
    conn.commit();
    conn.close();
    t_0 = datetime.now() - start
    print('Time to fetch data: %s' % t_0)
    return None

def showhelp():
    print ("Usage: geoip address [address]...")
    print ("find gelocation of IP addresses and host names, using http://freegeoip.net/")

if __name__ == "__main__": #code to execute if called from command-line
    inputs = sys.argv
    if len(inputs) < 2 or "--help" in inputs:
        showhelp()
    else:
        #print(inputs[1])
        print("Let's get started...")

        sql_query = "SELECT state_code FROM " + mycreds.tablename1 + " WHERE deceased!=1 LIMIT 10;"
        redshift_query_getter(sql_query)

        for line in open(inputs[1]):
        #for address in inputs[1:]:
            csv_row = line.split(",") #returns a list ["1","50","60"]
            #print(csv_row)
            if (csv_row[2] and csv_row[6]
                and re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', csv_row[6])
                ):
                print(csv_row[2] + " " + csv_row[6])
                time.sleep(15)
                ip_lookup=get_info(csv_row[6])
                #print(ip_lookup)
                print("Returned City: ", ip_lookup["city"])

        print("************************************************")
