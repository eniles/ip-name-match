#!/usr/bin/env python
import sys
from datetime import *
import csv
import urllib
import json
import time
import re
#import pandas
import psycopg2
import mycreds


def get_info(adress):
    #uses the API from http://freegeoip.net/ for lookup, all credit or issues with data should be directed to FreeGeoIP
    #note that IP lookups often show the address information for ISP rather than the end user
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

    #print(adress)
    #print("IP: ", result["ip"])
    #print("Country Name: ", result["country_name"])
    #print("Country Code: ", result["country_code"])
    #print("Region Name: ", result["region_name"])
    #print("Region Code: ", result["region_code"])
    #print("City: ", result["city"])
    #print("Zip Code: ", result["zip_code"])
    #print("Latitude: ", result["latitude"])
    #print("Longitude: ", result["longitude"])
    #print("Location link: " + "http://www.openstreetmap.org/#map=11/" + str(result["latitude"]) +"/" + str(result["longitude"]))
    return result

def redshift_query_getter(query):
    #Return data from str query from Redshift
    start = datetime.now()
    #Obtaining the connection to RedShift
    connection_string = "dbname='" + mycreds.redshift_db['dbname'] + "' port='5439' user='" + mycreds.redshift_db['user'] + "' password='" + mycreds.redshift_db['pass'] + "' host='" + mycreds.redshift_db['dburl'] + "'";
    #print "Connecting to \n        ->%s" % (connection_string)
    print("Connecting to database: " + mycreds.redshift_db['dburl'] + ":" + mycreds.redshift_db['dbname'])
    conn = psycopg2.connect(connection_string);
    cur = conn.cursor()

    ## DO THE THINGS
    cur.execute(query)
    #for row in cur.fetchall():
    #    print(row) 
    data=cur.fetchall()
    cur.close();
    conn.commit();
    conn.close();
    t_0 = datetime.now() - start
    print('Time to fetch data: %s' % t_0)
    return data

def csv_writer(data, path):
    #Write data to a CSV file path
    with open(path, "wb") as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        for line in data:
            writer.writerow(line)


def showhelp():
    print ("Usage: run_lookup.py input_file.csv output_file.csv")
    print ("Lookup geolocation for a set of names and IPs using http://freegeoip.net/, check if those names exist in your person database at that location, and output CSV of found persons")

if __name__ == "__main__": #code to execute if called from command-line
    inputs = sys.argv
    if len(inputs) < 3 or "--help" in inputs:
        showhelp()
    else:
        #print(inputs[1])
        #print(inputs[2])
        print("Let's get started...")

        f = open(inputs[1])
        ofile_path = inputs[2]
        reader = csv.reader(f)
        for row in reader:
            print("**********")
            csv_row = row 
            #print(csv_row)
            name = csv_row[2]
            if (name and csv_row[6]
                and re.match(r'^((\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])\.){3}(\d{1,2}|1\d{2}|2[0-4]\d|25[0-5])$', csv_row[6])
                ):
                print(name + " " + csv_row[6])
                firstname = name.split(' ',1)
                firstname = firstname[0]
                lastname = name.rsplit(' ',1)
                lastname = lastname[1]
                time.sleep(5)
                ip_lookup=get_info(csv_row[6])
                #print(ip_lookup)
                print("Returned City: ", ip_lookup["city"])
                #edit sql_query to fit the person database you're checking against 
                sql_query = "SELECT " + mycreds.id_col + "," + mycreds.fname_col + "," + mycreds.lname_col + "," + mycreds.city_col + "," + mycreds.state_col + "," + mycreds.zip_col + " FROM " + mycreds.tablename2 + " WHERE " + mycreds.deceased_col + " is null AND " + mycreds.fname_col + "=upper('" + firstname + "') AND " + mycreds.lname_col + "=upper('" + lastname + "') AND " + mycreds.city_col + "=upper('" + ip_lookup["city"] + "') AND " + mycreds.state_col+ "=upper('" + ip_lookup["region_code"] + "')  LIMIT 10;"
                #print(sql_query)
                sql_results=redshift_query_getter(sql_query)
                print(sql_results)
                no_results=len(sql_results)
                #write result to output csv if only one match, otherwise attempt to narrow down by zip code
                if no_results == 1:
                    print("WRITE MATCH: " + str(sql_results))
                    csv_writer(sql_results, ofile_path)
                elif no_results > 1:
                    print("too many results, attempting to narrow by zip code")
                    sql_query2 = "SELECT " + mycreds.id_col + "," + mycreds.fname_col + "," + mycreds.lname_col + "," + mycreds.city_col + "," + mycreds.state_col + "," + mycreds.zip_col + " FROM " + mycreds.tablename2 + " WHERE " + mycreds.deceased_col + " is null AND " + mycreds.fname_col + "=upper('" + firstname + "') AND " + mycreds.lname_col + "=upper('" + lastname + "') AND " + mycreds.city_col + "=upper('" + ip_lookup["city"] + "') AND " + mycreds.state_col+ "=upper('" + ip_lookup["region_code"] + "') AND " + mycreds.zip_col + "="+ ip_lookup["zip_code"] +" LIMIT 10;"
                    #print(sql_query2)
                    sql_results2=redshift_query_getter(sql_query2)
                    #print(sql_results2)
                    no_results2=len(sql_results2)
                    if no_results2 == 1:
                        print("WRITE MATCH: " + str(sql_results2))
                        csv_writer(sql_results2, ofile_path)
                    else:
                        print("NO MATCH: still too many results")
                else:
                    print("NO MATCH: no result")
            else:
                print("Skip header row")
        print("************************************************")
        f.close()
