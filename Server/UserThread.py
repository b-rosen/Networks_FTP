import threading
import Users
import os
import random
import DataConnection
from socket import gethostname, gethostbyname, timeout
from subprocess import check_output
from platform import system

''' Written by Benjamin Rosen (858324) '''
# Opens the file containing all response codes. Necessary when deciding which response code to send to the user.
responsesFile = open('../Command_Response_Database/response.txt', 'r')
replyCodes = {}
for line in responsesFile:
    msg, code = line.split(' ', 1)
    code = code.rstrip()
    replyCodes[msg] = code
responsesFile.close()

CRLF = '\r\n'

DefaultPath = './User_Folders/'
DefaultDataPort = 20

# Main class that represents each user. Since it is run on a separate thread, it inherits from the threading class.
class UserThread(threading.Thread):
    msg = str()
    username = str()
    currentDirectory = '/'

 # Written by Benjamin Rosen (858324)
    # Initialises the thread, giving it an id, connection socket and address. The user is set to not logged, and the base directory is set to the default path (i.e. the absolute path to the User_Folders directory)
    def __init__(self, threadName, threadID, conn_socket, address):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadName
        self.conn_socket = conn_socket
        self.address = address
        self.loggedIn = False
        self.running = True
        self.baseDirectory = DefaultPath
        # Tell the client that the system is functioning correctly
        self.Send('Service_OK')

# Written by Benjamin Rosen (858324)
    # This is the main loop of the thread. It will keep receiving commands from the client and calling a function to execute the command.
    def run(self):
        cmd, msg = self.Receive()
        self.ExecuteCommand(cmd, msg)

# Written by Benjamin Rosen (858324)
    # Sends the return code back to the client. It uses the responses dictionary to find the code number to send. It also allows a custom message to be sent back, which could be used to give the client more detail with regards to the response.
    def Send(self, code, message=str()):
        if message != str():
            code = replyCodes[code] + ' ' + message + CRLF
        else:
            code = replyCodes[code] + CRLF
        self.conn_socket.send(code)

# Written by Benjamin Rosen (858324)
    # Receives the command from the client and then calls another function to parse the command (strip out the CRLF symbol, separate command from arguments etc.).
    def Receive(self, bufferSize=2048):
        message = ''
        while CRLF not in message:
            message = self.conn_socket.recv(bufferSize)
            cmd, args = self.ParseCommand(message)
            return cmd, args

# Written by Benjamin Rosen (858324)
    # Allows the client to log in. It first checks the level of access that the client needs to log in (password or account, or both). It then either logs the user in, or calls the corresponding function that will reply to the client whether it needs a password or account.
    def Login(self, args):
        if self.loggedIn:
            self.Send('Logged_In')
            return

        self.username = args[0]
        try:
            currentUser = Users.users[self.username]
        except KeyError:
            self.Send('Not_Logged_In', 'Username does not exist')
            return

        if currentUser.password != Users.defaultPassword:
            self.EnterPassword(currentUser)
        elif currentUser.account != Users.defaultAccount:
            self.EnterAccount(currentUser)
        else:
            self.Send('Logged_In')
            self.loggedIn = True
            self.baseDirectory += self.username

# Written by Benjamin Rosen (858324)
    # Prompts the client for a password through a reply code. It then checks if the given password is correct for the user, and either logs the user in or calls the function to check for account requirements.
    def EnterPassword(self, currentUser):
        if self.loggedIn:
            self.Send('Logged_In')
            return
        elif type(currentUser) is not Users.UserInfo:
            self.Send('Not_Logged_In')
            return

        self.Send('Need_Password')
        cmd, args = self.Receive()
        password = args[0]
        if cmd == 'PASS':
            if password == currentUser.password:
                if currentUser.account == Users.defaultAccount:
                    self.Send('Logged_In')
                    self.loggedIn = True
                    self.baseDirectory += self.username
                else:
                    self.EnterAccount(currentUser)
            else:
                self.Send('Not_Logged_In', 'Incorrect password')
        else:
            self.Send('Bad_Sequence')

# Written by Benjamin Rosen (858324)
    # Prompts the client for a account through a reply code. It then checks if the given account is correct for the user, and either logs the user in or tells the user they are not logged in.
    def EnterAccount(self, currentUser):
        if self.loggedIn:
            self.Send('Logged_In')
            return
        elif type(currentUser) is not Users.UserInfo:
            self.Send('Not_Logged_In')
            return

        self.Send('Need_Account')
        cmd, args = self.Receive()
        account = args[0]
        if cmd == 'ACCT':
            if account == currentUser.account:
                self.Send('Logged_In')
                self.loggedIn = True
                self.baseDirectory += self.username
            else:
                self.Send('Not_Logged_In')
        else:
            self.Send('Bad_Sequence')

