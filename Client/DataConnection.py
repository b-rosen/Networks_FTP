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
    global connection, active, connected, initiateConn
    while active:
        print 'Waiting for transfer'
        continue
    connection.close()
    if initiateConn == False:
        data_socket.close()
    print 'DC: Connection Closed'
    connected = False

def GetData(buffer=2048):
    global active, connection, data
    print 'DC: Getting Data'
    msg = ' '
    dataList = []
    active = True
    counter = 5
    while counter > 0:
        msg = connection.recv(buffer)
        dataList.append(msg)
        if msg == '':
            counter -= 1
    datastr = str()
    datastr = ''.join(dataList)
    data = datastr
    print 'DC: Data Received'
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
