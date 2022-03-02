import os, sys, tkinter
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from tkinter.constants import DISABLED, END, FALSE

PORT = 5544
BUFFSIZE = 16384
NAME = "Chat by Eren"


def receive():
    while True:
        try:
            msg = clientSocket.recv(BUFFSIZE).decode("utf16")
            msg = msg.replace("\uFEFF", "")
            for line in msg.split("\n"):
                if line != "":
                    msgList.insert(tkinter.END, line)
                    msgList.yview(END)
        except:
            close()


def send(event=None):
    msg = myMsg.get()
    myMsg.set("")
    if msg == "exit":
        close()
    elif len(msg) > 500:
        msgList.insert(tkinter.END, "mesajın çok uzundu, gönderemedim")
        msgList.yview(END)
    elif msg != "":
        try:
            clientSocket.send(bytes(msg, "utf16"))
        except:
            close()


def close(event=None):
    try:
        clientSocket.send(bytes("exit", "utf16"))
    finally:
        os._exit(0)


if __name__ == "__main__":
    top = tkinter.Tk()
    top.configure(bg="lightgray")
    top.title(NAME)
    top.geometry("550x650")
    top.resizable(width=FALSE, height=FALSE)
    messageFrame = tkinter.Frame(top)
    scrollbar = tkinter.Scrollbar(messageFrame)

    msgList = tkinter.Listbox(
        top,
        bd=0,
        bg="white",
        height="8",
        width="55",
        font="TkFixedFont",
        yscrollcommand=scrollbar.set,
    )
    scrollbar.pack(
        side=tkinter.RIGHT,
        fill=tkinter.Y,
    )
    msgList["yscrollcommand"] = scrollbar.set
    msgList.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msgList.pack(fill=tkinter.X)
    msgList.configure(bg="lightblue")
    messageFrame.pack()

    myMsg = tkinter.StringVar()
    myMsg.set("")

    entryField = tkinter.Entry(
        top, textvariable=myMsg, width=1, bg="white", font="TkFixedFont"
    )
    entryField.bind("<Return>", send)
    entryField.pack()
    sendButton = tkinter.Button(
        top,
        font=30,
        text="yolla",
        width=8,
        height=4,
        bd=0,
        bg="#FFBF00",
        activebackground="#FACC2E",
        command=send,
    )

    scrollbar.place(x=540, y=6, height=545)
    entryField.place(x=118, y=555, height=90, width=425)
    sendButton.place(x=6, y=555, height=90)
    msgList.place(x=6, y=6, height=545, width=540)

    top.protocol("WM_DELETE_WINDOW", close)
    HOST = ""
    while not HOST:
        try:
            inp = int(
                input(
                    "sunucu seç:\n 1) BT4 (exclusive bilgisayarımız)\n 2) localhost\n 3) başka bir sunucu\n\nseçtiğin sunucunun numarası: "
                )
            )
            if inp == 1:
                HOST = "BT4"
            elif inp == 2:
                HOST = "localhost"
            elif inp == 3:
                HOST = input(
                    "\n\nBT4'ü (kutsal bilgisayarımızı) kullanmadığına üzüldüm doğrusu.\n\nher neyse, hangi sunucu: "
                )
            else:
                raise ValueError
        except ValueError:
            print(
                "\n\n\ttek yapman gereken klavyedeki lanet olası sayıya basmak gerizekalı\n"
            )
            sys.exit(1)

    ADDR = (HOST, PORT)
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(ADDR)

    receiveThread = Thread(target=receive)
    receiveThread.start()
    tkinter.mainloop()
    receiveThread.join()
