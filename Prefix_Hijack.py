import re
import os
import requests
import ipaddress
import datetime
from telnetlib import *

def prefix_list():
# connecting to a remote website to import all the prefixes an ISP own's.
    connect = requests.get('remote file where prefixes where stored')
    temp_list = []
    prefix = re.findall('(\S+)\s+\S+\s+\S+',connect.text)
    if prefix:
        temp_list += prefix
    del temp_list[0:3]
    return(temp_list)

temp_list = prefix_list()
host = 'route-views.routeviews.org'
user = 'rviews'
conn =Telnet(host)
conn.write((user + "\n").encode('ascii'))
conn.write(("term len 0\n").encode('ascii'))
#prefix if needs to ignored as ISP can sell their prefix to other customers and the program shouldn't pull such prefixes.
ignore_prefix =['mutlihomed customer prefix list']
del temp_list[0:3]
for element in ignore_prefix:
    if temp_list.count(element) != 0:
        temp_list.remove(element)
    else:
        first_obj = ipaddress.ip_network(element)
        index = 0
        for check_overlap in temp_list:
            second_obj = ipaddress.ip_network(temp_list[index])
            if first_obj.overlaps(second_obj):
                del temp_list[index]
                break
            else:
                index += 1
current_date_time = datetime.datetime.now()
string_current_date_time = str(current_date_time.year)+'_'+str(current_date_time.month)+'_'+str(current_date_time.day)+'_Prefix_Hijack' 
try:
    os.makedirs(string_current_date_time)
    os.chdir(string_current_date_time)
except:
    os.chdir(string_current_date_time)    
length = len(temp_list)
index = 0
while index < length:
    ipv4 = re.search('\d+.\d+.\d+.\d+\/\d+',temp_list[index])
    if ipv4:
        conn.write(("show ip bgp "+temp_list[index]+" lon\n").encode('ascii'))
    index += 1
conn.write(("exit\n").encode('ascii'))
filename = host+'.txt'
fo = open(filename, 'w')
fo.write(conn.read_all().decode("utf-8"))
fo.flush()
fo.close() 
conn.close()
del temp_list

file = open(filename,'r')
fo = open('parsed_text.txt', 'w')
data = file.readline()
while data:
   parsed_text = re.search(r'(?:\*|\*>)\s+(\d+.\d+.\d+.\d+\/\d+\s+)?(\S+)(?:\s+\d+\s+|\s+\d+\s+\d+\s+)(\d+\s+.+)[ie]',data)
   if parsed_text:
    fo.write(str(parsed_text.group(1)))
    fo.write('\t\t')
    fo.write(str(parsed_text.group(2)))
    fo.write('\t\t')
    fo.write(str(parsed_text.group(3)))
    fo.write('\t\t\n')
    data = file.readline()
fo.close()
file.close()

fo = open('parsed_text.txt','r')
content = fo.readline()
while content:
    content_list = content.split()
    comcast_asn = ['prefix list']
    if content_list[0] != 'None':
        agg_prefix = content_list[0]
        if comcast_asn.count(content_list[-1]) == 0:
            print ('The prefix '+ content_list[0] + ' with next hop ' + content_list[1] + ' has a different ASN origin ' + content_list[-1])  
    else:
        if comcast_asn.count(content_list[-1]) == 0:
            print ('The prefix '+ agg_prefix + ' with next hop ' + content_list[1] + ' has a different ASN origin ' + content_list[-1])
    content = fo.readline()
fo.close()
os.remove('parsed_text.txt')
