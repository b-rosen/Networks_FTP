import threading

class UserThread (threading.Thread):
    msg = str()

    def __init__(self, threadName, threadID, conn_socket, address):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadName
        self.conn_socket = conn_socket
        self.address = address
    # def __init__(self):
    #     self.name = "hello"
    def run(self):
        print self.name + " is ready to use"
        while self.msg != 'exit':
            self.msg = self.conn_socket.recv(2048)
            # print 'The message (from ' + str(address) + ') is: ' + self.msg
            # self.conn_socket.send(self.msg)
            ExecuteCommand(self, self.msg)
        self.conn_socket.close()
        print ('\n' + self.name +  ' has been closed')
    def UserName(args):
        # Sends back ok message, waits for password
        print args
    def Password(args):
        num = int(args[0]) * int(args[1])
        print num

    commandList = {
        "USER": test1,
        "PASS": test2
    }

def ExecuteCommand(userThread, msg):
    # TODO: parse cmd (strip out key stuff)
    msg = msg.split(" ", 1)
    cmd = msg.pop(0)
    userThread.commandList[cmd](msg)
