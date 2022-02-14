from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from tkinter.constants import DISABLED, END, FALSE


PORT = 5544
BUFFSIZE = 1024
NAME="Chat by Eren"

def receive():
    stop = False
    while True and not stop:
        try:
            msg = clientSocket.recv(BUFFSIZE).decode('utf8')
            msgList.insert(tkinter.END,msg)
            msgList.yview(END)
        except OSError:
            close()
            break

def send(event=None):
    msg = myMsg.get()
    myMsg.set("")
    if msg == "exit":
        clientSocket.close()
        top.quit()
    else:
        try: clientSocket.send(bytes(msg,'utf8'))
        except: pass

def close(event=None):
    try:
        myMsg.set("exit")
        send()
        top.destroy()
    finally: exit(0)

if __name__ == '__main__':
    top = tkinter.Tk()
    top.configure(bg="lightgray")
    top.title(NAME)
    top.geometry("550x650")
    top.resizable(width=FALSE, height=FALSE)
    messageFrame = tkinter.Frame(top)
    scrollbar = tkinter.Scrollbar(messageFrame)

    msgList = tkinter.Listbox(top,bd=0, bg="white", height="8", width="55", font="Arial",)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y,)
    msgList['yscrollcommand'] = scrollbar.set
    msgList.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msgList.pack(fill = tkinter.X)
    msgList.configure(bg="lightblue")
    messageFrame.pack()

    myMsg = tkinter.StringVar()
    myMsg.set("")

    entryField = tkinter.Entry(top,textvariable = myMsg, width=1, bg="white")
    entryField.bind("<Return>", send)
    entryField.pack()
    sendButton= tkinter.Button(top,font=30, text="yolla", width=8, height=4,bd=0, bg="#FFBF00", activebackground="#FACC2E", command=send)
    # sendButton= tkinter.Button(top,font=30, text="Send", width="12", height=5,  bd=0, bg="#FFBF00", activebackground="#FACC2E", command=send)
    
    
    scrollbar.place(x=540,y=6,height=545)
    entryField.place(x=118, y=555, height=90, width=425)
    sendButton.place(x=6, y=555, height=90)
    msgList.place(x=6,y=6, height=545, width=540)

    top.protocol("WM_DELETE_WINDOW", close)
    HOST=""
    while not HOST:
        try:
            inp=int(input("sunucu seç:\n 1) BT4 (exclusive bilgisayarımız)\n 2) başka bir sunucu\n\nseçtiğin sunucunun numarası: "))
            if inp==1: HOST="BT4"
            elif inp==2: HOST=input("\n\nBT4'ü (kutsal bilgisayarımızı) kullanmadığına üzüldüm doğrusu.\n\nher neyse, hangi sunucu: ")
            else: raise ValueError
        except ValueError:
            print("\n\n\ttek yapman gereken klavyedeki lanet olası sayıya basmak gerizekalı\n")
            exit(code=1)

    ADDR = (HOST, PORT)
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(ADDR)

    receiveThread = Thread(target=receive)
    receiveThread.start()
    tkinter.mainloop()  
    receiveThread.join()
