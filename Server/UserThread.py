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
        self.Respond('Service_OK')
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

    '''
    110 Restart marker reply.
             In this case, the text is exact and not left to the
             particular implementation; it must read:
                  MARK yyyy = mmmm
             Where yyyy is User-process data stream marker, and mmmm
             server's equivalent marker (note the spaces between markers
             and "=").
    120 Service ready in nnn minutes.
    125 Data connection already open; transfer starting.
    150 File status okay; about to open data connection.
    200 Command okay.
         202 Command not implemented, superfluous at this site.
         211 System status, or system help reply.
         212 Directory status.
         213 File status.
         214 Help message.
             On how to use the server or the meaning of a particular
             non-standard command.  This reply is useful only to the
             human user.
         215 NAME system type.
             Where NAME is an official system name from the list in the
             Assigned Numbers document.
         220 Service ready for new user.
         221 Service closing control connection.
             Logged out if appropriate.
         225 Data connection open; no transfer in progress.
         226 Closing data connection.
             Requested file action successful (for example, file
             transfer or file abort).
         227 Entering Passive Mode (h1,h2,h3,h4,p1,p2).
         230 User logged in, proceed.
         250 Requested file action okay, completed.
         257 "PATHNAME" created.

         331 User name okay, need password.
         332 Need account for login.
        350 Requested file action pending further information.

        421 Service not available, closing control connection.
             This may be a reply to any command if the service knows it
             must shut down.
        425 Can't open data connection.
        426 Connection closed; transfer aborted.
        450 Requested file action not taken.
             File unavailable (e.g., file busy).
        451 Requested action aborted: local error in processing.
        452 Requested action not taken.
             Insufficient storage space in system.
        500 Syntax error, command unrecognized.
             This may include errors such as command line too long.
         501 Syntax error in parameters or arguments.
         502 Command not implemented.
         503 Bad sequence of commands.
         504 Command not implemented for that parameter.
         530 Not logged in.
         532 Need account for storing files.
         550 Requested action not taken.
             File unavailable (e.g., file not found, no access).
         551 Requested action aborted: page type unknown.
         552 Requested file action aborted.
             Exceeded storage allocation (for current directory or
             dataset).
         553 Requested action not taken.
             File name not allowed.
    '''