# Written by Benjamin Rosen (858324)
    # Changes the current directory seen by the server when executing default commands (such as list without a path)
    def ChangeDirectory(self, args):
        path = args[0]
        path = path

        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return
        elif os.path.exists(self.baseDirectory + path) == False:
            self.Send('Action_Not_Taken', 'File not found')
            return

        if path[-1] != '/':
            path += '/'
        self.currentDirectory = path
        self.Send('File_Action_Completed')

# Written by Benjamin Rosen (858324)
    # Goes up one directory and stores this as the current directory. Tells the client that the change was successful
    def ChangeUp(self,args):
        if len(self.currentDirectory) == 1:
            self.Send('Action_Not_Taken', 'Already at root directory')
            return

        testPath = self.currentDirectory.split("/")[:-2]
        testPath.append(str())
        testPath = "/".join(testPath)
        if os.path.exists(self.baseDirectory + testPath):
            self.currentDirectory = testPath
            self.Send('File_Action_Completed')
        else:
            self.Send('Action_Not_Taken')

# Written by Benjamin Rosen (858324)
    # Logs the user out and closes the control connection between client and server. The current thread is terminated.
    def Logout(self, args):
        self.Send('Closed')
        self.conn_socket.close()
        print ('\n' + self.name +  ' has been closed')
        self.running = False
        self.loggedIn = False

# Written by Benjamin Rosen (858324)
    # Resets all user variables to default, while keeping the user logged in
    def Reinitialise(self, args):
        self.loggedIn = False
        self.username = str()
        self.baseDirectory = DefaultPath
        self.currentDirectory = str()

# Written by Benjamin Rosen (858324)
    # Changes the default port used by the server for the data connection to the one specified by the user. It also sets the data connection to initate the connection when a transfer request is made. Lets the client know that the port was changed correctly.
    def DataPortChange(self, args):
        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return

        hostPort = args[0].split(',')
        DataConnection.address = '.'.join(hostPort[0:4])
        DataConnection.port = int(hostPort[4]) * 256 + int(hostPort[5])
        DataConnection.initiateConn = True
        self.Send('Command_OK')

# Written by Shane House (749524)
    # Checks whether the given representation type is supported by this server and lets the user know.
    def CheckType(self,args):
        testType = args[0].split()
        if testType[0] == 'A' and testType[1] == 'N':
            self.Send('Command_OK')
        else:
            self.Send('Not_Implemented_Param')

# Written by Shane House (749524)
    # Checks if the specified mode of transmission is supported by this server and tells the user.
    def CheckMode(self,args):
        if args[0] == 'S':
            self.Send('Command_OK')
        else:
            self.send('Not_Implemented_Param')

# Written by Shane House (749524)
    # Checks if the file structure specified is supported by this server and tells the user.
    def CheckStructure(self,args):
        if args[0] == 'F':
            self.Send('Command_OK')
        else:
            self.send('Not_Implemented_Param')

# Written by Benjamin Rosen (858324)
    # Creates a port number that this server will use for the data connection. It first generates a random number (higher than the reserved ports but lower than the maximum port number). It replies to the client, specifying the IP address and port that it will listen to when connecting the data connection.
    def PassiveMode(self, args):
        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return

        random.seed()
        DataConnection.port = random.randint(1024, 65534)
        replyAddress = gethostbyname(gethostname()).replace('.', ',')
        replyPort = ','.join((str(int(DataConnection.port) / 256), str(DataConnection.port % 256)))
        reply = ','.join((replyAddress, replyPort))
        DataConnection.initiateConn = False
        self.Send('Passive_Mode', reply)

