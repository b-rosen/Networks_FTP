import threading
from socket import *
from time import sleep

''' All code in this file is Written by Benjamin Rosen (858324) '''
# This file contains functions pertaining to the data connection. These functions are intended to run in parallel, although only one data connection is allowed at one time. It is used by both the client and server.

data = str()
active = False
connected = False
initiateConn = False
bufferSize = 2048
data_socket = None
connection = None

# These variables are used in the connection phase and are changed by the client/server as necessary (for example, when sending/executing the PORT command)
address = str()
port = 20

# Closes the data connection. If the client/server initiated the connection, the listening socket is also closed.
def Close():
    global connection, active, connected, initiateConn
    while active:
        continue
    connection.close()
    if initiateConn == False:
        data_socket.close()
    print 'DC: Connection Closed'
    connected = False

# Keeps receiving data chunks until the connection has been closed by the other party, or an error has occurred. The data chunks are then joined together for use by the client/server code.
def GetData(buffer=2048):
    global active, connection, data
    print 'DC: Getting Data'
    msg = ' '
    dataList = []
    active = True
    counter = 10
    errorCounter = 10
    while counter > 0 and errorCounter > 0:
        try:
            msg = connection.recv(buffer)
        except Exception:
            if msg == '':
                counter -= 1
            else:
                errorCounter -= 1
            continue
        if msg == '':
            counter -= 1
        dataList.append(msg)
    datastr = str()
    datastr = ''.join(dataList)
    data = datastr
    print 'DC: Data Received'
    active = False

# Keeps sending data chunks until all the chunks have been sent, or an error has occurred.
def SendData():
    global active, connection, data
    active = True
    print 'DC: Sending Data'
    sendCounter = 20
    while sendCounter > 0:
        try:
            connection.sendall(data)
        except Exception:
            sendCounter -= 1
            continue
        break
    if sendCounter <= 0:
        print 'DC: Error in sending data'
    print 'DC: Data Sent'
    active = False

# Attempts to connect to the other party's port and address, using the ones specified by the client/server. If the server/client is set to initialise the connection, it will attempt to connect. Otherwise, it will listen on the port and address.
def Connect():
    global initiateConn, connection, address, port, data_socket, connected
    if connected:
        print 'DC: Already Connected'
        return

    connection = None
    data_socket = None

    if initiateConn:
        sleep(0.1)
        connection = socket(AF_INET, SOCK_STREAM)
        connectCounter = 20
        while connectCounter > 0:
            try:
                connection.connect((address, port))
            except Exception:
                connectCounter -= 1
                continue
            break

        print 'DC: Initiated Connection'
    else:
        data_socket = socket(AF_INET, SOCK_STREAM)
        data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        data_socket.bind(('', port))
        data_socket.listen(1)
        connection, addr = data_socket.accept()
        print 'DC: Connected'
    connected = True
