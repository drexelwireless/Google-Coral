"""
Coral Client
------------

usages:     python coral-client.py <server_ip> <server_port>

Syntax:
    - Client connects to Server
    - Client sends "start" signal with frequency to get detections
    - Client reads data received byte-by-byte
    - If Client receives a '\n', Client watches next input closely
        - If Client receives a second '\n', Client ends connection and handles data collected accordingly
        - Else, Client treats previously collected data as data for one FRAME and handles according. 
            - Saves data as JSON (or sends to Thingsboard in Jetson's case)
            - Clears buffer and starts collecting data again
"""

# Import socket module
from socket import *
# Terminates the program and gets command line arguments
import sys
import os
import io
import datetime
# Parsing and creating JSONs
import json
from subprocess import run

detect_script = "/home/mendel/coral/examples-camera/opencv/detect-print-cont.py"


def print_frame(buf):
    for frame, data in buf.items():
        print("{frame} : {data[0]}")
        for obj, detection in data[1].items():
            print("\t{obj} : {detection}")
    return


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) != 3:
        print("ERROR -- usage: server.py <server_port>")
        sys.exit()

    server_host = ""
    server_port = -1

    # FIXME: check if server_host is valid
    server_host = sys.argv[1]

    # Check if port number is valid
    try:
        server_port = int(sys.argv[2])
    except:
        print("ERROR -- the given server_port is not a valid number")
        sys.exit()
    
    """
    print("Congrats! You passed all the command line argument checks c:")
    sys.exit()
    """

    start = datetime.datetime.now()

    # create pipe
    rFD, wFD = os.pipe()
    inheritable = True
    os.set_inheritable(wFD, inheritable)

    pid = os.fork()

    if pid == -1: # fork error
        print("ERROR -- could not create child process")
        sys.exit()
    elif pid == 0: # parent
        stop = datetime.datetime.now()
        print("Setup Time:", stop-start, "s")
        # FIXME: establish socket connection, 
        #           read info from child through pipe,
        #           send info over socket
        os.close(wFD)
        rFL = os.fdopen(rFD)
        while True:
            line = rFL.readline()[:-1]
            if len(line) > 0:
                print(line[0])
    else: # child
        os.close(rFD)
        # Run detection script once,
        # send info from it through pipe to parent
        # Change FDs to have output go to pipe
        newOUT = os.dup2(wFD, sys.stdout.fileno())

        # Using `execvp(FILE, ARGS)` where FILE is the name of the command to
        # run and ARGS is a tuple of the arguments the command needs
        args = ("python3", detect_script)
        os.execvp("python3", args)
        #os.write(wFD, b'Hello, world!')


    # exit
    sys.exit()

