import os, sys, tkinter, rsa, hashlib, aes, time
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from tkinter.constants import DISABLED, END, FALSE

sys.path.append(os.path.abspath(__file__))

PORT = 5544
BUFFSIZE = 16384
NAME = "Chat by Eren"
clientSocket = None
aeskey = None


def receive():
    global clientSocket, aeskey
    try:
        inp = int(
            input(
                """
sunucu seç:
 1) BT4 (exclusive bilgisayarımız)
 2) localhost
 3) başka bir sunucu

seçtiğin sunucunun numarası: """
            )
        )
        if inp == 1:
            HOST = "BT4"
        elif inp == 2:
            HOST = "localhost"
        elif inp == 3:
            HOST = input(
                """
BT4'ü (kutsal bilgisayarımızı) kullanmadığına üzüldüm doğrusu.

her neyse, hangi sunucu: """
            )
        else:
            raise ValueError
    except ValueError:
        print(
            "\n\ttek yapman gereken klavyedeki lanet olası sayıya basmak gerizekalı\n"
        )
        sys.exit(1)
        
    insertline("şifreleme algoritması olarak aes (rsa üzerinden) kullanılıyor")
    insertline("[rsa] anahtar oluşturuluyor: 2048 bit")
    pubkey, privkey = rsa.newkeys(2048)  # 2048 bit
    pub_sha256 = hashlib.sha256(str(pubkey).encode("utf-16")).hexdigest()
    insertline("[rsa] anahtar oluşturuldu")
    insertline("[rsa] açık anahtarımızın sha256 hash'i:")
    insertline("[rsa] " + pub_sha256)

    ADDR = (HOST, PORT)
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect(ADDR)
    insertline("[rsa] anahtar değiş tokuşu yapılıyor")
    s_pubkey = rsa.PublicKey.load_pkcs1(clientSocket.recv(BUFFSIZE), "DER")
    clientSocket.send(pubkey.save_pkcs1("DER"))
    insertline("[rsa] sunucunun açık anahtarının sha256 hash'i:")
    insertline("[rsa] " + hashlib.sha256(str(s_pubkey).encode("utf-16")).hexdigest())
    insertline("[rsa] aes anahtarı bekleniyor")
    aeskey = rsa.decrypt(clientSocket.recv(BUFFSIZE), privkey)
    insertline("[rsa] şifrelenmiş aes anahtarı alındı")
    sign = clientSocket.recv(BUFFSIZE)
    try:
        sign_algorithm = rsa.verify(aeskey, sign, s_pubkey)
        if sign_algorithm != "SHA-1":
            raise rsa.pkcs1.VerificationError
        insertline("[rsa] aes anahtarı sunucu tarafından imzalanmış")
    except rsa.pkcs1.VerificationError:
        insertline("[rsa] #####################################")
        insertline("[rsa] #UYARI UYARI UYARI UYARI UYARI UYARI#")
        insertline("[rsa] #AES ANAHTAR İMZASI GEÇERSİZ        #")
        insertline("[rsa] #BU BİRİLERİNİN BİR İŞLER ÇEVİRDİĞİ #")
        insertline("[rsa] #ANLAMINA GELEBİLİR                 #")
        insertline("[rsa] #####################################")
        insertline("[rsa] imza geçersiz, bağlantı kapatılıyor")
        clientSocket.close()
        while True:
            pass  # time.sleep(1000)

    while True:
        try:
            msg = clientSocket.recv(BUFFSIZE)
            msg = aes.decrypt(aeskey, msg).decode("utf-16")
            msg = msg.replace("\uFEFF", "")
            for line in msg.split("\n"):
                if line != "":
                    insertline(line)
        except:
            close()


def insertline(line):
    msgList.insert(tkinter.END, line)
    msgList.yview(END)


def send(event=None):
    msg = myMsg.get()
    myMsg.set("")
    if msg == "exit":
        close()
    elif len(msg) > 500:
        insertline("mesajın çok uzundu, gönderemedim")
    elif msg != "":
        try:
            clientSocket.send(aes.encrypt(aeskey, bytes(msg, "utf16")))
        except:
            close()


def close(event=None):
    try:
        clientSocket.send(bytes("exit", "utf16"))
    finally:
        os._exit(0)


if __name__ == "__main__":
    top = tkinter.Tk()
    top.configure(bg="#6f24f1")
    top.title(NAME)
    top.geometry("550x650")
    top.resizable(width=FALSE, height=FALSE)
    messageFrame = tkinter.Frame(top)
    scrollbar = tkinter.Scrollbar(messageFrame)

    msgList = tkinter.Listbox(
        top,
        bd=0,
        bg="#36383f",
        height="8",
        width="55",
        font="TkFixedFont",
        foreground="#ccd1d9",
        highlightbackground="#36383f",
        yscrollcommand=scrollbar.set,
    )
    scrollbar.pack(
        side=tkinter.RIGHT,
        fill=tkinter.Y,
    )
    msgList["yscrollcommand"] = scrollbar.set
    msgList.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msgList.pack(fill=tkinter.X)
    messageFrame.pack()

    myMsg = tkinter.StringVar()
    myMsg.set("")

    entryField = tkinter.Entry(
        top,
        textvariable=myMsg,
        width=1,
        bg="#40434b",
        font="TkFixedFont",
        foreground="#ccd1d9",
        highlightbackground="#40434b",
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
        bg="#b9bbbe",
        activebackground="#dcddde",
        command=send,
    )

    scrollbar.place(x=540, y=6, height=545)
    entryField.place(x=6, y=555, height=90, width=425)
    sendButton.place(x=436, y=555, height=90)
    msgList.place(x=6, y=6, height=545, width=540)

    top.protocol("WM_DELETE_WINDOW", close)

    receiveThread = Thread(target=receive)
    receiveThread.start()
    tkinter.mainloop()
    receiveThread.join()
