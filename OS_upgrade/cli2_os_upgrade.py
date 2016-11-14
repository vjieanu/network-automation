#!/usr/bin/env python
import time
import os
import re
import paramiko
import getpass
import base64

#variables
device = raw_input('Device to upgrade: ')
my_vrf = raw_input('VRF: ')
tftp_server = raw_input('TFTP Server: ')
image = raw_input('Name of the NX-OS file: ')
os_size = int(raw_input('Size in bytes of the NX-OS image: '))
md5_sum = raw_input('MD5 Checksum of the image: ')
myuser = raw_input('Username: ')
mypass = getpass.getpass('Password: ')

#cisco commands composer
cmd_dir_file = 'dir | include ' + image
cmd_dir = 'dir | include free'
cmd_up = 'copy tftp:'
cmd_1 = cmd_up + "//" + tftp_server + "/" + image + " " + "bootflash:" + " vrf " + my_vrf
md5_check = "show file " + image + " " + "md5sum"

#define clear-screen function
def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')

#define ssh connection function
def ssh_connect_no_shell(command):
	ssh_no_shell = paramiko.SSHClient()
	ssh_no_shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_no_shell.connect(device, port=22, username=myuser, password=mypass)
	stdin, stdout, stder = ssh_no_shell.exec_command(command)
	output = stdout.readlines()
	print '\n'.join(output)
	ssh_no_shell.close()

#main program
def main():
	print 'Program starting...\n'
	time.sleep(1)
	ssh_connect_no_shell('show version')
	ssh_connect_no_shell('dir')

#run main program in main file
if __name__ == '__main__':
	clear_screen()
	main()