from tkinter import *

root = Tk()

# label widget
myLabel1 = Label(root, text="dupa kurwa chuj")
myLabel2 = Label(root, text="cycki dupa chuj")
myLabel3 = Label(root, text="gowno dupa chuj")

myLabel1.grid(row=0, column=0)
myLabel2.grid(row=1, column=5)
myLabel3.grid(row=1, column=1)
root.mainloop()