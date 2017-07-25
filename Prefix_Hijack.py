import re
import os
import requests
import ipaddress
import datetime
from telnetlib import *

def prefix_list():
    connect = requests.get("http://ipctls-ch2-a1p.sys.comcast.net/addrtool/reference_pages/nipeo_ip.txt")
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
ignore_prefix =['24.104.0.0/17','24.104.128.0/19', '24.149.128.0/17','50.200.0.0/13','50.232.0.0/13','50.224.0.0/12','64.235.160.0/19','64.56.32.0/19','64.78.64.0/18','66.240.0.0/18','72.55.0.0/17','74.81.128.0/19', '107.0.0.0/15','208.39.128.0/18', '208.110.192.0/19', '209.23.192.0/18', '216.45.128.0/17','173.8.0.0/13','173.160.0.0/13','198.0.0.0/16']
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
    comcast_asn = ['7922','36733','33662','33491','7015','33659','33651','33667','7016','33668','33657','33490','7725','33287','33652','33650','13385','13367','22909','21508','20214','11025','33489','36732','33661','33653','22258','33656','33665','33666','33654','33655','33664','33660']
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
