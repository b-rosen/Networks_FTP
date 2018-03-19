from Tkinter import *
from PIL import Image, ImageTk

clientWindow = Tk()
clientWindow.title("FTP Client")
clientWindow.geometry('640x360')
openFImg = Image.open("./images/openfile.png")
openFTkImg = ImageTk.PhotoImage(openFImg)
openFileButton = Button(clientWindow,image=openFTkImg,height=20,width=20)
downloadButton = Button(clientWindow,image="")
connectButton = Button(clientWindow,image="")
openFileButton.grid(column=1,row=1)
downloadButton.grid(column=2,row=1)
connectButton.grid(column=3,row=1)
clientWindow.mainloop()