# Written by Benjamin Rosen (858324)
    # Mimics the ls -l command on UNIX for the given directory path (or the current directory if it is not specified). Creates a parallel process that deals with the data connection, using the data transfer parameters set through other commands (PORT, PASV). It sends all the data and then tells the client that the connection will be closed and then closes the data connection.
    def ListDir(self, args):
        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return

        connected = DataConnection.connected
        DataConnection.Connect()

        if connected:
            self.Send('Data_Connection_Open')
        else:
            self.Send('File_Status_Ok')
        dirPath = str()
        if len(args) == 0:
            dirPath = self.baseDirectory + self.currentDirectory
        else:
            dirPath = self.baseDirectory + args[0]

        # Special code for windows, that uses the DIR command (instead of ls) and formats it so that it mimics the ls command for the most important information (if the entry is a directory or file and the file name)
        if system() == "Windows":
            windowsPath = dirPath.replace('/','\\')
            data = check_output(['dir', windowsPath],shell=True)

            data = data.split(CRLF)
            if data != str():
                data = data[7:-3]
                temp = []
                for lines in data:
                    lines = lines.split()
                    if lines[3] == "<DIR>":
                        lines[0] = 'd'
                    else:
                        lines[0] = '-'
                    while len(lines) < 9:
                        lines.insert(2, 'dummy')
                    lines = ' '.join(lines)
                    temp.append(lines)
                data = temp
        else:
            data = check_output(['ls', '-l', dirPath])
            if data != str():
                data = data.split('\n')
                data.pop(0)
                data.pop(-1)
        DataConnection.data = CRLF.join(data)
        data_thread = threading.Thread(None, DataConnection.SendData)
        data_thread.start()

        self.conn_socket.settimeout(0.5)
        while DataConnection.active:
            try:
                message = self.conn_socket.recv(2048)
            except timeout:
                continue

            cmd, args = self.ParseCommand(message)
            if cmd == "QUIT" or cmd == 'ABOR' or cmd == 'STAT':
                commands[cmd](args)
                return
        self.conn_socket.settimeout(None)
        self.Send('Closing_Data_Connection')
        DataConnection.Close()

# Written by Benjamin Rosen (858324)
    # Compiles a list of files/directories for the given directory path (or the current directory if it is not specified). Creates a parallel process that deals with the data connection, using the data transfer parameters set through other commands (PORT, PASV). It sends all the data and then tells the client that the connection will be closed and then closes the data connection.
    def ListNames(self, args):
        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return

        connected = DataConnection.connected
        DataConnection.Connect()

        if connected:
            self.Send('Data_Connection_Open')
        else:
            self.Send('File_Status_Ok')

        dirPath = str()
        if len(args) == 0:
            dirPath = self.baseDirectory + self.currentDirectory
        else:
            dirPath = self.baseDirectory + args[0]
        data = os.listdir(dirPath)
        if len(data) > 0 and data[0] == '.DS_Store':
            data.pop(0)
        DataConnection.data = CRLF.join(data)
        data_thread = threading.Thread(None, DataConnection.SendData)
        data_thread.start()

        self.conn_socket.settimeout(0.5)
        while DataConnection.active:
            try:
                message = self.conn_socket.recv(2048)
            except timeout:
                continue

            cmd, args = self.ParseCommand(message)
            if cmd == "QUIT" or cmd == 'ABOR' or cmd == 'STAT':
                commands[cmd](args)
                return
        self.conn_socket.settimeout(None)
        self.Send('Closing_Data_Connection')
        DataConnection.Close()

# Written by Benjamin Rosen (858324)
    # Sends a file to client over the data connection. It first checks that the given path exists in the user's folder and then opens and reads the file. It sends all the data and then tells the client that the connection will be closed and then closes the data connection.
    def SendFile(self, args):
        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return

        if len(args) > 0:
            dirPath = args[0]
        else:
            self.Send('Argument_Error', 'No Pathname Specified')
            return

        connected = DataConnection.connected
        DataConnection.Connect()

        if os.path.exists(self.baseDirectory + args[0]) == False:
            self.Send('Action_Not_Taken', 'File does not exist')
            return

        data = []
        try:
            file = open(self.baseDirectory + args[0], 'rb')
            for line in file:
                data.append(line)
            file.close()
        except IOError:
            self.Send('Action_Not_Taken', 'Given Path is a Directory')
            return

        if connected:
            self.Send('Data_Connection_Open')
        else:
            self.Send('File_Status_Ok')

        DataConnection.data = ''.join(data)
        data_thread = threading.Thread(None, DataConnection.SendData)
        data_thread.start()

        self.conn_socket.settimeout(0.5)
        while DataConnection.active:
            try:
                message = self.conn_socket.recv(2048)
            except timeout:
                continue

            cmd, args = self.ParseCommand(message)
            if cmd == "QUIT" or cmd == 'ABOR' or cmd == 'STAT':
                commands[cmd](args)
                return
        self.conn_socket.settimeout(None)
        self.Send('Closing_Data_Connection')
        DataConnection.Close()

