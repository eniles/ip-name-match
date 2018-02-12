# ip-name-match

developed for Python 2.7.10

Usage: run_lookup.py input_file.csv output_file.csv
Lookup geolocation for a set of names and IPs using http://freegeoip.net/, check if those names exist in your person database at that location, and output CSV of found persons

Quick and dirty Python script to:
-Read in data from a CSV file with a list of persons and IP addresses (from an online form or whatnot) and look up City/Zip for an IP from freegeoip.net (expects a CSV file with ID in first column, FULLNAME in third column, and IPADDR in sixth column)
-Look up City/Zip for each IP from freegeoip.net
-Log into a database specified in a mycreds.py file and for each name see if that name exists at that location in your person database
-Write a row to the output CSV with some info from your person database if a single match exists

The match as written here is pretty dumb, looking at exact matches on name/city/state, and then retrying with exact matches on name/city/state/zip if there were multiple results returned.  The code and SQL could be easily modified to do a more complex match or use improved logic.
