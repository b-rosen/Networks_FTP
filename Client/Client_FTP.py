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
    print str(code) + " " + msg
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
    global currentDirectory

    Send('CWD ' + path)
    code = Receive()
    if code == replyCodes['File_Action_Completed']:
        currentDirectory = path
        if currentDirectory[-1] != '/':
            currentDirectory += '/'
        msg = 'Directory changed'
        print msg
        return (True,msg)
    else:
        return codeCommands[code]()

def ChangeUp():
    global currentDirectory
    if currentDirectory == '/':
        return (False, 'At root directory')
    Send('CDUP')
    code = Receive()
    if code == replyCodes['File_Action_Completed']:
        currentDirectory = currentDirectory.split("/")[:-2]
        currentDirectory.append(str())
        currentDirectory = "/".join(currentDirectory)
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
    if lines[-1] == '':
        lines.pop(-1)

    for line in lines:
        values = line.split()
        extraInfo = 9 - len(values)
        if extraInfo < 0:
            singleFile =  ' '.join(values[extraInfo-1:])
            values = values[:extraInfo-1]
            values[-1] = singleFile
        entryName.append(values[len(values)-1])
        if values[0][0] == 'd':
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

    try:
        DataConnection.Connect()
    except Exception:
        return (False,"Could not create data connection",[],[])

    code = Receive()
    if code == replyCodes['Data_Connection_Open']:
        print 'Data Connection Already open'
    elif code == replyCodes['File_Status_Ok']:
        print 'Opening data connection'
    else:
        return codeCommands[code](),[],[]
    data_thread = threading.Thread(None, DataConnection.GetData)
    data_thread.start()

    while True:
        try:
            code = Receive()
        except timeout:
            continue
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
            return codeCommands[code](),[],[]

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
        if len(hostPort[0]) > 3:
            hostPort[0] = hostPort[0].split('(')[1]
            hostPort[-1] = hostPort[-1].split(')')[0]
        DataConnection.address = '.'.join(hostPort[0:4])
        DataConnection.port = int(hostPort[4]) * 256 + int(hostPort[5])
        print DataConnection.address
        print DataConnection.port
        DataConnection.initiateConn = True
        msg = 'Entered Passive Mode'
        print msg
        return (True, msg)
    else:
        return codeCommands[code]()

def Download(filePath, savePath):
    Send('RETR '+ filePath)

    try:
        DataConnection.Connect()
    except Exception:
        return (False,"Could not create data connection")

    code = Receive()
    if code == replyCodes['Data_Connection_Open']:
        print 'Data Connection Already open'
    elif code == replyCodes['File_Status_Ok']:
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
            file = open(savePath, 'wb')
            file.write(DataConnection.data)
            file.close()
            return (True, msg)
        elif code == replyCodes['File_Action_Completed']:
            msg = 'Transfer complete'
            print msg
            file = open(savePath, 'wb')
            file.write(DataConnection.data)
            file.close()
            return (True, msg)
        elif code == replyCodes['Cant_Open_Data_Connection'] or code == replyCodes['Connection_Closed'] or code == replyCodes['Action_Aborted_Local']:
            DataConnection.Close()
            return codeCommands[code]()

def Upload(filePath,serverPath):
    global c_socket
    Send('STOR ' + serverPath)

    try:
        DataConnection.Connect()
    except Exception:
        return (False,"Could not create data connection")

    code = Receive()
    if code == replyCodes['File_Status_Ok'] or code == replyCodes['Data_Connection_Open']:
        print 'Connection Successful'
    else:
        return codeCommands[code]()

    data = []
    try:
        file = open(filePath, 'rb')
        for line in file:
            data.append(line)
        file.close()
    except IOError:
        self.Send('Action_Not_Taken', 'Given Path is a Directory')
        return

    DataConnection.data = ''.join(data)

    data_thread = threading.Thread(None, DataConnection.SendData)
    data_thread.start()

    c_socket.settimeout(0.5)
    while DataConnection.active:
        try:
            code = Receive()
        except timeout:
            continue

        if code == replyCodes['Closing_Data_Connection']:
            DataConnection.Close()
            msg = 'Transfer complete - Closing data connection'
            print msg
            return (True, msg)
        elif code == replyCodes['File_Action_Completed']:
            msg = 'Transfer complete'
            print msg
            return (True, msg)
        elif code == replyCodes['Cant_Open_Data_Connection'] or code == replyCodes['Connection_Closed'] or code == replyCodes['Action_Aborted_Local']:
            DataConnection.Close()
            return codeCommands[code]()
    DataConnection.Close()
    c_socket.settimeout(None)
    msg = 'Successfully sent data'
    return (True, msg)

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
    global currentDirectory

    Send('PWD')
    code, path = Receive(getMessage=True)
    if code == replyCodes['Pathname_Created']:
        path = path.split('\"')[1]
        print path
        if path[0] == '\"':
            path = path[1:]
        if path[-1] == '\"':
            path = path[:-1]
        path = path.replace('\"\"', '\"')
        currentDirectory = path
        print 'current Dir: ' + path
        return (True, path)
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

def NoStorage():
    msg = "Insufficient Storage Space"
    print msg
    return (False,msg)

def NoAccount():
    msg = "Need account for storing files"
    print msg
    return (False,msg)

def AbortPageType():
    msg = "Action aborted: Page type unknown"
    print msg
    return (False,msg)

def AbortStorage():
    msg = "Action aborted: Exceeded storage allocation"
    print msg
    return (False,msg)

def NameNotAllowed():
    msg = "File name not allowed"
    print msg
    return (False,msg)


codeCommands = {
    '110': Restart,
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
    '452': NoStorage,
    '500': BadSyntax,
    '501': BadArgument,
    '502': NoCommand,
    '503': BadCommandOrder,
    '530': LoginFail,
    '532': NoAccount,
    '550': FileActionFailed,
    '551': AbortPageType,
    '552': AbortStorage,
    '553': NameNotAllowed
}

''' Testing Code '''
#StartUp(s_name, s_port)
#Login()
#print GetCurrentDir()
#ChangeDirectory('/test/')
#print GetCurrentDir()
# ChangePort(10000)
# PassiveMode()
# if ListFiles('/'):
#     print DataConnection.data
#PassiveMode()
#Download('/testfile.txt', 'testfile.txt')
