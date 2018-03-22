import threading
import Users
import os
import random

responsesFile = open('../Command_Response_Database/response.txt', 'r')
replyCodes = {}
for line in responsesFile:
    msg, code = line.split(' ', 1)
    code = code.rstrip()
    replyCodes[msg] = code
responsesFile.close()

CRLF = '\r\n'

DefaultPath = './User_Folders'
DefaultDataPort = 20

# commandFile = open('../Command_Response_Database/command.txt', 'r')
# commands = {}
# for line in commandFile:
#     command, function = line.split(' ', 1)
#     commands[command] = function
# commandFile.close()
#
# replyCodeFile = open('../Command_Response_Database/response.txt', 'r')
# replyCodes = {}
#
# for line in replyCodeFile:
#     message, code = line.split(' ', 1)
#     replyCodes[message] = code
# replyCodeFile.close()
class UserThread (threading.Thread):
    msg = str()
    username = str()
    loggedIn = False
    running = True
    baseDirectory = DefaultPath
    currentDirectory = str()
    dataHost = str()
    dataPort = DefaultDataPort
    initiateDataConnection = True

    def __init__(self, threadName, threadID, conn_socket, address):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadName
        self.conn_socket = conn_socket
        self.address = address
        self.dataHost = address[0]

        self.Send('Service_OK')
    # def __init__(self):
    #     self.name = "hello"
    def run(self):
        # print self.name + " is ready to use"
        # while self.msg != 'exit':
        self.msg = self.conn_socket.recv(2048)
            # print 'The message (from ' + str(address) + ') is: ' + self.msg
            # self.conn_socket.send(self.msg)
        self.ExecuteCommand(self.msg)

    def Send(self, code, message=str()):
        if message != str():
            code = replyCodes[code] + ' ' + message + CRLF
        else:
            code = replyCodes[code] + CRLF
        self.conn_socket.send(code)

    def Receive(self, bufferSize=2048):
        message = self.conn_socket.recv(bufferSize)
        cmd, args = self.ParseCommand(message)
        if cmd == "QUIT":
            commands[cmd](args)
            return
        return cmd, args

    def Login(self, args):
        if self.loggedIn:
            self.Send('Logged_In')
            return

        self.username = args[0]
        try:
            currentUser = Users.users[self.username]
        except KeyError:
            self.Send('Not_Logged_In', 'Incorrect')
            return

        if currentUser.password != Users.defaultPassword:
            self.EnterPassword(currentUser)
        elif currentUser.account != Users.defaultAccount:
            self.EnterAccount(currentUser)
        else:
            self.Send('Logged_In')
            self.loggedIn = True
            self.baseDirectory += self.username + '/'

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
                    self.baseDirectory += self.username + '/'
                else:
                    self.EnterAccount(currentUser)
            else:
                self.Send('Not_Logged_In')
        else:
            self.Send('Bad_Sequence')

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
                self.baseDirectory += self.username + '/'
            else:
                self.Send('Not_Logged_In')
        else:
            self.Send('Bad_Sequence')

    def Logout(self, args):
        self.Send('Closed')
        self.conn_socket.close()
        print ('\n' + self.name +  ' has been closed')
        self.running = False
# TODO: add defaults as necessary
    def Reinitialise(self, args):
        # Reset all user variables to default
        self.loggedIn = False
        self.username = str()
        self.baseDirectory = DefaultPath
        self.currentDirectory = str()

    def DataPortChange(self, args):
        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return

        hostPort = args[0].split(',')
        self.dataHost = '.'.join(hostPort[0:4])
        self.dataPort = int(hostPort[4]) * 256 + int(hostPort[5])
        self.Send('Command_OK')

    def PassiveMode():
        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return

        random.seed()
        self.dataPort = random.randint(1024, 65534)
        self.initiateDataConnection = False

    def NoOp(self, args):
        self.Send('Command_OK')

    def ChangeDirectory(self, args):
        path = args[0]
        path = path

        if self.loggedIn == False:
            self.Send('Not_Logged_In')
            return
        elif os.path.exists(self.baseDirectory + path) == False:
            # Send 550 response (file not found)
            self.Send('Action_Not_Taken')
            return

        if path[-1] != '/':
            path += '/'
        self.currentDirectory = path
        # Send successful command
        self.Send(File_Action_Completed)

    def ChangeUp(self,args):
        testPath = "/".join(self.currentDirectory.split("/")[:-1])
        if os.path.exists(self.baseDirectory + testPath):
            self.currentDirectory = testPath
            self.Send('File_Action_Completed')
        else:
            self.Send('Action_Not_Taken')

    def NotImplemented(self, args):
        self.Send('Command_Not_Implemented')

    def ParseCommand(self, msg):
        # TODO: parse cmd (strip out key stuff)
        # TODO: keep receiving until CRLF char is found
        # Removes the CRLF command terminator
        message = msg.split('\r\n', 1)
        message = message[0].split(" ")
        command = str.upper(message.pop(0))
        return (command, message)

    commands = {
        'USER': Login,
        'PASS': EnterPassword,
        'ACCT': EnterAccount,
        'CWD': ChangeDirectory,
        'CDUP': ChangeUp,
        'QUIT': Logout,
        'REIN': Reinitialise,
        'PORT': DataPortChange,
        'PASV': PassiveMode,
        'NOOP': NoOp
    }

    def ExecuteCommand(self, message):
        cmd, msg = self.ParseCommand(message)
        # TODO: check if there is another command in the data sent
        try:
            self.commands[cmd](self, msg)
        except KeyError:
            self.Send('Syntax_Error')
        except TypeError:
            print 'Error calling command'
            self.Send('Argument_Error')

        if self.running:
            self.run()
        # except TypeError:
        #     print 'Too Many Arguments'
        #     userThread.run()
    '''
    USER <SP> <username> <CRLF>
    PASS <SP> <password> <CRLF>
    ACCT <SP> <account-information> <CRLF>
    CWD  <SP> <pathname> <CRLF>
    CDUP <CRLF>
    SMNT <SP> <pathname> <CRLF>
    QUIT <CRLF>
    REIN <CRLF>
    PORT <SP> <host-port> <CRLF>
    PASV <CRLF>
    TYPE <SP> <type-code> <CRLF>
    STRU <SP> <structure-code> <CRLF>
    MODE <SP> <mode-code> <CRLF>
    RETR <SP> <pathname> <CRLF>
    STOR <SP> <pathname> <CRLF>
    STOU <CRLF>
    APPE <SP> <pathname> <CRLF>
    ALLO <SP> <decimal-integer>
        [<SP> R <SP> <decimal-integer>] <CRLF>
    REST <SP> <marker> <CRLF>
    RNFR <SP> <pathname> <CRLF>
    RNTO <SP> <pathname> <CRLF>
    ABOR <CRLF>
    DELE <SP> <pathname> <CRLF>
    RMD  <SP> <pathname> <CRLF>
    MKD  <SP> <pathname> <CRLF>
    PWD  <CRLF>
    LIST [<SP> <pathname>] <CRLF>
    NLST [<SP> <pathname>] <CRLF>
    SITE <SP> <string> <CRLF>
    SYST <CRLF>
    STAT [<SP> <pathname>] <CRLF>
    HELP [<SP> <string>] <CRLF>
    NOOP <CRLF>
    '''
