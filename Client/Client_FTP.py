from socket import *

responsesFile = open('../Command_Response_Database/response.txt', 'r')
replyCodes = {}
for line in responsesFile:
    msg, code = line.split(' ', 1)
    code = code.rstrip()
    replyCodes[msg] = str(code)
responsesFile.close()

account = str()

# For Local Server

s_name = 'localhost'
s_port = 2400
username = 'Benjy'
password = 'Hello'
# ------------------------------------------

# For Wits Server

# s_name = 'ELEN4017.ug.eie.wits.ac.za'
# s_port = 21
# username = 'group8'
# password = 'phuo4eeK'
# ------------------------------------------

# For Mirror (given in brief)

# s_name = 'mirror.ac.za'
# s_port = 21
# username = 'anonymous'
# password = ''
# ------------------------------------------

CRLF = '\r\n'

def ParseReply(msg):
    code = msg.split('\r\n', 1)
    if(msg != ''):
        code = code[0].split('-')
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

def StartUp(site, port):
    global c_socket
    c_socket = socket(AF_INET, SOCK_STREAM)
    c_socket.connect((site, port))
    code = Receive()
    if code == replyCodes['Service_OK']:
        print 'Me: Service ok'
        Login()

def Login():
    Respond('USER ' + username)
    code = Receive()
    if code == replyCodes['Logged_In']:
        return
    codeCommands[code]()

def EnterPassword():
    Respond('PASS ' + password)
    code = Receive()
    print 'Me: Sent password'
    if code == replyCodes['Logged_In']:
        print 'Me: Logged in'
    elif code == replyCodes['Command_Unnecessary']:
        print 'Superfluous code'
    else:
        codeCommands[code]()

def EnterAccount():
    Respond('ACCT ' + account)
    code = Receive()
    print 'Me: Sent password'
    if code == replyCodes['Logged_In']:
        print 'Me: Logged in'
        return
    codeCommands[code]()

def LoginFail():
    print 'Failed to login'

def Logout():
    Respond('QUIT')
    code = Receive()
    if code == replyCodes['Closed']:
        print 'Me: Successfully Logged Off'
        c_socket.close()
        print 'Me: The connection was closed'
    else:
        codeCommands[code]()

def NoOp():
    Respond('NOOP')
    code = Receive()
    print 'Me: No-op successful'
    if code != replyCodes['Command_OK']:
        print 'Error: service is down'

def CloseConnection():
    c_socket.close()

def BadSyntax():
    print 'Syntax is incorrect'

def BadArgument():
    print 'Argument(s) are incorrect'

def BadCommandOrder():
    print 'Order of commands was incorrect'

codeCommands = {
    '331': EnterPassword,
    '332': EnterAccount,
    '421': CloseConnection,
    '500': BadSyntax,
    '501': BadArgument,
    '503': BadCommandOrder,
    '530': LoginFail
}
# replyCodes = {
#     'Service_OK': 220,
#     'Closed': 221,
#     'Need_Password': 331,
#     'Logged_In': 230
# }

msg = str()
cmd = str()
StartUp(s_name, s_port)
NoOp()
# while cmd.upper() != 'QUIT':
#     cmd = raw_input("Me: Input command: ")
#     Respond(cmd)
#     msg = Receive()
    # if msg != replyCodes['Service_OK']:
    #     print 'Wrong reply'
Logout()
