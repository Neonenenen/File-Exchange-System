#S15
#PAULE, MIKAEL ANGELO GONZALES
#REYES, MA. JULIANNA RE-AN DE GUZMAN
#SANTOS, EMMANUEL GABRIEL DEL VALLE
import socket
import json
import threading

client = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

server_addr = None
connection = False
registered = False
alias = ""

def help_commands():
    #this functions shows the various commands the user can do

    print("1.Connect to the server application      /join <server_ip_add> <port>\n")

    print("2.Disconnect to the server application       /leave\n")

    print("3.Register a unique handle or alias      /register <handle>\n")
    
    print("4.Send file to server        /store <filename>\n")

    print("5.Request directory file list from a server      /dir\n")

    print("6.Fetch a file from a server     /get <filename>\n")

    print("7.Output all input commands for references       /?\n")

def receive_file():
    #This functions allows the user to get information and files from the server

    global server_addr

    while True:
        if server_addr is not None:
            try:
                data, addr = client.recvfrom(1024)

                if not data:
                    break

                rsp = json.loads(data.decode())

                if rsp['command'] == 'join' or rsp['command'] == 'error':
                    print(f"{rsp['message']}\n")

                elif rsp['command'] == 'leave':
                    print(f"{rsp['message']}\n")
                    server_addr = None

                elif rsp['command'] == 'register':
                    print(f"Welcome {rsp['client']}!\n")

                elif rsp['command'] == 'dir':
                    if 'files_list' in rsp:
                        print("Server Files:")
                        for filename, timestamps_list, uploaders_list in zip(rsp['files_list'], rsp['timestamps_list'], rsp['uploaders_list']):
                            print(f"{filename} uploaded by {uploaders_list} at {timestamps_list}")
                    else:
                        print("Error: No files have been found int the server.\n")

                elif rsp['command'] == 'get':
                    filename = rsp['filename']
                    file_data = rsp['data']
                    try:
                        with open(filename, 'wb') as file:
                            file.write(file_data.encode('ISO-8859-1'))
                        print(f"File {filename} received from server.")
                    except Exception as e:
                        print(f"Error saving file: {str(e)}\n")

                elif rsp['command'] == 'store':
                    if rsp['status'] == 'success':
                        print(f"File {rsp['filename']} successfully stored on the server.")
                    else:
                        print(f"Error storing file on the server: {rsp['message']}")
                
            except json.JSONDecodeError:
                print('Error decoding JSON data from the server. Please try again\n')

def print_error_command():
    #prints the error command if the user typed something wrong
    print("Error: Command paramters do not match or is not allowed.\n")

def start():
    #the functions lets the client interact and connect to the server, also allows the user to do the different commands placed in by the specificaitons

    global connection
    global registered

    while True:
        users_input = input()
        users_parts = users_input.split()
        command = users_parts[0]
        params = users_parts[1:]

        msg = {'command': command, 'params': params}

        if command == '/?':
            if len(params) == 0:
                help_commands()

            else:
                print_error_command()
        
        elif not connection and command == '/join':
            if len(params) !=2:
                print_error_command()
            
            elif len(params) == 2 and params [0] == '127.0.0.1' and params[1] == '12345':
                #allows the user to connect to the server
                temp = (params[0], int(params[1]))
                client.sendto(json.dumps(msg).encode('utf-8'),temp)

                global server_addr
                server_addr = temp
                connection = True

            else:
                print("Error: Connection to the Server has failed! please check IP Address and port Number.\n")

        elif connection and command == '/join':
            print_error_command()

        elif command == '/leave':
            if connection:
                client.sendto(json.dumps(msg).encode('utf-8'),server_addr)
                connection = False
                registered = False

            else:
                print("Error: Disconnection failed. please connect to the server first.\n")

        elif command == '/register':
            if connection:
                client.sendto(json.dumps(msg).encode('utf-8'),server_addr)
                registered = True

            else:
                print("Error: No connection found to the server, please connect to the server.\n")

        elif command == '/store':
            if registered and len(params) == 1:  
                filename = params[0]
                try:
                    with open(filename, 'rb') as file:
                        fileData = file.read()
                        msg = {'command': command, 'params':[filename], 'data': fileData.decode('ISO-8859-1')}

                        client.sendto(json.dumps(msg).encode(), server_addr)
                        print(f"{filename} has been succesfully sent to the server.\n")

                except FileNotFoundError:
                    print("Error: File not found.\n")
                
                except Exception as e:
                    print(f"Error: {str(e)}\n")
            
            elif registered and len(params) !=1:
                print_error_command()
            elif connection and not registered:
                print("Error: Client not registered to the server, please register a handle first.\n")
            elif not connection:
                print("Error: Client not connected to the server, please connect to the server first.\n")
        
        elif command == '/dir':
            if registered and len(params) == 0:
                try:
                    client.sendto(json.dumps({"command": "dir"}).encode(), server_addr)
                except Exception as e:
                    print("There has been an Error in sending data: ", e)
                
            elif registered and len(params) != 0:
                print_error_command()
            
            elif connection and registered:
                print("Error: Client not registered to the server, please register a handle first.\n")

            elif not connection:
                print("Error: No connection found to the server, please connect to the server.\n")
            
        elif command == '/get':
            if registered and len(params) == 1:
                filename = params[0]
                try:
                    msg = {'command': 'get', 'params':[filename]}

                    client.sendto(json.dumps(msg).encode(), server_addr)
                except Exception as e:
                    print("There has been an Error in sending data: ", e)
            
            elif registered and len(params) != 1:
                print_error_command()
            
            elif connection and registered:
                print("Error: Client not registered to the server, please register a handle first.\n")

            elif not connection:
                print("Error: No connection found to the server, please connect to the server.\n")

        else:
            print('Error:Command not found.\n')

receiveThread = threading.Thread(target=receive_file)
receiveThread.start()

help_commands()
start()
                 
