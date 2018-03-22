import threading
import socket

class DataConnection(threading.Thread):
    data = str()
    active = False
    connected = False
    initiateDataConnection = False
    command = str()
    bufferSize = 2048
    data_socket = None
    connection = None

    def __init__(self, address, port):
        threading.Thread.__init__(self)
        self.address = address
        self.port = port
    def run(self):
        print "Data thread is ready to use"
        while command != 'Close':
            if command == 'GetData':
                GetData(bufferSize)
            elif command == 'SendData':
                SendData()
            elif command == 'Connect':
                Connect()
        command = str()
        self.connection.close()
        connected = False

    def GetData(buffer=2048):
        msg = str()
        dataList = []
        self.active = True
        while msg != '':
            msg = self.connection.recv(buffer)
            dataList.append(msg)
        self.data = str()
        self.data = ''.join(dataList)
        self.active = False

    def SendData():
        self.active = True
        self.connection.sendall(self.data)
        self.active = False
        pass

    def Connect():
        if self.initiateDataConnection:
            self.connection = socket(AF_INET, SOCK_STREAM)
            self.connection.connect((self.address, self.port))
        else:
            self.data_socket = socket(AF_INET, SOCK_STREAM)
            self.data_socket.bind(('', self.port))
            self.data_socket.listen(1)
            print 'Ready to receive Data'
            self.connection, address = data_socket.accept()
        self.connected = True
