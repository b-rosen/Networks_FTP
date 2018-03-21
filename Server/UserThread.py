import threading
import Users

responsesFile = open('../Command_Response_Database/response.txt', 'r')
replyCodes = {}
for line in responsesFile:
    msg, code = line.split(' ', 1)
    code = code.rstrip()
    replyCodes[msg] = code
responsesFile.close()

CRLF = '\r\n'

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

    def __init__(self, threadName, threadID, conn_socket, address):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadName
        self.conn_socket = conn_socket
        self.address = address

        self.Respond('Service_OK')
    # def __init__(self):
    #     self.name = "hello"
    def run(self):
        # print self.name + " is ready to use"
        # while self.msg != 'exit':
        self.msg = self.conn_socket.recv(2048)
            # print 'The message (from ' + str(address) + ') is: ' + self.msg
            # self.conn_socket.send(self.msg)
        self.ExecuteCommand(self.msg)

    def Respond(self, code):
        code = replyCodes[code] + '\r\n'
        self.conn_socket.send(code)

    def Receive(self, bufferSize=2048):
        message = self.conn_socket.recv(bufferSize)
        cmd, args = self.ParseCommand(message)
        if cmd == "QUIT":
            commands[cmd](args)
            return
        return cmd, args

    def Login(self, args):
        # TODO: Sends back ok message, waits for password
        self.username = args[0]
        # TODO: check if username exists
        self.Respond('Need_Password')
        cmd, args = self.Receive()
        if cmd == "PASS":
            if args[0] == Users.users[self.username]:
                self.Respond('Logged_In')
                self.run()

    def Logout(self, args):
        self.Respond('Closed')
        self.conn_socket.close()
        print ('\n' + self.name +  ' has been closed')

    def NoOp(self, args):
        self.Respond('Command_OK')
        self.run()

    def ParseCommand(self, msg):
        # TODO: parse cmd (strip out key stuff)
        # Removes the CRLF command terminator
        message = msg.split('\r\n', 1)
        message = message[0].split(" ", 1)
        command = str.upper(message.pop(0))
        return (command, message)

    commands = {
        'USER': Login,
        'QUIT': Logout,
        'NOOP': NoOp
    }

    def ExecuteCommand(self, message):
        cmd, msg = self.ParseCommand(message)
        # TODO: check if there is another command in the data sent
        try:
            self.commands[cmd](self, msg)
        except KeyError:
            print 'Wrong Command Entered'
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
