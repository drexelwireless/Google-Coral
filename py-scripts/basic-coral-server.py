"""
Coral Server
------------

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


object_names = ["rat", "pencil", "soda can", "giraffe", "skateboard", "basketball", 
                "rum cake", "glass cup", "plate"]


def mock_detection(i):
    # fake detections
    frames = {}

    f = {}
    l = []
    print("server-process: detecting objects...")
    #l.append(str(datetime.datetime.now()))
    
    i = 1
    for j in range(randint(2,4)):
        score = random()
        #f[object_names[randint(0,len(object_names)-1)]] = [score, "fake_data"];
        f["Object Detected" + " " + str(i)] = score
        i += 1
    l.append(f)

    #frames["frame " + str(i)] = l
    frames["frame"] = l

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
            s.listen()

            # Wait for a client to connect
            conn, addr = s.accept()

            # Connect
            with conn:
                print("Connected by", addr, ".")
                data = conn.recv(1024)

                data_str = data.decode()
                data_str_args = data_str.split(" ")
                frequency = int(data_str_args[1])

                if data_str_args[0] == "start":
                    rand_iters = randint(5,10)
                    for i in range(rand_iters):
                        # TODO: change to run external python program
                        data = mock_detection(i)
                        data_json = json.dumps(data)
                        conn.sendall(data_json.encode())
                        conn.sendall(b"\n")
                        time.sleep(1/frequency)

                conn.sendall(b"\n")
                data = conn.recv(1024)
    
    # exit
    sys.exit()

