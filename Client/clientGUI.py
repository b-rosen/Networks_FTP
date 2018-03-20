from Tkinter import *

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
        for p in (serverSelectPage,logInPage,mainPage):
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
                       
        serverLabel = Label(self, text="Server Name:",font=("Times New Roman",12),background="#12d168")
        serverLabel.place(x=320,y=150,anchor=CENTER)
        
        serverName = Entry(self, width=30)
        serverName.place(x=320,y=170,anchor=CENTER)
        
        connectButton = Button(self, text="connect to server",font=("Times New Roman",12),background="#12d168",command=lambda: gui.display(logInPage))
        connectButton.place(x=320,y=210,anchor=CENTER)
        
class logInPage(Frame):
    def __init__(self,parent,gui):
        Frame.__init__(self,parent)
        self.configure(background="#12d168")
        
        userLabel = Label(self, text="User Name:",background="#12d168",font=("Times New Roman",12))
        userLabel.place(x=320,y=115,anchor=CENTER)
        
        userName = Entry(self, width=30)
        userName.place(x=320,y=135,anchor=CENTER)
        
        passwordLabel = Label(self, text="Password:",background="#12d168",font=("Times New Roman",12))
        passwordLabel.place(x=320,y=165,anchor=CENTER)
        
        password = Entry(self, width=30)
        password.place(x=320,y=185,anchor=CENTER)
        
        logInButton = Button(self, text="Log In",background="#12d168",font=("Times New Roman",12),command=lambda: gui.display(mainPage))
        logInButton.place(x=320,y=225,anchor=CENTER)
        
class mainPage(Frame):
    def __init__(self,parent,gui):
        Frame.__init__(self,parent)
        self.configure(background="#12d168")
        
        openFileButton = Button(self,text="open",background="#12d168",height=1,width=7)
        openFileButton.place(x=260,y=85,anchor=CENTER)
        
        upFileButton = Button(self,text="up",background="#12d168",height=1,width=7)
        upFileButton.place(x=320,y=85,anchor=CENTER)
        
        downloadButton = Button(self,text="download",background="#12d168",height=1,width=7)
        downloadButton.place(x=380,y=85,anchor=CENTER)
        
        serverList = Listbox(self, height=10,width=30)
        serverList.place(x=320,y=180,anchor=CENTER)
        
        
app = clientGUI()
app.mainloop()
        
        
            