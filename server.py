#S15
#PAULE, MIKAEL ANGELO GONZALES
#REYES, MA. JULIANNA RE-AN DE GUZMAN
#SANTOS, EMMANUEL GABRIEL DEL VALLE
import socket
import json
from datetime import datetime
import time


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_addr = ('127.0.0.1', 12345)
server.bind(server_addr)

print("Server has started at {}:{}".format(*server_addr))

clients = {}
files_list = []
timestamps_list = []
uploaders_list = []

while True:
    data, addr = server.recvfrom(1024)

    try:
        response = json.loads(data.decode())
    except json.JSONDecodeError as e:
        msg = {'command': 'error', 'message': str(e)}
        server.sendto(json.dumps(msg).encode('utf-8'),addr)

        continue
    
    #The response of the server when the client inputs the various commands
    if response['command'] == '/join':
        #Connect to the Server Application
        print(f"Client {addr} has connected to server")
        msg = {'command': 'join', 'message':"Connection to the File Exchange Server is succesful!"}
        server.sendto(json.dumps(msg).encode('utf-8'),addr)

    elif response['command'] == '/leave':
        #Disconnect to the Server Application
        if len(response['params']) != 0:
            msg = {'command': 'error', 'message':
            'Error: Command parameters do not match or are not allowed.\n'}
            server.sendto(json.dumps(msg).encode('utf-8'),addr)
        else:
            #Removing the user from the clients connected to the server
            for name, value in clients.items():
                if value == addr:
                    print(f"Client {name} has disconnected from the server")
                    clients.pop(name)
                    break
            
            print(f"{addr} has disconnected")
            msg = {'command': 'leave', 'message':
                   f"Connected closed, Thank you!"}
            server.sendto(json.dumps(msg).encode('utf-8'),addr)

    elif response['command'] == '/register':
        #Register a unique handle or alias
        if len(response['params']) != 1:
            msg = {'command': 'error', 'message':
            'Error: Command parameters do not match or are not allowed.\n'}
            server.sendto(json.dumps(msg).encode('utf-8'),addr)
        else:
            handle_alias = response['params'][0]
            flag = True
            for name,value in clients.items():
                if value == addr:
                    msg = {'command': 'error', 'message': 'Error: Registration failed. user is already registered.\n'}
                    server.sendto(json.dumps(msg).encode('utf-8'),addr)
                    flag = False
                    break
                elif name == handle_alias:
                    msg = {'command': 'error','message': 'Error: Registration failed. you are already registered.\n'}
                    server.sendto(json.dumps(msg).encode('utf-8'),addr)
                    flag = False
                    break

            if flag:
                clients[handle_alias] = addr
                print(f"Client {addr} registered as {handle_alias}")
                msg = {'command': 'register','client': handle_alias}
                server.sendto(json.dumps(msg).encode('utf-8'),addr)
        
        print(clients)

    elif response['command'] == '/store':
        #Send file to server
        filename = response['params'][0]
        filename_str = str(filename)
        filename_data = response.get('data')

        for key, value in clients.items():
            if value == addr:
                uploader = key
                break

        try:
            with open(filename,'wb') as file:
                file.write(filename_data.encode('utf-8'))
            timeRecord = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            files_list.append(filename)
            timestamps_list.append(timeRecord)
            uploaders_list.append(uploader)

            msg = f"{uploader} <{timeRecord}>: Uploaded {filename_str}"

            print(msg)
        except Exception as e:
            rsp = json.dumps({'command': 'error', 'message': f"{str(e)}"})
            print("Store server Exception tracker")

    elif response['command'] == 'dir':
        #Request directory list from server
        try:
            if len(files_list) == 0:
                print("Error: No files found in the server")
                jsonData = {'command': 'error','message':"Error: No files found in the server"}
            else:
                jsonData = {'command': 'dir', 'files_list': files_list, 'timestamps_list':timestamps_list,'uploaders_list': uploaders_list}

            server.sendto(json.dumps(jsonData).encode(),addr)
        except Exception as e:
            print("Error sending response to the client: " + str(e))

    elif response['command'] == 'get':
        #Fetch a file from the sevrer
        filename = response['params'][0]
        try:
            if filename not in files_list:
                raise FileNotFoundError
            
            with open(filename,'rb') as file:
                file_data = file.read()
                rsp = {'command': 'get', 'filename': filename,'data': file_data.decode('ISO-8859-1'),'message': "File sent Succesfully."}

            print("File sent to the client successfully.")

        except FileNotFoundError:
            rsp = {'command': 'error','message':f"Error: File {filename} not found."}
            print("File Not Found.")
        
        except Exception as e:
            rsp = {'command': 'error', 'message': f"Error: {str(e)}"}
            print(f"Error: {str(e)}")
        
        server.sendto(json.dumps(rsp).encode(),addr)
    else:
        msg = {'command': 'error', 'message': "Error: Command not found.\n"}
        server.sendto(json.dumps(msg).endcode('utf-8'),addr)
            


