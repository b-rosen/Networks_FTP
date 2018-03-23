import threading
import socket

data = str()
active = False
connected = False
initiateConn = False
command = str()
bufferSize = 2048
data_socket = None
connection = None

address = str()
port = int()


def Close():
    DataConnection.connection.close()
    connected = False

def GetData(buffer=2048):
    msg = str()
    dataList = []
    DataConnection.active = True
    while msg != '':
        msg = DataConnection.connection.recv(buffer)
        dataList.append(msg)
    DataConnection.data = str()
    DataConnection.data = ''.join(dataList)
    DataConnection.active = False

def SendData():
    DataConnection.active = True
    DataConnection.connection.sendall(DataConnection.data)
    DataConnection.active = False

def Connect():
    if DataConnection.initiateConn:
        DataConnection.connection = socket(AF_INET, SOCK_STREAM)
        DataConnection.connection.connect((DataConnection.address, DataConnection.port))
    else:
        DataConnection.data_socket = socket(AF_INET, SOCK_STREAM)
        DataConnection.data_socket.bind(('', DataConnection.port))
        DataConnection.data_socket.listen(1)
        print 'Ready to receive Data'
        DataConnection.connection, address = data_socket.accept()
    DataConnection.connected = True
