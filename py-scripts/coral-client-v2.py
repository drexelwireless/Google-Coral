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
import signal
import io
import datetime
import re
import errno
# Parsing and creating JSONs
import json
from subprocess import run

detect_script = "/home/mendel/coral/examples-camera/opencv/detect-print-cont.py"


def signal_handler(sig, frame):
    os.close(wFD)
    sys.exit()


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) != 3:
        print("ERROR -- usage: server.py <server_port>")
        sys.exit()

    server_host = ""
    server_port = -1

    # Check if server_host is valid
    server_host = sys.argv[1]
    pattern = re.compile("[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+")
    if not pattern.fullmatch(server_host):
        print("ERROR -- the given server_host is not a valid IPv4 address")
        sys.exit()
    sh_sections = re.split("\.", server_host)
    for section in sh_sections:
        if int(section) > 255 or int(section) < 0:
            print("ERROR -- the given server_host is not a valid IPv4 address")
            sys.exit()

    # Check if port number is valid
    try:
        server_port = int(sys.argv[2])
    except:
        print("ERROR -- the given server_port is not a valid number")
        sys.exit()
    if server_port < 0 or server_port > 65535:
        print("ERROR -- the given server_port is not a valid number")
        sys.exit()
    
    """
    print("Congrats! You passed all the command line argument checks c:")
    sys.exit()
    """

    # (start) time setup
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
        # Establish socket connection, 
        # Read info from child through pipe,
        # Send info over socket
        os.close(wFD)
        rFL = os.fdopen(rFD)

        with socket(AF_INET, SOCK_STREAM) as s:
            # Create connection
            try:
                s.connect((server_host, server_port))
            except OSError as error:
                if error.errno == errno.ENETUNREACH:
                    print(f'ERROR {error.errno}: {os.strerror(error.errno)}')
                os.close(rFD)
                os.kill(pid, signal.SIGTERM)
                sys.exit()

            # (stop) time setup
            stop = datetime.datetime.now()
            print("Setup Time:", stop-start, "s")
            
            # (start) time sending
            start = datetime.datetime.now()

            # run program
            while True:
                # Reads a line from the pipe, then converts it into a JSON file 
                # to be sent over socket
                # Skips any lines that only server as flags for the end of 
                # frames or is empty
                # Break loop if EOF reached
                line = rFL.readline()[:-1]
                if line == "":
                    break
                elif len(line) == 0 or line.isspace():
                    continue
                elif "DETECTION END" in line:
                    break

                frame = {}
                f = {}
                l = []
                i = 1
                while "END FRAME" not in line:
                    if "Frame" in line or len(line.strip()) == 0:
                        line = rFL.readline()[:-1]
                        continue
                    line_arr = line.split(":")
                    if len(line_arr) < 2:
                        #print(line_arr)
                        line = rFL.readline()[:-1]
                        continue
                    label = line_arr[0].strip()
                    f["Object Detected " + str(i)] = label
                    metadata = line_arr[1].strip().split(", ")
                    score = metadata[1].strip()
                    f["Score " + str(i)] = score
                    i += 1
                    line = rFL.readline()[:-1]
                l.append(f)
                frame["frame"] = l
                print(frame)

                json_frame = json.dumps(frame)
                s.sendall(json_frame.encode())

            # (stop) time sending
            stop = datetime.datetime.now()
            print("Sending Time of 100 Frames:", stop-start, "s")
            print("Frame Detections sent per seconds =", (stop-start)/100)
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


    # exit
    sys.exit()

