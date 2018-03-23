from socket import *

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
connected = False
import atexit
# ------------------------------------------

# For Wits Server

s_name = 'ELEN4017.ug.eie.wits.ac.za'
s_port = 21
username = 'group8'
password = 'phuo4eeK'
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
    print message
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
    global c_socket, connected
    c_socket = socket(AF_INET, SOCK_STREAM)
    try:
        c_socket.connect((site, port))
    except Exception, msg:
        print(msg)
        return (False, "Could not find server")

    code = Receive()
    if code == replyCodes['Service_OK']:
        msg = 'Service ok'
        print msg
        connected = True
        return (True,msg)
    return codeCommands[code]()

def Login():
    Send('USER ' + username)
    code = Receive()
    if code == replyCodes['Logged_In']:
        return (True, "Logged in")
    return codeCommands[code]()

def EnterPassword():
    Send('PASS ' + password)
    code = Receive()
    print 'Sent password'
    if code == replyCodes['Logged_In']:
        msg = 'Logged in'
        print msg
        return (True, msg)
    elif code == replyCodes['Command_Unnecessary']:
        msg = 'Superfluous code'
        print msg
        return (True, msg)
    else:
        return codeCommands[code]()

def EnterAccount():
    Send('ACCT ' + account)
    code = Receive()
    print 'Sent account'
    if code == replyCodes['Logged_In']:
        msg = 'Logged in'
        print msg
        return (True, msg)
    return codeCommands[code]()

def LoginFail():
    msg = 'Failed to login'
    print msg
    return (False, msg)

def ChangeDirectory(path):
    Send('CWD ' + path)
    code = Receive()
    if code == replyCodes['File_Action_Completed']:
        msg = 'Directory changed'
        print msg
        return (True,msg)
    else:
        return codeCommands[code]()

def ChangeUp():
    Send('CDUP')
    code = Receive()
    if code == replyCodes['File_Action_Completed']:
        msg =  'Changed to parent directory'
        print msg
        return (True,msg)
    else:
        return codeCommands[code]()

def ListFilesRec():
    #code = Receive()
    code = '226'
    listInfo = "test 4 test test 0 month year time Directory\ntest 1 test test 1234 month year time file"
    if (code == replyCodes['Data_Connection_Open']) or (code == replyCodes['File_Status_Ok']):
        return ListFilesRec()
    
    result,message = codeCommands[code]()
    if result:
        entryType = []
        entryName = []
        lines = listInfo.split("\r\n")
        for line in lines:
            values = line.split()
            entryName.append(String(values[len(values)-1]))
            if int(values[1]) > 1:
                entryType.append("Directory")
            else:
                entryType.append("File")
        return (True,entryName,entryType)
    else:
        return (False,message,"")
    
def ListFiles(directoryPath):
    if directoryPath == '':
        Send('LIST')
    else:
        commandString = 'LIST ' + directoryPath
        Send(commandString)
    return ListFilesRec()

@atexit.register
def Logout():
    global connected
    if connected:
        Send('QUIT')
        code = Receive()
        if code == replyCodes['Closed']:
            print 'Successfully Logged Off'
            c_socket.close()
            msg = 'The connection was closed'
            connected = False
            print msg
            return (True, msg)
        else:
            codeCommands[code]()
    else:
        msg = "Not connected"
        print msg
        return (False, msg)

def NoOp():
    Send('NOOP')
    code = Receive()
    if code != replyCodes['Command_OK']:
        msg = 'service is down'
        print msg
        return (False, msg)
    else:
        msg = 'No-op successful'
        print msg
        return (True, msg)

def CloseConnection():
    c_socket.close()

def BadSyntax():
    msg = 'Syntax is incorrect'
    print msg
    return (False,msg)

def BadArgument():
    msg = 'Argument(s) are incorrect'
    print msg
    return (False,msg)

def BadCommandOrder():
    msg = 'Order of commands was incorrect'
    print msg
    return (False,msg)

def FileActionFailed():
    msg = 'File action was not completed'
    print msg
    return (False,msg)

def NoCommand():
    msg = 'Command not implemented'
    print msg
    return (False,msg)

def DCOpen():
    msg = "Transfer starting, please wait"
    print msg
    return (False,msg)

def DCAboutToOpen():
    msg = "About to open data connection, please wait"
    print msg
    return (False,msg)

def ClosingDC():
    msg = "Closing Data Connection"
    print msg
    return (True,msg)

def FileActionOkay():
    msg = "Action complete"
    print msg
    return (True,msg)

def CantOpenDC():
    msg = "Cannot open data connection"
    print msg
    return (False,msg)

def ConnectionClosedAbort():
    msg = "Connection closed, transfer aborted"
    print msg
    return (False,msg)

def FileUnavailable():
    msg = "The file is currently unavailable"
    print msg
    return (False,msg)

def ActionAbortedLocal():
    msg = "There was a local error while processing, action aborted"
    print msg
    return (False,msg)



codeCommands = {
    '125': DCOpen,
    '150': DCAboutToOpen,
    '226': ClosingDC,
    '250': FileActionOkay,
    '331': EnterPassword,
    '332': EnterAccount,
    '421': CloseConnection,
    '425': CantOpenDC,
    '426': ConnectionClosedAbort,
    '450': FileUnavailable,
    '451': ActionAbortedLocal,
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
# ListFiles('/')
# # while cmd.upper() != 'QUIT':
# #     cmd = raw_input("Me: Input command: ")
# #     Send(cmd)
# #     msg = Receive()
#     # if msg != replyCodes['Service_OK']:
#     #     print 'Wrong reply'
# Logout()
