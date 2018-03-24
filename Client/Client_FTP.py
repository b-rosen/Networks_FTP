from socket import *
import threading
import DataConnection

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
currentDirectory = str()
import atexit
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
    reply = msg.split('\r\n', 1)
    if(msg != ''):
        reply = reply[0].split('-')
        reply = reply[0].split(" ", 1)
        code = int(reply[0])
        try:
            message = reply[1]
        except IndexError:
            message = str()
    return (code, message)

def Receive(bufferSize=2048, getMessage=False):
    message = c_socket.recv(bufferSize)
    code, msg = ParseReply(message)
    # if code == "QUIT":
    #     commandList[cmd](args)
    #     return
    # if code == replyCodes['Syntax_Error']:
    #     print 'Syntax Error'
    #     return '-1'
    if getMessage:
        return str(code), msg
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
    msg = 'Not logged in'
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

def getList(listData):
    #listData = "test 1 test test bits month date time fileName1\r\ntest 1 test test bits month date time fileName2\r\ntest 1 test test bits month date time fileName3\r\ntest 4 test test bits month date time directoryName1"
    entryType = []
    entryName = []
    lines = listData.split('\r\n')

    for line in lines:
        values = line.split()
        entryName.append(values[len(values)-1])
        if int(values[1]) > 1:
            entryType.append("Directory")
        else:
            entryType.append("File")
    return (entryName,entryType)

def ListFiles(directoryPath):
    if directoryPath == '':
        Send('LIST')
    else:
        commandString = 'LIST ' + directoryPath
        Send(commandString)
    code = Receive()
    if code == replyCodes['Data_Connection_Open']:
        print 'Data Connection Already open'
    elif code == replyCodes['File_Status_Ok']:
        DataConnection.Connect()
        print 'Opening data connection'
    else:
        return codeCommands[code]()
    data_thread = threading.Thread(None, DataConnection.GetData)
    data_thread.start()
    
    while True:
        code = Receive()
        if code == replyCodes['Closing_Data_Connection']:
            DataConnection.Close()
            msg = 'Transfer complete - Closing data connection'
            print msg
            entryNames,entryTypes = getList(DataConnection.data)
            return (True, msg, entryNames,entryTypes)
        elif code == replyCodes['File_Action_Completed']:
            msg = 'Transfer complete'
            print msg
            entryNames,entryTypes = getList(DataConnection.data)
            return (True, msg,entryNames,entryTypes)
        elif code == replyCodes['Cant_Open_Data_Connection'] or code == replyCodes['Connection_Closed'] or code == replyCodes['Action_Aborted_Local']:
            DataConnection.Close()
            return codeCommands[code]()

def ChangePort(newPort):
    DataConnection.port = int(newPort)
    cmdAddress = gethostbyname(gethostname()).replace('.', ',')
    cmdPort = ','.join((str(int(DataConnection.port) / 256), str(DataConnection.port % 256)))
    cmd = ','.join((cmdAddress, cmdPort))
    DataConnection.initiateConn = False
    Send('PORT ' + cmd)
    code = Receive()
    if code == replyCodes['Command_OK']:
        msg = 'Successfully changed port'
        print msg
        return (True, msg)
    else:
        return codeCommands[code]()

def PassiveMode():
    Send('PASV')
    code, message = Receive(getMessage=True)
    if code == replyCodes['Passive_Mode']:
        hostPort = message.split(',')
        DataConnection.address = '.'.join(hostPort[0:4])
        DataConnection.port = int(hostPort[4]) * 256 + int(hostPort[5])
        DataConnection.initiateConn = True
        msg = 'Entered Passive Mode'
        print msg
        return (True, msg)
    else:
        return codeCommands[code]()

def download(filePath):
    Send('RETR '+ filePath)
    code = Receive()
    if code == replyCodes['Data_Connection_Open']:
        print 'Data Connection Already open'
    elif code == replyCodes['File_Status_Ok']:
        DataConnection.Connect()
        print 'Opening data connection'
    else:
        return codeCommands[code]()
    data_thread = threading.Thread(None, DataConnection.GetFile)
    data_thread.start()
    
    while True:
        code = Receive()
        if code == replyCodes['Closing_Data_Connection']:
            DataConnection.Close()
            msg = 'Transfer complete - Closing data connection'
            print msg
            rFile = DataConnection.fileData
            print rFile
            #Save file
            return (True, msg)
        elif code == replyCodes['File_Action_Completed']:
            msg = 'Transfer complete'
            print msg
            rFile = DataConnection.fileData
            print rFile
            #Save file
            return (True, msg,entryNames,entryTypes)
        elif code == replyCodes['Cant_Open_Data_Connection'] or code == replyCodes['Connection_Closed'] or code == replyCodes['Action_Aborted_Local']:
            DataConnection.Close()
            return codeCommands[code]()

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
            return codeCommands[code]()
    else:
        msg = "Not connected"
        print msg
        return (False, msg)

def GetCurrentDir():
    Send('PWD')
    code, message = Receive(getMessage=True)
    if code == replyCodes['Pathname_Created']:
        if message[0] == '\"':
            message = message[1:]
        if message[-1] == '\"':
            message = message[:-1]
        message = message.replace('\"\"', '\"')
        return (True, message)
    else:
        return codeCommands[code]()

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

def Restart():
    msg = "Restart needed"
    print msg
    return (False,msg)



codeCommands = {
    '110': Restart(),
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

''' Testing Code '''
StartUp(s_name, s_port)
Login()
PassiveMode()
print GetCurrentDir()
ChangeDirectory('/test/')
print GetCurrentDir()
ChangePort(10000)
