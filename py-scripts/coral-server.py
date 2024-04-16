"""
Coral Server
------------

Python 3+ required to use `subprocess` module

usages:     python server.py <server_port>


Tips:
    - don't need headers
    - end messages with '\n'
    - make simple commands like start / stop
    - get examples from internet and cite sources

Goals:
    - [v] echo server / client
        - link in ~/projects/senior-design/notes.md
    - [v] figure out how to end connection on both ends
        - needed `while True` for  server to allow future connections and read incoming data byte-by-byte
          rather than all at once. Used '\n' as signal to stop reading data.
    - [v] send json through server
        - Formatted correctly. Can save as JSON or convert to Python dict and operate on.
    - [ ] Get server to run `detect-print.py` and format and forward its output through socket.
    - [ ] Allow Server to be able to receive "stop" signals to end programs being run like `detect-print.py`.

Data Format:

        {
         Frame 0 :   [
                      date, 
                            {
                             obj_0_name : [obj_0_data],
                             obj_1_name : [obj_1_data],
                             obj_2_name : [obj_2_data],
                                    ...
                             obj_n_name : [obj_n_data],
                            }
                    ],

            ...

         Frame i :   [
                      date, 
                            {
                             obj_0_name : [obj_0_data],
                             obj_1_name : [obj_1_data],
                             obj_2_name : [obj_2_data],
                                    ...
                             obj_n_name : [obj_n_data],
                            }
                    ],
        }

"""

# Import socket module
from socket import *
# Terminates the program and gets command line arguments
import sys
# Parsing and creating JSONs
import json
# For delay
import time
import datetime
from random import randint, random
# To run other programs (like C's `exec()`)
from subprocess import run, PIPE, Popen


detect_script = "/home/mendel/coral/examples-camera/opencv/detect-print.py"


object_names = ["rat", "pencil", "soda can", "giraffe", "skateboard", "basketball", 
                "rum cake", "glass cup", "plate"]


def mock_detection(i):
    # fake detections
    frames = {}

    f = {}
    l = []
    print("server-process: detecting objects...")
    l.append(str(datetime.datetime.now()))

    for j in range(randint(2,4)):
        score = random()
        f[object_names[randint(0,len(object_names)-1)]] = [score, "fake_data"];
    l.append(f)

    frames["frame " + str(i)] = l

    return str(frames)


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) != 2:
        print("ERROR -- usage: server.py <server_port>")
        sys.exit()

    server_host = ""
    server_port = -1

    # Check if port number is valid
    try:
        server_port = int(sys.argv[1])
    except:
        print("ERROR -- the given server_port is not a valid number")
        sys.exit()
    
    """
    print("Congrats! You passed all the command line argument checks c:")
    sys.exit()
    """

    with socket(AF_INET, SOCK_STREAM) as s:
        # Create door
        s.bind((server_host, server_port))

        while True:
            # wait for clients to connect (only one allowed to be queued)
            s.listen(1)

            # Accept request from queued connections
            conn, addr = s.accept()

            # Connect
            with conn:
                print("Connected by", addr, ".")
                time.sleep(1)
                
                # Run detection program and pipe STDOUT to this program
                result = run(args=["python3", detect_script], text=True, capture_output=True)
                result_lines = result.stdout.split("\n")[1:]
                frame = {}
                l = []
                for line in result_lines:
                    if line == "":
                        continue
                    s1 = line.split(":")
                    label = s1[0].strip()
                    s2 = s1[1].split(",")
                    f = {}
                    f[label] = s2[1].strip()
                    l.append(f)
                frame["frame"] = l
                print(frame)

                json_frame = json.dumps(str(frame))
                conn.sendall(json_frame.encode())

    
    # exit
    sys.exit()

