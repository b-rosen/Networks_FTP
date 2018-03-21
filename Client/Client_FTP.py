from socket import *
import atexit

responsesFile = open('../Command_Response_Database/response.txt', 'r')
replyCodes = {}
for line in responsesFile:
    msg, code = line.split(' ', 1)
    code = code.rstrip()
    replyCodes[msg] = str(code)
responsesFile.close()

# For Local Server

s_name = 'localhost'
s_port = 2400
username = 'Benjy'
password = 'Hello'
account = str()
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
    # if code == replyCodes['Syntax_Error']:
    #     print 'Syntax Error'
    #     return '-1'
    return str(code)

def Send(code):
    code = code + CRLF
    c_socket.send(code)

def StartUp(site, port):
    global c_socket
    c_socket = socket(AF_INET, SOCK_STREAM)
    try:
        c_socket.connect((site, port))
    except Exception, msg:
        print(msg)
        return False

    code = Receive()
    if code == replyCodes['Service_OK']:
        print 'Me: Service ok'
        return True
    return False

def Login():
    Send('USER ' + username)
    code = Receive()
    if code == replyCodes['Logged_In']:
        return True
    return codeCommands[code]()

def EnterPassword():
    Send('PASS ' + password)
    code = Receive()
    print 'Me: Sent password'
    if code == replyCodes['Logged_In']:
        print 'Me: Logged in'
        return True
    elif code == replyCodes['Command_Unnecessary']:
        print 'Superfluous code'
        return True
    else:
        return codeCommands[code]()

def EnterAccount():
    Send('ACCT ' + account)
    code = Receive()
    print 'Me: Sent account'
    if code == replyCodes['Logged_In']:
        print 'Me: Logged in'
        return True
    return codeCommands[code]()

def LoginFail():
    print 'Failed to login'
    return False

def ChangeDirectory(path):
    Send('CWD ' + path)
    code = Receive()
    if code == replyCodes['File_Action_Completed']:
        print 'Me: Directory changed'
    else:
        codeCommands[code]()

def ChangeUp():
    Send('CDUP')
    code = Receive()
    if code == replyCodes['File_Action_Completed']:
        print 'Me: Changed to parent directory'
    else:
        codeCommands[code]()

@atexit.register
def Logout():
    Send('QUIT')
    code = Receive()
    if code == replyCodes['Closed']:
        print 'Me: Successfully Logged Off'
        c_socket.close()
        print 'Me: The connection was closed'
    else:
        codeCommands[code]()

def NoOp():
    Send('NOOP')
    code = Receive()
    if code != replyCodes['Command_OK']:
        print 'Error: service is down'
    else:
        print 'Me: No-op successful'

def CloseConnection():
    c_socket.close()

def BadSyntax():
    print 'Error: Syntax is incorrect'

def BadArgument():
    print 'Error: Argument(s) are incorrect'

def NoCommand():
    print 'Error: Command not implemented'

def BadCommandOrder():
    print 'Error: Order of commands was incorrect'

def FileActionFailed():
    print 'Error: File action was not completed'

codeCommands = {
    '331': EnterPassword,
    '332': EnterAccount,
    '421': CloseConnection,
    '500': BadSyntax,
    '501': BadArgument,
    '502': NoCommand,
    '503': BadCommandOrder,
    '530': LoginFail,
    '550': FileActionFailed
}
# replyCodes = {
#     'Service_OK': 220,
#     'Closed': 221,
#     'Need_Password': 331,
#     'Logged_In': 230
# }

# msg = str()
# cmd = str()
# StartUp(s_name, s_port)
# Login()
# NoOp()
# # while cmd.upper() != 'QUIT':
# #     cmd = raw_input("Me: Input command: ")
# #     Send(cmd)
# #     msg = Receive()
#     # if msg != replyCodes['Service_OK']:
#     #     print 'Wrong reply'
# Logout()
