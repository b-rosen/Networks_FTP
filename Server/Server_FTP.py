from socket import *
import threading

# Class for multithreading: each object of this class has a run funtion which performs the receiving and sending of the message from the client
class TCP_UserThread (threading.Thread):
    msg = str()

    def __init__(self, threadName, threadID, conn_socket, address):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadName
        self.conn_socket = conn_socket
        self.address = address
    def run(self):
        print self.name + " is ready to use"
        while self.msg != 'exit':
            self.msg = self.conn_socket.recv(2048)
            print 'The message (from ' + str(address) + ') is: ' + self.msg
            self.conn_socket.send(self.msg)
        self.conn_socket.close()
        print ('\n' + self.name +  ' has been closed')

s_port = 2400

s_socket = socket(AF_INET, SOCK_STREAM)
s_socket.bind(('', s_port))
# Array to contain all created threads
threads = []
conn_ID = 0
# Every time a connection is requested, accept the connection and pass it off to a newly created thread.
while True:
    s_socket.listen(1)
    print 'Ready to receive \n\n'
    connection, address = s_socket.accept()
    threads.append(TCP_UserThread("Connection " + str(conn_ID), conn_ID, connection, address))
    threads[conn_ID].start()
    conn_ID += 1
