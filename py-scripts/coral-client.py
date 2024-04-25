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
import datetime
# Parsing and creating JSONs
import json
from subprocess import run

detect_script = "/home/mendel/coral/examples-camera/opencv/detect-print.py"


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

    n_max = 100
    n = 0

    
    with socket(AF_INET, SOCK_STREAM) as s:
        # Create connection
        s.connect((server_host, server_port))

        stop = datetime.datetime.now()
        print("Setup Time:", stop-start,"s")

        start = datetime.datetime.now()

        # run program
        while True:
            if n > n_max:
                break
            result = run(args=["python3", detect_script], text=True, 
                        capture_output=True)
            result_lines = result.stdout.split("\n")[1:]
            print(result.stderr)
            frame = {}
            f = {}
            l = []
            i = 1
            for line in result_lines:
                print(line)
                if line == "":
                    continue
                s1 = line.split(":")
                label = s1[0].strip()
                s2 = s1[1].split(",")
                score = s2[1].strip()
                f["Object Detected " + str(i)] = label
                f["Score " +str(i)] = score
                i += 1
            l.append(f)
            frame["frame"] = l
            print(frame)

            json_frame = json.dumps(frame)
            s.sendall(json_frame.encode())
            
            n += 1

        stop = datetime.datetime.now()
        print("Send Time of 100 Frames:", stop-start, "s")
        print("Frame Detections sent per second:", (stop-start)/100)



    # exit
    sys.exit()

