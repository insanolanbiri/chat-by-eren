import datetime
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

import chat_aliases

HOST = "0.0.0.0"
PORT = 5544
BUFFSIZE = 4096
MAX_CONN=50
NAME="Chat by Eren"
BOT_NAME="insanolanbot [✓BOT]"
blacklist = [line.strip() for line in open("blacklist.txt", 'r')]

ADDR = (HOST,PORT)
SERVER = socket(AF_INET,SOCK_STREAM)
SERVER.bind(ADDR)
clients  = {}
banned_list=[]
muted_list=[]
adminstatic=("insanolanbiri","insanolanbot","eren_geri_geldi","biriolaninsan")

def welcomeToTurkey(client,name):
    global NAME
    welcome=(f"{NAME}'e hoşgeldin {name}, yardım için /help yaz",
            chat_aliases.aliases["/chatbyeren"],
            "UYARI: BU CHAT 7/24 REİS TARAFINDAN İNCELENMEKTEDİR",
            "BAŞINIZA BELA OLACAK YAZILAR YAZMAYIN. UYARILDINIZ!",
            chat_aliases.aliases["/reis"],
            "reis tarafından uyarıldın dostum")
    msg="\n".join(welcome)
    send(client,msg)

def check31(text):
    try:
        a=float(eval(text))
        return a in (31.0,13.0)
    except: return False

def isAdmin(name):
    return clients[name2client(name)][2]

def name2client(name):
    return [client for client in dict(clients) if clients[client][1] == name][0]

def isUserIn(name):
    return name in [v[1] for k,v in clients.items()]

def encode(msg):
    return bytes(msg, "utf16")

def send(client,msg):
    try: client.send(encode(msg))
    except: del clients[client]

def botcast(msg,to=False):
    if to:
        send(to,f"dm: {BOT_NAME}: "+msg)
    else:
        broadcast(msg,prefix=f"{BOT_NAME}: ")

def accept():
    while True:
        client, clientAddress = SERVER.accept()
        send(client,"seni *mükemmel* tanımlayan bir kullanıcı adı seçip yolla")
        clients[client] = [None,None,False]
        clients[client][0] = clientAddress
        Thread(target=handle, args=(client,)).start()

def handle(client):
    name = client.recv(BUFFSIZE).decode("utf16")
    if name in banned_list:
        send(client,"banlanmışsın dostum")
        client.close()
    if isUserIn(name):
        send(client,"bu kullanıcı adı alınmış, başka bir tane dene")
        client.close()
    if ("31" in name) or check31(name) or any(kelime in name.lower() for kelime in blacklist):
        send(client,"hay senin gireceğin kullanıcı adını .......\naklını ....... bu mu seni mükemmel tanımlıyor aq", "utf16")
        for i in range(1,MAX_CONN):
            if not isUserIn(f"CokKomikBirArkadas{i}"):
                name = f"CokKomikBirArkadas{i}"
                break
    welcomeToTurkey(client,name)
    broadcast(f"{name} bağlandı")
    print(f"{clients[client][0][0]}:{clients[client][0][1]} ({name}) bağlandı")
    clients[client][1] = name
    if name in adminstatic:
        clients[client][2] = True
    while True:
        try:
            msg = client.recv(BUFFSIZE)
            dmsg=msg.decode("utf16")
            dt=datetime.datetime.now().strftime("%H:%M")
        except:
            print(f"{clients[client][0][0]}:{clients[client][0][1]} ({name}) bağlantısı kesildi")
            try: del clients[client]
            except: pass
            broadcast(f"{name} bağlantısı kesildi")
            return None

        if dmsg == "exit":
            print(f"{clients[client][0][0]}:{clients[client][0][1]} ({name}) ayrıldı")
            del clients[client]
            broadcast(f"{name} ayrıldı")
            return None

        elif name in banned_list:
            del clients[client]
            send("banlandın dostum")
            client.close()
            return None

        elif name in muted_list:
            botcast("susturuldun dostum, mesajların iletilmiyor",client)

        elif dmsg[:6] == "/kick ":
            usertokick = dmsg[6:]
            if not isAdmin(name):
                botcast("bu komut seni aşar canım",client)
            elif usertokick == name:
                botcast("kendi kendini kicklemek çok aptalca, kicklemiyorum",client)
            elif not isUserIn(usertokick):
                botcast("öyle biri yok!?",client)
            else:
                try:
                    kick_client = name2client(usertokick)
                    botcast("kicklendin dostum",kick_client)
                    kick_client.close()
                finally:
                    try: del clients[kick_client]
                    finally: botcast(f"{usertokick}, {name} tarafından kicklendi")

        elif dmsg[:5] == "/ban ":
            usertoban = dmsg[5:]
            if not isAdmin(name):
                botcast("bu komut seni aşar canım",client)
            elif usertoban==name:
                botcast("kendi kendini banlamak çok aptalca, banlamıyorum",client)
            elif not isUserIn(usertoban):
                botcast("öyle biri yok!?",client)
            else:
                banned_list.append(usertoban)
                ban_cilent = name2client(usertoban)
                botcast("banlandın dostum",ban_cilent)
                ban_cilent.close()
                del clients[ban_cilent]
                botcast(f"{usertoban}, {name} tarafından banlandı")
                
        elif dmsg[:6] == "/mute ":
            usertomute = dmsg[6:]
            if not isAdmin(name):
                botcast("bu komut seni aşar canım",client)
            elif usertomute in muted_list:
                botcast("bu kullanıcı zaten susturulmuş",client)
            elif usertomute==name:
                botcast("kendi kendini susturmak çok aptalca, susturmuyorum",client)
            elif not isUserIn(usertomute):
                botcast("öyle biri yok!?",client)
            else:
                muted_list.append(usertomute)
                botcast(f"{usertomute}, {name} tarafından susturuldu")
                

        elif dmsg[:8] == "/unmute ":
            usertounmute = dmsg[8:]
            if not isAdmin(name):
                botcast("bu komut seni aşar canım",client)
            elif not isUserIn(usertomute):
                botcast("öyle biri yok!?",client)
            elif usertounmute not in muted_list:
               botcast("susturulmamış ki unsusturayım!?",client)
            else:
                muted_list.remove(usertounmute)
                botcast(f"{usertounmute}, {name} tarafından un-susturuldu")
                

        elif dmsg in chat_aliases.aliases:
            broadcast(chat_aliases.aliases[dmsg], f"{dt}: {name}: ")

        elif dmsg == "/help":
            botcast(chat_aliases.help,client)

        elif dmsg == "/users":
            botcast(chat_aliases.strkullanıcılar(clients.values()),client)

        elif dmsg == "/usersbroadcast":
            botcast(chat_aliases.strkullanıcılar(clients.values()))

        elif dmsg[:1] == "/":
            botcast("komut yok",client)

        elif any(x in dmsg for x in blacklist) and not isAdmin(name):
            muted_list.append(name)
            botcast(f"{name} oto-susturuldu")
        
        else:
            broadcast(dmsg, f"{dt}: {name}: ")

def broadcast(msg,prefix = ""):
    for client in dict(clients):
        if clients[client][1]:
            try: client.send(encode(prefix+msg))
            except: del clients[client]


if __name__ == "__main__":
    SERVER.listen(MAX_CONN)
    print(f"{NAME}: sunucu çalışır durumda\n")
    ACCEPT_THREAD = Thread(target=accept)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
