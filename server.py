from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import datetime

HOST = input("sunucu adresi: ")
PORT = 5544
BUFFSIZE = 1024
NAME="Chat by Eren"


ADDR = (HOST,PORT)
SERVER = socket(AF_INET,SOCK_STREAM)
SERVER.bind(ADDR)
clients  = {}
addresses = {}

def accept():
    while True:
        client, clientAddress = SERVER.accept()
        client.send(bytes("seni mükemmel bir şekilde tanımlayan bir kullanıcı seçip yolla", "utf8"))
        addresses[client] = clientAddress
        Thread(target=handle, args=(client,)).start()

def handle(client):
    name = client.recv(BUFFSIZE).decode("utf8")
    client.send(bytes(f"{NAME}'e hoşgeldin {name}, sohbetten ayrılmak istediğin zaman exit yaz.",'utf8'))
    client.send(bytes(f"bu arada unutma ki eğer istenmeyebilecek bir mesaj atarsan banlanacaksın",'utf8'))
    msg = f"{name} bağlandı"
    broadcast(bytes(msg, 'utf8'))
    print(f"{addresses[client][0]}:{addresses[client][1]} ({name}) bağlandı")
    clients[client] = name
    while True:
        try:
            msg = client.recv(BUFFSIZE)
        except:
            print(f"{addresses[client][0]}:{addresses[client][1]} ({name}) bağlantısı kesildi")
            del clients[client]
            del addresses[client]
            broadcast(bytes(f"{name} bağlantısı kesildi",'utf8'))
        if msg != bytes("exit", "utf8"):
            dt=datetime.datetime.now().strftime("%H:%M")
            broadcast(msg, f"{dt}: {name}: ")
        else:
            print(f"{addresses[client][0]}:{addresses[client][1]} ({name}) ayrıldı")
            client.send(bytes("exit", "utf8"))
            client.close()
            broadcast(bytes(f"{name} ayrıldı", "utf8"))
            del clients[client]
            del addresses[client]
        
            break

def broadcast(msg,prefix = ""):
    for client in clients:
        client.send(bytes(prefix,'utf8')+msg)


if __name__ == "__main__":
    SERVER.listen(30)
    print(f"{NAME}: sunucu çalışır durumda\n")
    ACCEPT_THREAD = Thread(target=accept)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
