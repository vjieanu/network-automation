#!/usr/bin/python

import base64
import time
import getpass

#variables

device = raw_input('Device to upgrade: ')
my_vrf = raw_input('VRF: ')
tftp_server = raw_input('TFTP Server: ')
image = raw_input('Name of the NX-OS file: ')
os_size = int(raw_input('Size in bytes of the NX-OS image: '))
md5_sum = raw_input('MD5 Checksum of the image: ')
myuser = raw_input('Username: ')
mypass = getpass.getpass('Password: ')

cmd_dir_file = 'dir | include ' + image
cmd_dir = 'dir | include free'
cmd_up = 'copy tftp:'
cmd_1 = cmd_up + "//" + tftp_server + "/" + image + " " + "bootflash:" + " vrf " + my_vrf
md5_check = "show file " + image + " " + "md5sum"  

#use paramiko ssh client
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#check if file is already on the flash

ssh.connect(device, port=22, username=myuser, password=mypass)
stdin, stdout, stder = ssh.exec_command(cmd_dir_file)
output_of_dir_file = stdout.readlines()
#print '\n'.join(output_of_dir_file)
ssh.close()

if any(image in s for s in output_of_dir_file):
    print '\nThe file you are trying to upload is already there.'
    print 'Program will exit now.'
    exit()
else:
    time.sleep(1)
    
#perform ssh connection
ssh.connect(device, port=22, username=myuser, password=mypass)
stdin, stdout, stder = ssh.exec_command(cmd_dir)
output = stdout.readlines()
ssh.close()

#store the flash free space information
for line in output:
    if 'bytes' in line:
        bytes_count = int(line.split()[0].strip('('))

#definition of interactive menu
try:
    from msvcrt import getch
except ImportError:
    def getch():
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

#start the interactive menu
print "Are you sure? (y/n)"
while True:
    char = getch()
    if char.lower() == "y":
        print char

        #check disk-space and perform upgrade
        if os_size < bytes_count:
            print "Performing upgrade..."
            ssh.connect(device, port=22, username=myuser, password=mypass)
            stdin, stdout, stder = ssh.exec_command(cmd_1)
            output1 = stdout.readlines()
            print '\n'.join(output1)
            print 'Press any key to continue'
            ssh.close()         
        else:
            print "Upgrade cannot continue due not enough space on the flash"
    else:
    	print "Program End"
    	break

#Verifify the MD5 checksum
ssh.connect(device, port=22, username=myuser, password=mypass)
stdin, stdout, stder = ssh.exec_command(md5_check)
output2 = stdout.readlines()
#print '\n'.join(output2)
ssh.close()

#compare the md5 checksum and display upload result
if any(md5_sum in s1 for s1 in output2):
    print "Upload Succesfull. " + "md5 " + md5_sum + " " + "checksum verified."
else:
    print "Upload Failed. " + "Original Checksum " + md5_sum + " " + "differ from calculated checksum"

#end program