# Written by Benjamin Rosen (858324)
    # Receives a file from the client over the data connection. It first checks that the given path exists in the user's folder, and that the pathname is not a directory, and opens the data connection. It receives all the data and then tells the client that the connection will be closed and then closes the data connection. The data is then written to the specified file.
    def ReceiveFile(self, args):
        connected = DataConnection.connected
        DataConnection.Connect()

        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return

        if len(args) > 0:
            dirPath = args[0]
        else:
            self.Send('Argument_Error', 'No Pathname Specified')
            return

        try:
            file = open(self.baseDirectory + args[0], 'wb')
        except IOError:
            self.Send('Action_Not_Taken', 'Given Path is a Directory')
            return

        if connected:
            self.Send('Data_Connection_Open')
        else:
            self.Send('File_Status_Ok')

        data_thread = threading.Thread(None, DataConnection.GetData)
        data_thread.start()

        self.conn_socket.settimeout(0.5)
        while DataConnection.active:
            try:
                message = self.conn_socket.recv(2048)
            except timeout:
                continue

            cmd, args = self.ParseCommand(message)
            if cmd == "QUIT" or cmd == 'ABOR' or cmd == 'STAT':
                commands[cmd](args)
                return
        DataConnection.Close()
        self.conn_socket.settimeout(None)
        self.Send('Closing_Data_Connection')

        file.write(DataConnection.data)
        file.close()

# Written by Benjamin Rosen (858324)
    # Responds to the client with the current path that the server is at, with / representing the root folder (which is the root of the user's folder in User_Folders)
    def PrintCurrentDir(self, args):
        if os.path.exists(self.baseDirectory + self.currentDirectory):
            dir = self.currentDirectory.replace('\"', '\"\"')
            self.Send('Pathname_Created', '\"' + dir + '\"' + 'Was requested')
        else:
            self.Send('Action_Not_Taken')

# Written by Benjamin Rosen (858324)
    # Responds with a 'OK' reply, to let the user know that the server is still running
    def NoOp(self, args):
        self.Send('Command_OK')

# Written by Benjamin Rosen (858324)
    # Catch-all function that tells the client that the specified command is not implemented at this time.
    def NotImplemented(self, msg):
        self.Send('Command_Not_Implemented', 'Sorry, this command is not implemented for this server')

# Written by Benjamin Rosen (858324)
    # Keeps receiving the command until the CRLF specifier is found. It then strips out the text before this specifier. This text is further processed (using the space character) to extract the command and arguments/messages that the client has attached.
    def ParseCommand(self, msg):
        message = msg.split(CRLF, 1)
        message = message[0].split(" ", 1)
        command = str.upper(message.pop(0))
        return (command, message)

# Written by Benjamin Rosen (858324)
    # Dictionary of commands specified in RFC 959, which links the commands' characters to a function to be called for each command. The NotImplemented function is used for unimplemented commands.
    commands = {
        'USER': Login,
        'PASS': EnterPassword,
        'ACCT': EnterAccount,
        'CWD': ChangeDirectory,
        'CDUP': ChangeUp,
        'QUIT': Logout,
        'MODE': CheckMode,
        'TYPE': CheckType,
        'STRU': CheckStructure,
        'REIN': Reinitialise,
        'RETR': SendFile,
        'STOR': ReceiveFile,
        'PORT': DataPortChange,
        'PASV': PassiveMode,
        'LIST': ListDir,
        'NLST': ListNames,
        'PWD': PrintCurrentDir,
        'NOOP': NoOp,

        'SMNT': NotImplemented,
        'STOU': NotImplemented,
        'APPE': NotImplemented,
        'ALLO': NotImplemented,
        'REST': NotImplemented,
        'RNFR': NotImplemented,
        'RNTO': NotImplemented,
        'ABOR': NotImplemented,
        'DELE': NotImplemented,
        'RMD': NotImplemented,
        'MKD': NotImplemented,
        'SITE': NotImplemented,
        'SYST': NotImplemented,
        'STAT': NotImplemented,
        'HELP': NotImplemented
    }

# Written by Benjamin Rosen (858324)
    # The correct function is selected from the command dictionary based on the command, and the arguments are passed to that function, which will use its own parsing based on its unique needs (for example, PORT will strip out the port and address from the arguements while LIST will use the arguemnt as the path to check). If the command does not exist in the dictionary, or the arguments passed to the function throws a TypeError (such as a string instead of an int), the server reponds with the corresponding error code. It then continues in the thread loop.
    def ExecuteCommand(self, cmd, msg):
        try:
            self.commands[cmd](self, msg)
        except KeyError:
            self.Send('Syntax_Error')
        except TypeError:
            print 'Error calling command'
            self.Send('Argument_Error')

        if self.running:
            self.run()
