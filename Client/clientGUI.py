from Tkinter import *
from PIL import Image, ImageTk

clientWindow = Tk()
clientWindow.title("FTP Client")
clientWindow.geometry('640x360')

openFImg = Image.open("./images/openFileSmall.png")
openFTkImg = ImageTk.PhotoImage(openFImg)
openFileButton = Button(clientWindow,image=openFTkImg,height=20,width=20)

connectButton = Button(clientWindow,text="Connect to server",width=15)

serverName = Entry(clientWindow,width=30)

serverName.place(relx=0,x=260,y=15,anchor=CENTER)
openFileButton.place(x=15,y=15,anchor=CENTER)
connectButton.place(relx=0,x=415,y=15,anchor=CENTER)

serverList = Listbox(clientWindow,height=15,width=50)
serverList.place(relx=0,x=320,y=180,anchor=CENTER)

clientWindow.mainloop()