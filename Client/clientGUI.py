from Tkinter import *
import tkMessageBox
import Client_FTP

class clientGUI(Tk):
    def __init__(self,*args,**kwargs):
        Tk.__init__(self,*args,**kwargs)

        pageHolder = Frame(self)
        pageHolder.pack(side="top", fill="both", expand=True)
        pageHolder.grid_rowconfigure(0, weight=1)
        pageHolder.grid_columnconfigure(0, weight=1)

        self.title("Client FTP")
        self.geometry("640x360")
        self.configure(background="#12d168")

        self.pages = {}
        for p in (serverSelectPage,guestOrUserPage,logInPage,mainPage):
            page = p(pageHolder,self)
            self.pages[p] = page
            page.grid(row=0, column=0, sticky="NESW")

        self.display(serverSelectPage)

    def display(self, pageToDisp):
        page = self.pages[pageToDisp]
        page.tkraise()


class serverSelectPage(Frame):
    def __init__(self,parent,gui):
        Frame.__init__(self,parent)
        self.configure(background="#12d168")

        serverLabel = Label(self, text="Server Name:",font=("Times New Roman",12),background="#12d168",fg="#4d12b5")
        serverLabel.place(x=320,y=115,anchor=CENTER)

        serverName = Entry(self, width=30,fg="#4d12b5")
        serverName.place(x=320,y=135,anchor=CENTER)

        portLabel = Label(self, text="Port Number:",font=("Times New Roman",12),background="#12d168",fg="#4d12b5")
        portLabel.place(x=320,y=165,anchor=CENTER)

        portName = Entry(self, width=30,fg="#4d12b5")
        portName.place(x=320,y=185,anchor=CENTER)

        def serverInput():
            Client_FTP.s_name = serverName.get()
            Client_FTP.s_port = int(portName.get())
            result, message = Client_FTP.StartUp(Client_FTP.s_name,Client_FTP.s_port)
            if result:
                gui.display(guestOrUserPage)
                return
            tkMessageBox.showerror("Error",message)

        connectButton = Button(self, text="Connect to server",font=("Times New Roman",12),background="#12d168",fg="#4d12b5",command=serverInput)
        connectButton.place(x=320,y=225,anchor=CENTER)

class guestOrUserPage(Frame):
    def __init__(self,parent,gui):
        Frame.__init__(self,parent)
        self.configure(background="#12d168")
        selected = IntVar()

        userSelect = Radiobutton(self,text="user",font=("Times New Roman",12),background="#12d168",fg="#4d12b5",value=1,variable=selected)
        userSelect.place(x=320,y=150,anchor=CENTER)

        guestSelect = Radiobutton(self,text="guest",font=("Times New Roman",12),background="#12d168",fg="#4d12b5",value=2,variable=selected)
        guestSelect.place(x=320,y=180,anchor=CENTER)

        def getSelected():
            if selected.get() == 1:
                gui.display(logInPage)
            elif selected.get() == 2:
                gui.display(mainPage)
            else:
                tkMessageBox.showerror("Error","Nothing selected")

        continueButton = Button(self, text="Continue",background="#12d168",fg="#4d12b5",font=("Times New Roman",12),command=getSelected)
        continueButton.place(x=320,y=220,anchor=CENTER)

class logInPage(Frame):
    def __init__(self,parent,gui):
        Frame.__init__(self,parent)
        self.configure(background="#12d168")

        userLabel = Label(self, text="User Name:",background="#12d168",fg="#4d12b5",font=("Times New Roman",12))
        userLabel.place(x=320,y=80,anchor=CENTER)

        userName = Entry(self, width=30,fg="#4d12b5")
        userName.place(x=320,y=100,anchor=CENTER)

        passwordLabel = Label(self, text="Password:",background="#12d168",fg="#4d12b5",font=("Times New Roman",12))
        passwordLabel.place(x=320,y=130,anchor=CENTER)

        passwordEntry = Entry(self, width=30,fg="#4d12b5")
        passwordEntry.place(x=320,y=150,anchor=CENTER)

        accountLabel = Label(self, text="Account:",background="#12d168",fg="#4d12b5",font=("Times New Roman",12))
        accountLabel.place(x=320,y=180,anchor=CENTER)

        accountEntry = Entry(self, width=30,fg="#4d12b5")
        accountEntry.place(x=320,y=200,anchor=CENTER)

        def logIn():
            Client_FTP.username = userName.get()
            Client_FTP.password = passwordEntry.get()
            Client_FTP.account = accountEntry.get()
            result, message = Client_FTP.Login()
            if result:
                gui.display(mainPage)
                return
            tkMessageBox.showerror("Error",message)


        logInButton = Button(self, text="Log In",background="#12d168",fg="#4d12b5",font=("Times New Roman",12),command=logIn)
        logInButton.place(x=320,y=240,anchor=CENTER)

class mainPage(Frame):
    def __init__(self,parent,gui):
        Frame.__init__(self,parent)
        self.configure(background="#12d168")

        def logOutGUI():
            result, message = Client_FTP.Logout()
            if result:
                gui.display(serverSelectPage)
                return
            tkMessageBox.showerror("Error",message)

        logOutButton = Button(self,text="log out",background="#12d168",fg="#4d12b5",height=1,width=7,command=logOutGUI)
        logOutButton.place(x=610,y=20,anchor=CENTER)

        openFileButton = Button(self,text="open",background="#12d168",fg="#4d12b5",height=1,width=7)
        openFileButton.place(x=260,y=85,anchor=CENTER)

        upFileButton = Button(self,text="up",background="#12d168",fg="#4d12b5",height=1,width=7)
        upFileButton.place(x=320,y=85,anchor=CENTER)

        serverList = Listbox(self, height=10,width=30,fg="#4d12b5")
        serverList.place(x=320,y=180,anchor=CENTER)

        def listItems():
            reply, msg = Client_FTP.PassiveMode()
            if reply:
                result,msg,names,types = Client_FTP.ListFiles('')
                if result:
                    counter = 0
                    for name in names:
                        serverList.insert(END,name)
                        if types[counter] == "Directory":
                            serverList.itemconfig(counter,{'fg':'red'})
                        counter += 1
                    return
            tkMessageBox.showerror("Error",msg)

        listButton = Button(self,text="list",background="#12d168",fg="#4d12b5",height=1,width=7,command=listItems)
        listButton.place(x=196,y=111,anchor=CENTER)

        def downloadFile():
            fileName = serverList.get(serverList.curselection()[0])
            sFilePath = '/' + fileName
            cFilePath = 'Downloads/'+fileName
            reply, msg = Client_FTP.PassiveMode()
            if reply:
                Client_FTP.Download(sFilePath,cFilePath)

        downloadButton = Button(self,text="download",background="#12d168",fg="#4d12b5",height=1,width=7,command=downloadFile)
        downloadButton.place(x=380,y=85,anchor=CENTER)


app = clientGUI()
app.mainloop()
