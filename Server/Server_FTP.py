from socket import *
import UserThread

# Class for multithreading: each object of this class has a run funtion which performs the receiving and sending of the message from the client

s_port = 2400

s_socket = socket(AF_INET, SOCK_STREAM)
s_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s_socket.bind(('', s_port))
# Array to contain all created threads
threads = []
conn_ID = 0
# Every time a connection is requested, accept the connection and pass it off to a newly created thread.
while True:
    s_socket.listen(1)
    print 'Ready to receive \n\n'
    connection, address = s_socket.accept()
    threads.append(UserThread.UserThread("Connection " + str(conn_ID), conn_ID, connection, address))
    threads[conn_ID].start()
    conn_ID += 1
