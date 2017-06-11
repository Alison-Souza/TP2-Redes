# From Python 2.6 you can import the print function from Python 3:
from __future__ import print_function
import socket
import select
import sys

import struct
import binascii
import ctypes

# sort list with attribute
import operator

# keep it as an exponent of 2
RECV_BUFFER = 4096

# messages type
class msg_type:
	OK = 1
	ERRO = 2
	OI = 3
	FLW = 4
	MSG = 5
	CREQ = 6
	CLIST = 7

# colorized output
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def print_header(msg):
	print(bcolors.HEADER + str(msg) + bcolors.ENDC)

def print_bold(msg):
	print(bcolors.BOLD + str(msg) + bcolors.ENDC)

def print_blue(msg):
	print(bcolors.OKBLUE + str(msg) + bcolors.ENDC)

def print_green(msg):
	print(bcolors.OKGREEN + str(msg) + bcolors.ENDC)

def print_warning(msg):
	print(bcolors.WARNING + str(msg) + bcolors.ENDC)

# For print errors in RED
def print_error(msg):
	print(bcolors.FAIL + str(msg) + bcolors.ENDC)
