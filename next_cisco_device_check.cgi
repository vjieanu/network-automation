#!/usr/bin/python
import cgi
import cgitb
cgitb.enable()
form = cgi.FieldStorage()

#import variables from web-form
mydevice = form.getvalue('mydevice')

print 'Content-type: text/html\r\n\r'
print '<html>' #start of html output

#program start

import paramiko
import base64
b64pass = base64.b64decode("Y2ljaTE=")
b64usr = base64.b64decode("dmppZWFudQ==")
sh_ver = 'show version'

#initiate ssh connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#run command on device and get read the output
ssh.connect(mydevice, port=22, username=b64usr, password=b64pass)
stdin, stdout, stder = ssh.exec_command(sh_ver)
output_sh_ver = stdout.readlines()
ssh.close()

#reading the input and parsing

print mydevice
print('<br />')

for line in output_sh_ver:
    if 'IOS' in line:
        print "Device type is: Cisco Catalyst"

for line in output_sh_ver:
    if 'uptime' in line:
        myuptime = (line.split()[3:0].strip('('))        

#printing output

print "Uptime: "+ myuptime
print('<br />')

#program end

print '</html>'	#end html page
