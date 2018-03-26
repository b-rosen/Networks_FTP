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
sendCounter = 10

address = str()
port = 20


def Close():
    global connection, active, connected, initiateConn
    while active:
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
    counter = 10
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
    global active, connection, data, sendCounter
    active = True
    print 'DC: Sending Data'
    try:
        connection.sendall(data)
    except EBADF:
        sendCounter -= 1
        if sendCounter > 0:
            SendData()
        else:
            print 'DC: Failed to send data'
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
        data_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        data_socket.bind(('', port))
        data_socket.listen(1)
        print 'DC: Connected'
        connection, addr = data_socket.accept()
    connected = True
