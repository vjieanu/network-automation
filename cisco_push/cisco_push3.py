#!/usr/bin/env python3
import os
import argparse
import paramiko
import getpass
import socket
import re
import sys
import time

# Define command line arguments and global variables
def args():
	parser = argparse.ArgumentParser(description='Python Program to configure Cisco switches. Use with care.')
	parser.add_argument('--hosts', help='Specify a hosts file', required=True)
	parser.add_argument('--commands', help='Specify a commands file', required=True)
	arg = vars(parser.parse_args())
	global main_menu_actions, hosts_file, commands_file, vlan_cfg
	hosts_file = arg['hosts']
	commands_file = arg['commands']
	main_menu_actions = {
		'main_menu': main_menu,
		'1': sh_host_list,
		'2': sh_commands_list,
		'3': yes_no,
		'0': prog_exit}

'''Define menus and menu calls and menu navigation'''

# Clear screen function	
def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')

# Navigate to Main Menu function
def press_return():
    print ('\n\nPress enter to go back\n')
    input(' >> ')
	
def end_write():
	remote_conn.send('end\n')
	remote_conn.send('wr mem\n')
	remote_conn.send('\n')

# Call menu items function
def exec_menu(menu_actions, menu_return, choice):
	clear_screen()
	try:
		menu_actions[choice]()
	except KeyError:
		print ('Invalid Selection, Please Try Again.\n')
		time.sleep(1)
		menu_return()    

# Exit program function
def prog_exit():
    sys.exit()

def enter_config_mode():
	print ('\t*** Entering configure terminal mode *** \n')
	remote_conn.send('conf t\n')
	time.sleep(1)

''' Define menu actions '''

# Show what host file contains
def sh_host_list():
    hosts = open(hosts_file, 'r')
    print ('\n\n\tHosts in file: \n')
    for x in hosts:
        print ('\t\t' + x.strip('\n'))
    print ('\n\n')
    hosts.close()
    press_return()
    main_menu()

# Show what commands file contains
def sh_commands_list():
	commands = open(commands_file, 'r')
	print ('\n\n\tCommands in file: \n')
	for x in commands:
		print ('\t\t' + x.strip('\n'))
	print ('\n\n')
	commands.close()
	press_return()
	main_menu()
	
 # Interfactive yes_no menu to continue with the configuration
def yes_no():
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
    print ('\n\n')
    print ('\n\n\tYou are about to modify the switches configuration.\n\n')
    print ('\n\n\t\tAre you sure you want to continue? y/n')
    while True:
        char = getch()
        if char.lower() == "y":
            print (char)
            clear_screen()
            connect()
            print ('\n\n Program finished. Press enter to return to main menu.')
        else:
            main_menu()
			
# Welcome page function
def main_menu():
	clear_screen()
	menu_actions = main_menu_actions
	menu_return = main_menu
	print ('\n\n')
	print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
	print ('\t*      Python Program for bulk network configuration        *')
	print ('\t*                                                           *')
	print ('\t*    Is is recomended to use this script to automate        *')
	print ('\t*    simple and repetitive configuration tasks.             *')
	print ('\t*                                                           *')
	print ('\t*    It is not recommended to use this program for          *')
	print ('\t*    complex tasks, like OSPF routing changes               *')
	print ('\t*                                                           *')
	print ('\t*                               Author: Valentin Jieanu     *')
	print ('\t* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
	print ('\n\n\tPlease choose an option from the following:\n\n')
	print ('\t\t1. Show IP addresses in list file\n')
	print ('\t\t2. Show the commands to be pushed to the devices\n')
	print ('\t\t3. Push the configuration to all devices\n')
	print ('\n\n\t\t0. Quit')
	choice = input('\n\n >> ')
	exec_menu(menu_actions, menu_return, choice)
	return  

# Ask user for username and password for the devices
def creds():
	global username, password, en_password
	username = input('Username: ')
	password = getpass.getpass('Password: ')
	en_password = getpass.getpass('Enable Password(may not be necesary):')

# Parse the commands list and store it globaly
def push_config():
	fo = open(commands_file, 'r') 
	for snd_cmd in fo:
		print ('\t*** Sending: ' + snd_cmd.strip())
		remote_conn.send(snd_cmd + '\n')
		time.sleep(.5)
	fo.close()
	
# Perform connection to the device and call SSH shell 
def connect():
    creds()
    global remote_conn
    global host
    if os.path.isfile(hosts_file):
        myfile = open(hosts_file, 'r')
        for ip in myfile:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            remote_conn = ()
            ip = ip.strip('\n')
            host = ip
            print_host = host
            print_host = print_host.replace('\n', '')
            try:
                print ('\n----- Connecting to %s -----\n' % print_host)
                client.connect(host,username=username,password=password,timeout=5)
                print ('\t*** SSH session established with %s ***' % print_host)
                remote_conn = client.invoke_shell()
                output = remote_conn.recv(2000).decode()
                time.sleep(1)
                if '#' not in output:
                    remote_conn.send('en\n')
                    time.sleep(1)
                    print ('\t*** Sending Enable Password ***')
                    remote_conn.send(en_password)
                    remote_conn.send('\n')
                    time.sleep(1)
                    output = remote_conn.recv(2000).decode()
                if '#' in output:
                    print ('\t*** Successfully Entered Enable Mode ***')
                    remote_conn.send('terminal length 0\n')
                    time.sleep(1)
                    enter_config_mode()
                    time.sleep(1)
                    push_config()
                    time.sleep(1)
                    remote_conn.send('end\n')
                    time.sleep(1)
                    remote_conn.send('copy run start\n')
                    time.sleep(1)
                    remote_conn.send('\n')
                    print ('\t\n*** Device Successfully configured ***')
                else:
                    print ('\t*** Incorrect Enable Password ***')
            except paramiko.SSHException:
                print ('\t*** Authentication Failed ***')
            except socket.error:
                print ('\t*** %s is Unreachable ***' % host)
            client.close()
			
# main program run parameters
def main():
	print ('Program starting... please wait\n')
	time.sleep(2)
	main_menu()

# main program run from main file
if __name__ == '__main__':
	args()
	main()
	
''''
author = "Valentin Jieanu"
copyright = "Copyright (C) 2016 Valentin Jieanu"
date created = 17/11/2016
date modified = 17/11/2016
license = "Public"
version = "1.0"
'''
