import datetime
import time
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

import chat_aliases

HOST = "0.0.0.0"
PORT = 5544
BUFFSIZE = 4096
MAX_CONN=50
NAME="Chat by Eren"
blacklist = [line.strip() for line in open("blacklist.txt", 'r')]

ADDR = (HOST,PORT)
SERVER = socket(AF_INET,SOCK_STREAM)
SERVER.bind(ADDR)
clients  = {}
addresses = {}
banned_list=[]
muted_list=[]
gunahkarlar=[]

def welcomeToTurkey(client,name):
    global NAME
    welcome=(f"{NAME}'e hoşgeldin {name}",
            chat_aliases.aliases["/chatbyeren"],
            "UYARI: BU CHAT 7/24 REİS TARAFINDAN İNCELENMEKTEDİR",
            "BAŞINIZA BELA OLACAK YAZILAR YAZMAYIN. UYARILDINIZ!",
            chat_aliases.aliases["/reis"],
            "reis tarafından uyarıldın dostum")
    time.sleep(0.1)
    for line in welcome:
        client.send(bytes(line, "utf16"))
        time.sleep(0.15)

def check31(text):
    try:
        a=float(eval(text))
        return a==31.0
    except: return False

def accept():
    while True:
        client, clientAddress = SERVER.accept()
        client.send(bytes("seni *mükemmel* bir şekilde tanımlayan bir kullanıcı seçip yolla", "utf16"))
        addresses[client] = clientAddress
        Thread(target=handle, args=(client,)).start()

