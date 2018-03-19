import Tkinter, tkFileDialog

clientWindow = Tk()
clientWindow.title("FTP Client")
clientWindow.geometry('640x360')
connectButton = Button(clientWindow,text="Connect")
connectButton.grid(column=2,row=2)
file = tkFileDialog.askopenfilename()
clientWindow.mainloop()