from socket import *
import threading
import DataConnection

''' All Code in this file is Written by Shane House (749524) '''
#Opens the file containing the responses and codes
responsesFile = open('../Command_Response_Database/response.txt', 'r')
#Creates an array of the responses and their codes
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
#Defines the file endline
CRLF = '\r\n'

#splits the reply from the message and returns them
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

#recievs a reply from the server and returns either a code and a message
#or just a code
def Receive(bufferSize=2048, getMessage=False):
    message = c_socket.recv(bufferSize)
    code, msg = ParseReply(message)
    print str(code) + " " + msg
    if getMessage:
        return str(code), msg
    return str(code)

#Sends a code to the server
def Send(code):
    code = code + CRLF
    c_socket.send(code)

#Creates a socket and attempts to establish the control connection with
#the server. it returns true or false depending on whether it was
#successful or not as well as a message describing the responce
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

#Sends the USER command to the server along with the username passed to the
#function, it then waits for a reply and returns true or false depending on the
#outcome with a message that discribes the outcome
def Login():
    Send('USER ' + username)
    code = Receive()
    if code == replyCodes['Logged_In']:
        return (True, "Logged in")
    return codeCommands[code]()

#Sends the password to the server if asked for one. Returns true or false depending
#on the outcome with a message that discribes the outcome.
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

#Sends the account information to the server and returns true or false depending
#on the outcomes with a message that discribes the outcome
def EnterAccount():
    Send('ACCT ' + account)
    code = Receive()
    print 'Sent account'
    if code == replyCodes['Logged_In']:
        msg = 'Logged in'
        print msg
        return (True, msg)
    return codeCommands[code]()

#A function called when log in fails returns false and a message saying not logged
#in
def LoginFail():
    msg = 'Not logged in'
    print msg
    return (False, msg)

#Sends the command to change the server directory to the given path, returns true
# or false depending on the outcome and a message that describes the outcome
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

#Sends the command to the server to make it change to its parent directory and
#returns true or false depending on the outcome
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

#Formats list data retrieved from the data connection, removing unneeded information
#and determining whether a field is a file of folder, returns 2 arrays one holding
#The file names and the other holding the types
def getList(listData):
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

#sends the command to retrieve a list of file information from the server.
#returns true or false depending on the outcome, a message describing the outcome
#And 2 arrays, one containing the file names, and the other containing the file types
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

#Sends the port command to the server using the port number specified. returns
#true or false depending on the outcome and a message describing the outcome
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

#Sends the type command to the server and checks if the server supports the input
#type. it returns true or false depending on the outcome and a message describing
#the outcome
def CheckType(type1, type2):
    sendString = ["TYPE",type1,type2]
    sendString = ' '.join(sendString)
    Send(sendString)
    code = Receive()
    if code == replyCodes['Command_OK']:
        msg = 'The Server supports ASCII Non-print'
        print msg
        return (True,msg)
    else:
        return codeCommands[code]()

#Sends the mode command to the server to check whether is supports the input
#transfer mode. Returns true or false depending on the outcome and a message
#describing the outcome
def CheckMode(mode):
    sendString = "MODE " + mode
    Send(sendString)
    code = Receive()
    if code == replyCodes['Command_OK']:
        msg = 'The Server supports stream mode'
        print msg
        return (True,msg)
    else:
        return codeCommands[code]()

#Sends the structure command to the server to check if it supports the input type
#returns true or false depending on the outcome and a message describing the outcome
def CheckStructure(structure):
    sendString = "STRU " + structure
    Send(sendString)
    code = Receive()
    if code == replyCodes['Command_OK']:
        msg = 'The Server supports file mode'
        print msg
        return (True,msg)
    else:
        return codeCommands[code]()

#Sends the pasv command to the server, sets the data connection address and port to reflect
#what is returned by the server. It returns true or false depending on the outcome and a
#message that describes the outcome
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

#Sends the retr command to the server along with the given path to the file the
#server needs to send. It then establishes a data connection. After
#this it writes to a file with the name specified by the second parameter. returns
#true or false and a message that describes the outcome of this action.
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
        try:
            code = Receive()
        except timeout:
            continue

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

#This function sends the stor command to the server. It then establishes a data
#connection and then opens and reads the file to be uploaded and sends it over
#the data connection. returns true or false and a message depending on the outcome
#of the action
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
            DataConnection.Close()
            msg = 'Transfer complete'
            print msg
            return (True, msg)
        elif code == replyCodes['Cant_Open_Data_Connection'] or code == replyCodes['Connection_Closed'] or code == replyCodes['Action_Aborted_Local']:
            DataConnection.Close()
            return codeCommands[code]()
    DataConnection.Close()
    c_socket.settimeout(None)
    code = Receive()
    if code == replyCodes['Closing_Data_Connection']:
        msg = 'Transfer complete - Closing data connection'
        print msg
        return (True, msg)
    elif code == replyCodes['File_Action_Completed']:
        msg = 'Transfer complete'
        print msg
        return (True, msg)
    elif code == replyCodes['Cant_Open_Data_Connection'] or code == replyCodes['Connection_Closed'] or code == replyCodes['Action_Aborted_Local']:
        return codeCommands[code]()
    msg = 'Successfully sent data'
    return (True, msg)

#Logs the user out of the server, also runs when the client window is closed
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

#sends the print current directory command to the server and sets the currentDirectory
#global variable to a slightly edited version of what is returned by the server
#Returns true or false depending on the outcome and a message describing the outcome
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

#Sends the no op command to the server returns true or false and a message
#depending on the outcome
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

#Closes the socket
def CloseConnection():
    c_socket.close()

#The functions below all just return either true or false and a message
#They do not perform a function other than to be called by the functions above
#to accurately describe the code sent back by the server. i.e the server sends
#back a reply and the code will be looked up in a table below, and one of these
#functions will be called to return the correct boolian and message to the user.
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

def CommandNotImplementedParam():
    msg = "Command not implemented for that parameter"
    print msg
    return (False,msg)


#This dictionary runs the needed function above based on the reply code returned by
#the server
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
    '504': CommandNotImplementedParam,
    '530': LoginFail,
    '532': NoAccount,
    '550': FileActionFailed,
    '551': AbortPageType,
    '552': AbortStorage,
    '553': NameNotAllowed
}