def handle(client):
    name = client.recv(BUFFSIZE).decode("utf16")
    rev_clients=[v for k,v in clients.items()]
    if name in banned_list:
        client.send(bytes("banlanmışsın dostum", "utf16"))
        client.close()
    if name in rev_clients:
        client.send(bytes("bu kullanıcı adı alınmış, başka bir tane dene", "utf16"))
        client.close()
    if ("31" in name) or check31(name) or any(kelime in name.lower() for kelime in blacklist):
        client.send(bytes("hay senin gireceğin kullanıcı adını .......", "utf16"))
        time.sleep(0.1)
        client.send(bytes("aklını ....... bu mu seni mükemmel tanımlıyor aq", "utf16"))
        for i in range(1,MAX_CONN):
            if f"CokKomikBirArkadas{i}" not in rev_clients:
                name = f"CokKomikBirArkadas{i}"
                break
    welcomeToTurkey(client,name)
    broadcast(bytes(f"{name} bağlandı", 'utf16'))
    print(f"{addresses[client][0]}:{addresses[client][1]} ({name}) bağlandı")
    clients[client] = name
    while True:
        try:
            msg = client.recv(BUFFSIZE)
        except:
            print(f"{addresses[client][0]}:{addresses[client][1]} ({name}) bağlantısı kesildi")
            try: del clients[client]
            except: pass
            broadcast(bytes(f"{name} bağlantısı kesildi",'utf16'))
            return None
        if msg.decode("utf16") == "exit":
            print(f"{addresses[client][0]}:{addresses[client][1]} ({name}) ayrıldı")
            del clients[client]
            broadcast(bytes(f"{name} ayrıldı",'utf16'))
            return None
        elif name in banned_list:
            del clients[client]
            client.send(bytes("banlandın dostum", "utf16"))
            client.close()
            return None
        elif name in muted_list:
            client.send(bytes("susturuldun dostum, mesajların iletilmiyor", "utf16"))
        elif msg.decode("utf16")[:6] == "/kick ":
            usertokick = msg.decode("utf16")[6:]
            if usertokick == name:
                client.send(bytes("kendi kendini kicklemek çok aptalca, kicklemiyorum", "utf16"))
            elif usertokick in [v for k,v in clients.items()]:
                try:
                    kick_client = [k for k,v in clients.items() if v == usertokick][0]
                    kick_client.send(bytes("kicklendin dostum", "utf16"))
                    kick_client.close()
                finally:
                    try: del clients[kick_client]
                    finally: broadcast(bytes(f"{usertokick} kişisi {name} tarafından kicklendi", "utf16"))
            else:
                client.send(bytes("öyle biri yok!?", "utf16"))
        elif msg.decode("utf16")[:5] == "/ban ":
            usertoban = msg.decode("utf16")[5:]
            if usertoban in banned_list:
                client.send(bytes("bu kullanıcı zaten banlanmış", "utf16"))
            elif usertoban==name:
                client.send(bytes("kendi kendini banlamak çok aptalca, banlamıyorum", "utf16"))
            elif usertoban in [v for k,v in clients.items()]:
                if usertoban == "insanolanbiri":
                    client.send(bytes("hayırdır kardeş?\nsen kimin chatinden kimi banlıyorsun?\n ", "utf16"))
                    broadcast(bytes(f"{name} kişisi günahkarlar arasına eklendi", "utf16"))
                    gunahkarlar.append(name)
                elif not name=="insanolanbiri":
                    client.send(bytes("bu kutsal işlemi sadece insanolanbiri yapabilir", "utf16"))
                    broadcast(bytes(f"{name} kişisi günahkarlar arasına eklendi", "utf16"))
                    gunahkarlar.append(name)
                else:
                    banned_list.append(usertoban)
                    ban_cilent = [k for k,v in clients.items() if v == usertoban][0]
                    ban_cilent.send(bytes("banlandın dostum", "utf16"))
                    ban_cilent.close()
                    del clients[ban_cilent]
                    broadcast(bytes(f"{usertoban} kişisi {name} tarafından banlandı", "utf16"))
            else:
                client.send(bytes("öyle biri yok!?", "utf16"))
        elif msg.decode("utf16")[:6] == "/mute ":
            usertomute = msg.decode("utf16")[6:]
            if usertomute in muted_list:
                client.send(bytes("bu kullanıcı zaten susturulmuş", "utf16"))
            elif usertomute==name:
                client.send(bytes("kendi kendini susturmak çok aptalca, susturmuyorum", "utf16"))
            elif usertomute in [v for k,v in clients.items()]:
                muted_list.append(usertomute)
                broadcast(bytes(f"{usertomute} kişisi {name} tarafından susturuldu", "utf16"))
            else:
                client.send(bytes("öyle biri yok!?", "utf16"))
        elif msg.decode("utf16")[:8] == "/unmute ":
            usertounmute = msg.decode("utf16")[8:]
            if usertounmute in muted_list:
                muted_list.remove(usertounmute)
                broadcast(bytes(f"{usertounmute} kişisi {name} tarafından un-susturuldu", "utf16"))
            else:
                client.send(bytes("öyle biri yok!?", "utf16"))
        elif msg.decode("utf16") in chat_aliases.aliases:
            real_msg=chat_aliases.aliases[msg.decode("utf16")]
            dt=datetime.datetime.now().strftime("%H:%M")
            broadcast(bytes(real_msg,'utf16'), f"{dt}: {name}: ")
        elif msg.decode("utf16") == "/help":
            real_msg=chat_aliases.help
            client.send(bytes(real_msg,'utf16'))
        elif msg.decode("utf16") == "/gunahkarlar":
            real_msg=chat_aliases.strgunahkarlar(gunahkarlar)
            client.send(bytes(real_msg,'utf16'))
        elif msg.decode("utf16") == "/users":
            ds = [clients,addresses]
            d = {}
            for k in clients.keys():
                d[k] = tuple(d[k] for d in ds)
            real_msg=chat_aliases.strkullanıcılar(d.values())
            broadcast(bytes(real_msg,'utf16'))
        elif msg.decode("utf16")[:1] == "/":
            client.send(bytes("chatbyeren: fatal: komut yok", "utf16"))
        else:
            dt=datetime.datetime.now().strftime("%H:%M")
            broadcast(msg, f"{dt}: {name}: ")

def broadcast(msg,prefix = ""):
    for client in dict(clients):
        try: client.send(bytes(prefix,'utf16')+msg)
        except: del clients[client]


if __name__ == "__main__":
    SERVER.listen(MAX_CONN)
    print(f"{NAME}: sunucu çalışır durumda\n")
    ACCEPT_THREAD = Thread(target=accept)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
