import threading
from socket import *
from time import sleep

data = str()
active = False
connected = False
initiateConn = False
bufferSize = 2048
data_socket = None
connection = None
fileData = None

address = str()
port = int()


def Close():
    global connection, active, connected
    while active:
        print 'Waiting for transfer'
        continue
    connection.close()
    print 'DC: Connection Closed'
    connected = False

def GetData(buffer=2048):
    global action, connection, data
    print 'DC: Getting Data'
    msg = ' '
    dataList = []
    active = True
    while msg != '':
        msg = connection.recv(buffer)
        dataList.append(msg)
    datastr = str()
    datastr = ''.join(dataList)
    data = datastr
    print 'DC: Data Received'
    active = False

def GetFile(buffer=2048):
    global action, connection, fileData
    print 'DC: Getting File'
    msg = ' '
    dataList = []
    active = True
    while msg != '':
        msg = connection.recv(buffer)
        dataList.append(msg)
    datastr = str()
    datastr = ''.join(dataList)
    data = datastr
    print 'DC: file Received'
    active = False

def sendFile(buffer=2048):
    global active, connection, fileData
    active = True
    print 'DC: Sending File'
    connection.sendall(fileData)
    print 'DC: File Sent'
    active = False

def SendData():
    global active, connection, data
    active = True
    print 'DC: Sending Data'
    connection.sendall(data)
    print 'DC: Data Sent'
    active = False

def Connect():
    global initiateConn, connection, address, port, data_socket, connected
    if connected:
        print 'Already Connected'
        return

    if initiateConn:
        sleep(0.1)
        connection = socket(AF_INET, SOCK_STREAM)
        connection.connect((address, port))
        print 'DC: Initiated Connection'
    else:
        data_socket = socket(AF_INET, SOCK_STREAM)
        data_socket.bind(('', port))
        data_socket.listen(1)
        print 'DC: Connected'
        connection, addr = data_socket.accept()
    connected = True
