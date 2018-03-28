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
    errorCounter = 10
    while counter > 0 and errorCounter > 0:
        try:
            msg = connection.recv(buffer)
        except:
            errorCounter -= 1
            continue
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
