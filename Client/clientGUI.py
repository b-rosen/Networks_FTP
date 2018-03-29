from Tkinter import *
import tkMessageBox
import tkFileDialog
from PIL import Image, ImageTk
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

    def getPage(self, pageName):
        return self.pages[pageName]

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

        serverName.bind('<Return>', lambda _: serverInput())
        portName.bind('<Return>', lambda _: serverInput())

        def serverInput():
            Client_FTP.s_name = serverName.get()
            Client_FTP.s_port = int(portName.get())
            result, message = Client_FTP.StartUp(Client_FTP.s_name,Client_FTP.s_port)
            if result:
                gui.display(logInPage)
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

        selected.set(1)

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

        passwordEntry = Entry(self, width=30,fg="#4d12b5",show='*')
        passwordEntry.place(x=320,y=150,anchor=CENTER)

        accountLabel = Label(self, text="Account:",background="#12d168",fg="#4d12b5",font=("Times New Roman",12))
        accountLabel.place(x=320,y=180,anchor=CENTER)

        accountEntry = Entry(self, width=30,fg="#4d12b5")
        accountEntry.place(x=320,y=200,anchor=CENTER)

        userName.bind('<Return>', lambda _: logIn())
        passwordEntry.bind('<Return>', lambda _: logIn())
        accountEntry.bind('<Return>', lambda _: logIn())

        def logIn():
            Client_FTP.username = userName.get()
            Client_FTP.password = passwordEntry.get()
            Client_FTP.account = accountEntry.get()
            result, message = Client_FTP.Login()
            if result:
                Client_FTP.GetCurrentDir()
                gui.getPage(mainPage).listItems()
                gui.display(mainPage)
                Client_FTP.CheckMode('S')
                Client_FTP.CheckType('A','N')
                Client_FTP.CheckStructure('F')
                return
            tkMessageBox.showerror("Error",message)


        logInButton = Button(self, text="Log In",background="#12d168",fg="#4d12b5",font=("Times New Roman",12),command=logIn)
        logInButton.place(x=320,y=240,anchor=CENTER)

