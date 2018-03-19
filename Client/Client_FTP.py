from socket import *

s_name = 'localhost'
s_port = 2400

c_socket = socket(AF_INET, SOCK_STREAM)
c_socket.connect((s_name, s_port))

echoMsg = str()
msg = str()
''' The while loop:
        - Gets an input from the user
        - Sends that message to the server through the client's c_socket
        - Receives up to 2048 bytes of the echoed message from the server
        - Prints that message
    Until the message 'exit' is input, in which case the program will close the connection after sending the command to the server'''
while msg != 'exit':
    msg = raw_input('Enter message to send (exit to terminate): ')
    c_socket.send(msg)
    # echoMsg = c_socket.recv(2048)
    # print 'The server responded with: ' + echoMsg + '\n'

c_socket.close()
print 'The connection was closed'
