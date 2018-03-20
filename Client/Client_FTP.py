from socket import *
import response

# For Local Server
s_name = 'localhost'
s_port = 2400
username = 'Benjy'
password = 'Hello'

# For Wits Server
# s_name = 'ELEN4017.ug.eie.wits.ac.za'
# s_port = 21
# username = 'group8'
# password = 'phuo4eeK'

CRLF = '\r\n'

c_socket = socket(AF_INET, SOCK_STREAM)
c_socket.connect((s_name, s_port))
def ParseReply(msg):
    code = msg.split('\r\n', 1)
    if(msg != ''):
        code = int(code[0].split(" ", 1)[0])
    return code

def Receive(bufferSize=2048):
    message = c_socket.recv(bufferSize)
    # print message
    code = ParseReply(message)
    # if code == "QUIT":
    #     commandList[cmd](args)
    #     return
    return str(code)

def Respond(code):
    code = code + CRLF
    c_socket.send(code)

def Login():
    code = Receive()
    if code == response.replyCodes['Service_OK']:
        print 'Me: Service ok'
        Respond('USER ' + username)
        code = Receive()
        if code == response.replyCodes['Need_Password']:
            Respond('PASS ' + password)
            code = Receive()
            print 'Me: Sent password'
            if code == response.replyCodes['Logged_In']:
                print 'Me: Logged in'
                return
def Logout():
    Respond('QUIT')
    code = Receive()
    if code == response.replyCodes['Closed']:
        print 'Me: Successfully Logged Off'
        c_socket.close()
        print 'Me: The connection was closed'

# replyCodes = {
#     'Service_OK': 220,
#     'Closed': 221,
#     'Need_Password': 331,
#     'Logged_In': 230
# }

msg = str()
cmd = str()
Login()
while cmd.upper() != 'QUIT':
    cmd = raw_input("Me: Input command: ")
    Respond(cmd)
    msg = Receive()
Logout()