class mainPage(Frame):
    serverList = None
    def __init__(self,parent,gui):
        Frame.__init__(self,parent)
        self.configure(background="#12d168")

        def logOutGUI():
            result, message = Client_FTP.Logout()
            if result:
                gui.display(serverSelectPage)
                return
            tkMessageBox.showerror("Error",message)

        logOutButton = Button(self,text="log out",background="#12d168",fg="#4d12b5",command=logOutGUI)
        logOutButton.place(x=590,y=30,anchor=CENTER)

        self.serverList = Listbox(self, height=10,width=30,fg="#4d12b5")
        self.serverList.place(x=320,y=180,anchor=CENTER)

        self.serverList.bind('<Double-Button-1>', self.downloadFileClick)

        listButton = Button(self,text="list",background="#12d168",fg="#4d12b5",command=self.listItems)
        listButton.place(x=320,y=80,width=150,anchor=CENTER)

        downloadImg = Image.open("images/download.png")
        downloadButImg = ImageTk.PhotoImage(downloadImg)
        downloadButton = Button(self,image=downloadButImg,background="#12d168",command=self.downloadFile)
        downloadButton.place(x=110,y=30,anchor=CENTER)
        downloadButton.image = downloadButImg
        downloadText = Label(self, text="Down",background="#12d168",fg="#4d12b5",font=("Times New Roman",9))
        downloadText.place(x=110,y=58,anchor=CENTER)

        uploadImg = Image.open("images/upload.png")
        uploadButImg = ImageTk.PhotoImage(uploadImg)
        uploadButton = Button(self,image=uploadButImg,text="Upload",background="#12d168",command=self.uploadFile)
        uploadButton.place(x=150,y=30,anchor=CENTER)
        uploadButton.image = uploadButImg
        uploadText = Label(self, text="Upload",background="#12d168",fg="#4d12b5",font=("Times New Roman",9))
        uploadText.place(x=150,y=58,anchor=CENTER)

        openFileImg = Image.open("images/openFolder.png")
        openFileButImg = ImageTk.PhotoImage(openFileImg)
        openFileButton = Button(self,image=openFileButImg,background="#12d168",command=self.openFolder)
        openFileButton.place(x=30,y=30,anchor=CENTER)
        openFileButton.image = openFileButImg
        openFileText = Label(self, text="Open",background="#12d168",fg="#4d12b5",font=("Times New Roman",9))
        openFileText.place(x=30,y=58,anchor=CENTER)

        upFileImg = Image.open("images/fileUp.png")
        upFileButImg = ImageTk.PhotoImage(upFileImg)
        upFileButton = Button(self,image=upFileButImg,background="#12d168",command =self.goUp)
        upFileButton.place(x=70,y=30,anchor=CENTER)
        upFileButton.image = upFileButImg
        upFileText = Label(self, text="Go Up",background="#12d168",fg="#4d12b5",font=("Times New Roman",9))
        upFileText.place(x=70,y=58,anchor=CENTER)

    def downloadFile(self):
        try:
            fileName = self.serverList.get(self.serverList.curselection()[0])
        except Exception:
            tkMessageBox.showerror("Error","Nothing selected")
            return
        fileTest = fileName.split(".")
        if len(fileTest) <= 1:
            tkMessageBox.showerror("Error","the selected item is not a file that can be downloaded")
            return
        sFilePath = Client_FTP.currentDirectory + fileName
        cFilePath = 'Downloads/'+fileName
        reply, msg = Client_FTP.PassiveMode()
        if reply:
            result, msg = Client_FTP.Download(sFilePath,cFilePath)
            if result:
                tkMessageBox.showinfo('FTP Client', 'File Downloaded Successfully')
                return
        tkMessageBox.showerror("Error", msg)

    def downloadFileClick(self, event):
        try:
            fileName = self.serverList.get(self.serverList.curselection()[0])
        except Exception:
            tkMessageBox.showerror("Error","Nothing selected")
            return
        fileTest = fileName.split(".")
        if len(fileTest) > 1:
            sFilePath = Client_FTP.currentDirectory + fileName
            cFilePath = 'Downloads/'+fileName
            reply, msg = Client_FTP.PassiveMode()
            if reply:
                result, msg = Client_FTP.Download(sFilePath,cFilePath)
                if result:
                    tkMessageBox.showinfo('FTP Client', 'File Downloaded Successfully' + sFilePath)
                    return
            tkMessageBox.showerror("Error", msg)
            return
        else:
            serverPath = Client_FTP.currentDirectory
            if serverPath[-1] == '/':
                serverPath = serverPath + fileName
            else:
                serverPath = serverPath + '/'
                serverPath = serverPath + fileName
            reply, msg = Client_FTP.ChangeDirectory(serverPath)
            if reply:
                self.listItems()
                tkMessageBox.showinfo('FTP Client', 'Folder changed Successfully')
                return
            tkMessageBox.showerror("Error", msg)


    def uploadFile(self):
        fileToUploadPath = tkFileDialog.askopenfilename()
        if fileToUploadPath == '':
            return
        serverPath = fileToUploadPath.split('/')
        serverPath = Client_FTP.currentDirectory + '/' + serverPath[-1]
        reply, msg = Client_FTP.PassiveMode()
        if reply:
            result, msg = Client_FTP.Upload(fileToUploadPath,serverPath)
            if result:
                self.listItems()
                tkMessageBox.showinfo('FTP Client', 'File uploaded Successfully')
                return
        tkMessageBox.showerror("Error", msg)

    def openFolder(self):
        try:
            fileName = self.serverList.get(self.serverList.curselection()[0])
        except Exception:
            tkMessageBox.showerror("Error","Nothing selected")
            return
        fileTest = fileName.split(".")
        if len(fileTest) > 1:
            tkMessageBox.showerror("Error","the selected item is not a directory")
            return
        serverPath = Client_FTP.currentDirectory
        if serverPath[len(serverPath)-1] == '/':
            serverPath = serverPath + fileName
        else:
            serverPath = serverPath + '/'
            serverPath = serverPath + fileName
        reply, msg = Client_FTP.ChangeDirectory(serverPath)
        if reply:
            self.listItems()
            tkMessageBox.showinfo('FTP Client', 'Folder changed Successfully')
            return
        tkMessageBox.showerror("Error", msg)

    def goUp(self):
        reply, msg = Client_FTP.ChangeUp()
        if reply:
            self.listItems()
            tkMessageBox.showinfo('FTP Client', 'Folder changed Successfully')
            return
        tkMessageBox.showerror("Error", msg)


    def listItems(self):
        reply, msg = Client_FTP.PassiveMode()
        if reply:
            result,msg,names,types = Client_FTP.ListFiles('')
            if result:
                self.serverList.delete(0,END)
                counter = 0
                for name in names:
                    self.serverList.insert(END,name)
                    if types[counter] == "Directory":
                        self.serverList.itemconfig(counter,{'fg':'red'})
                    counter += 1
                return
        tkMessageBox.showerror("Error",msg)


app = clientGUI()
app.mainloop()
