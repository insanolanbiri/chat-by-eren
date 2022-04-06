import time, hashlib, random, rsa, os
from aes import aes
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread
from datetime import datetime
from denemesonuc import *

import chat_aliases

### bad code örneği için bu dosyayı kullanabilirsiniz

# TODO: insanolanbot class
# TODO: insanolanbot komutları
# TODO: try: ...; except: pass saçmalığı
# TODO: admin yönetim
# TODO: espri format

HOST = "0.0.0.0"
PORT = 5544
RSA_KEY_SIZE = 2048  # 2048 bit
AES_KEY_SIZE = 256  # 128 bit
BUFFSIZE = 16384
MAX_CONN = 50
NAME = "Chat by Eren"
BOT_NAME = "insanolanbot [✓BOT]"
text_spam_mute = False
blacklist = [line.strip().lower() for line in open("blacklist.txt", "r")]

ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)
clist = {}
banned_list = []
muted_list = []
adminstatic = ("insanolanbiri", "insanolanbot", "eren_geri_geldi", "biriolaninsan", "")


def broadcast(msg, prefix=""):
    for c in dict(clist):
        if clist[c][1]:
            try:
                aeskey = clist[c][7]
                c.send(aes.encrypt(aeskey, bytes(prefix + msg, "utf16")))
            except:
                del clist[c]


def check31(text):
    try:
        a = float(eval(text))
        return a in (31.0, 13.0)
    except:
        return False


def isAdmin(name):
    return clist[name2c(name)][2]


def name2c(name):
    return [c for c in dict(clist) if clist[c][1] == name][0]


def isUserIn(name):
    return name in [v[1] for k, v in clist.items()] + ["insanolanbot"]


def send(c, msg):
    try:
        aeskey = clist[c][7]
        c.send(aes.encrypt(aeskey, bytes(msg, "utf16")))
    except Exception as e:
        del clist[c]
        print(e)


def botcast(msg, to=False):
    dt = datetime.now().strftime("%H:%M")
    if to:
        send(to, f"dm: {dt}: {BOT_NAME}: " + msg)
    else:
        broadcast(msg, prefix=f"{dt}: {BOT_NAME}: ")


def accept():
    while True:
        try:
            c, cAddress = SERVER.accept()
            c.send(pubkey.save_pkcs1("DER"))
            c_pubkey = rsa.PublicKey.load_pkcs1(c.recv(BUFFSIZE), "DER")
            c_pubkey_hash = hashlib.sha256(str(c_pubkey).encode("utf-16")).hexdigest()
            print(f"\n[rsa] {cAddress[0]}:{cAddress[1]}'in açık anahtarının sha256 hash'i:")
            print("[rsa] " + c_pubkey_hash)
            aes_key = os.urandom(AES_KEY_SIZE // 8)

            clist[c] = [
                cAddress,  # ip,port
                None,  # username
                False,  # is an admin
                [None, None, None],  # last 3 messages
                [datetime.min, datetime.min, datetime.min],  # dates of last 3 messages
                c_pubkey,
                c_pubkey_hash,
                aes_key,
            ]
            print(f"[rsa] {clist[c][0][0]}:{clist[c][0][1]}'e aes anahtarı gönderiliyor")
            c.send(rsa.encrypt(aes_key, c_pubkey))
            sign = rsa.sign(aes_key, privkey, "SHA-1")
            # time.sleep(0.1)
            c.send(sign)
            send(
                c,
                "\n".join(
                    [
                        chat_aliases.aliases["/chatbyeren"],
                        "seni *mükemmel* tanımlayan bir kullanıcı adı seçip yolla",
                    ]
                ),
            )
            Thread(target=handle, args=(c,)).start()
        except Exception as e:
            print(e)


def handle(c):
    name = aes.decrypt(clist[c][7], c.recv(BUFFSIZE)).decode("utf16")
    # sürekli mesaj atılırsa aes decrypt çöküyor
    # its not a bug its a feature
    if name == "insanolanbiri":
        send(
            c,
            "\n".join(
                [
                    "taam taam inandım",
                    "kesin insanolanbiri'sin sen",
                    "kimi kandırıyon sen?",
                ]
            ),
        )
        botcast("banlandın dostum", c)  # aslında banlanmadı sadece korkutuyoruz
        c.close()
        del clist[c]
        return None
    if (
        hashlib.sha256(bytes(name, "utf16")).hexdigest()
        == "a8cd9e8bac481f76fc0bf19bd51276e1e7e47f43880267bc3a21fad20639c5f1"
    ):  # hakan ne gerek vardı dimi buna
        name = "insanolanbiri"
    if name in banned_list:
        send(c, "banlanmışsın dostum")
        c.close()
        del clist[c]
        return None
    elif isUserIn(name):
        send(c, "bu kullanıcı adı alınmış, başka bir tane dene\nbağlantı sonlandırılıyor")
        c.close()
        del clist[c]
        return None
    elif ("31" in name) or check31(name):
        botcast("k. adına bakılırsa yaşın tutmuyor dostum", c)
        botcast("banlandın dostum", c)  # aslında banlanmadı sadece korkutuyoruz
        c.close()
        del clist[c]
        return None
    elif name.startswith("\\\\?"):
        send(c, "kullanici adi kacis karakteriyle baslayamaz")
        c.close()
        del clist[c]
        return None
    elif any(kelime in name.lower() for kelime in blacklist):
        send(
            c,
            "\n".join(
                [
                    "hay senin gireceğin kullanıcı adını .......",
                    "aklını ....... bu mu seni mükemmel tanımlıyor aq",
                ]
            ),
        )
        for i in range(1, MAX_CONN):
            if not isUserIn(f"CokKomikBirArkadas{i}"):
                name = f"CokKomikBirArkadas{i}"
                break
    send(c, f"\\\\?\\user\\name\\{name}")
    welcome = (
        f"{NAME}'e hoşgeldin {name}, yardım için /help yaz",
        "Chat by Eren'deki şifreleme hakkında: /şifreleme",
        "UYARI: BU CHAT 7/24 REİS TARAFINDAN İNCELENMEKTEDİR",
        "BAŞINIZA BELA OLACAK YAZILAR YAZMAYIN. UYARILDINIZ!",
        chat_aliases.aliases["/reis"],
        "reis tarafından uyarıldın dostum",
    )
    msg = "\n".join(welcome)
    send(c, msg)
    broadcast(f"{name} bağlandı")
    print(f"{clist[c][0][0]}:{clist[c][0][1]} ({name}) bağlandı\n")
    clist[c][1] = name
    if name in adminstatic:
        clist[c][2] = True
    # time.sleep(0.2)
    botcast(f"hoşgeldin {name}!")
    while True:
        try:
            msg = aes.decrypt(clist[c][7], c.recv(BUFFSIZE))
            dmsg = msg.decode("utf16")
            dt = datetime.now().strftime("%H:%M")
            (clist[c][3]).append(dmsg)
            (clist[c][3]).pop(0)
            (clist[c][4]).append(datetime.now())
            (clist[c][4]).pop(0)
        except Exception as e:
            print(f"\n{clist[c][0][0]}:{clist[c][0][1]} ({name}) bağlantısı kesildi: {e}\n")
            try:
                del clist[c]
            except:
                pass
            broadcast(f"{name} bağlantısı kesildi")
            return None

        if name in banned_list:
            send("banlandın dostum")
            c.close()
            return None

        elif dmsg == "exit":
            print(f"\n{clist[c][0][0]}:{clist[c][0][1]} ({name}) ayrıldı\n")
            del clist[c]
            broadcast(f"{name} ayrıldı")
            return None

        elif name in muted_list:
            botcast("susturuldun dostum, mesajların iletilmiyor", c)

        elif text_spam_mute and (
            clist[c][3][0] == clist[c][3][1] == clist[c][3][2] and not isAdmin(name)
        ):
            muted_list.append(name)
            botcast(f"{name} oto-susturuldu: spam")

        elif (datetime.now() - clist[c][4][0]).seconds <= 5 and not isAdmin(name):
            muted_list.append(name)
            botcast(f"{name} oto-susturuldu: spam")

        elif dmsg[:5] == "/kick":
            usertokick = dmsg[6:]
            if not isAdmin(name):
                botcast("bu komut seni aşar canım", c)
            elif usertokick == name:
                botcast("kendi kendini kicklemek çok aptalca, kicklemiyorum", c)
            elif not isUserIn(usertokick):
                botcast("öyle biri yok!?", c)
            else:
                try:
                    kick_c = name2c(usertokick)
                    botcast("kicklendin dostum", kick_c)
                    kick_c.close()
                finally:
                    try:
                        del clist[kick_c]
                    finally:
                        botcast(f"{usertokick}, {name} tarafından kicklendi")

        elif dmsg[:4] == "/ban":
            usertoban = dmsg[5:]
            if not isAdmin(name):
                botcast("bu komut seni aşar canım", c)
            elif usertoban == name:
                botcast("kendi kendini banlamak çok aptalca, banlamıyorum", c)
            elif not isUserIn(usertoban):
                botcast("öyle biri yok!?", c)
            else:
                banned_list.append(usertoban)
                ban_c = name2c(usertoban)
                botcast("banlandın dostum", ban_c)
                ban_c.close()
                del clist[ban_c]
                botcast(f"{usertoban}, {name} tarafından banlandı")

        elif dmsg[:5] == "/mute":
            usertomute = dmsg[6:]
            if not isAdmin(name):
                botcast("bu komut seni aşar canım", c)
            elif usertomute in muted_list:
                botcast("bu kullanıcı zaten susturulmuş", c)
            elif usertomute == name:
                botcast("kendi kendini susturmak çok aptalca, susturmuyorum", c)
            elif not isUserIn(usertomute):
                botcast("öyle biri yok!?", c)
            else:
                muted_list.append(usertomute)
                botcast(f"{usertomute}, {name} tarafından susturuldu")

        elif dmsg[:7] == "/unmute":
            usertounmute = dmsg[8:]
            if not isAdmin(name):
                botcast("bu komut seni aşar canım", c)
            elif not isUserIn(usertounmute):
                botcast("öyle biri yok!?", c)
            elif usertounmute not in muted_list:
                botcast("susturulmamış ki unsusturayım!?", c)
            else:
                muted_list.remove(usertounmute)
                botcast(f"{usertounmute}, {name} tarafından un-susturuldu")

        elif dmsg in chat_aliases.aliases:
            broadcast(chat_aliases.aliases[dmsg], f"{dt}: {name}: ")

        elif dmsg == "/help":
            botcast(chat_aliases.help, c)

        elif dmsg == "/users":
            botcast(chat_aliases.strkullanicilar(clist.values()), c)

        elif dmsg == "/usersbroadcast":
            botcast(chat_aliases.strkullanicilar(clist.values()))

        elif dmsg == "/şifreleme":
            botcast(chat_aliases.sifreleme, c)

        elif dmsg == "/espri":
            broadcast(dmsg, f"{dt}: {name}: ")
            # time.sleep(0.2)
            botcast(random.choice(chat_aliases.esprilist))

        elif dmsg[:7] == "/deneme":
            broadcast(dmsg, f"{dt}: {name}: ")
            # time.sleep(0.2)
            try:
                no = int(dmsg[8:])
            except:
                botcast("böyle numara olmaz olsun")
                continue
            ad = getAd(no)
            if ad == -1:
                botcast("bana doğru düzgün numara ver")
            else:
                try:
                    sonuc = getSonuc(ad, no)
                    readable_sonuc = {
                        "ad": sonuc["ad"],
                        "numara": sonuc["no"],
                        "sınıf": sonuc["9x"],
                        " ": " ",
                        "derece": " ",
                        "   sınıf": sonuc["s_drc"],
                        "   kurum": sonuc["k_drc"],
                        "   il": sonuc["i_drc"],
                        "   genel": sonuc["g_drc"],
                        "  ": " ",
                        "soru sayısı": sonuc["ss"],
                        "doğru sayısı": sonuc["ds"],
                        "yanlış sayısı": sonuc["ys"],
                        "boş sayısı": sonuc["bs"],
                        "puan": sonuc["pn"],
                        "   ": " ",
                        "fizik": " ",
                        "   doğru": sonuc["fiz_d"],
                        "   yanlış": sonuc["fiz_y"],
                        "   boş": sonuc["fiz_b"],
                        "   net": sonuc["fiz_n"],
                    }
                    t = "\nsonuçlar\n========\n"
                    for key, value in readable_sonuc.items():
                        t += f" \n{key:16}: {value}"
                    botcast(t)
                except DenemeyeGirmemisException:
                    botcast(f"{getAd(no)} denemeye girmemiş")
                except Exception as e:
                    botcast("bir şey oldu, sonucu bulamadım")
                    botcast(e, c)

        elif dmsg[:1] == "/":
            botcast("yok ki öyle bi komut", c)

        elif dmsg[:1] == "@":
            usertoping = dmsg[1:]
            if not isUserIn(usertoping):
                botcast("öyle biri yok!?")
            elif usertoping == name:
                botcast("kendi kendini pinglemek çok aptalca, pinglemiyorum", c)
            else:
                broadcast(dmsg, f"{dt}: {name}: ")
                # time.sleep(0.2)
                if usertoping == "insanolanbot":
                    botcast("noldu?")
                else:
                    botcast(f"{name} seni soruyor dostum", name2c(usertoping))

        elif (("31" in dmsg) or check31(dmsg)) and not isAdmin(name):
            muted_list.append(name)
            botcast(f"{name} oto-susturuldu: yaşı tutmuyor")

        elif any(x in dmsg.lower().split() for x in blacklist) and not isAdmin(name):
            muted_list.append(name)
            botcast(f"{name} oto-susturuldu: yasaklı kelime")

        else:
            broadcast(dmsg, f"{dt}: {name}: ")
            if any(x in chat_aliases.autoreply for x in dmsg.lower().split()):
                inp = [x for x in chat_aliases.autoreply if x in dmsg.lower().split()][0]
                # time.sleep(0.2)
                botcast(chat_aliases.autoreply[inp])


if __name__ == "__main__":
    threads = os.cpu_count()
    print(f"[rsa] anahtar oluşturuluyor: {RSA_KEY_SIZE} bit")
    print(f"[rsa] anahtar algoritması {threads} iş parçacığı kullanıyor")
    pubkey, privkey = rsa.newkeys(RSA_KEY_SIZE, poolsize=threads)
    pub_sha256 = hashlib.sha256(str(pubkey).encode("utf-16")).hexdigest()
    print("[rsa] anahtar oluşturuldu")
    print("[rsa] açık anahtarımızın sha256 hash'i:")
    print("[rsa] " + pub_sha256)
    SERVER.listen(MAX_CONN)
    print(f"\n{NAME}: sunucu çalışır durumda\n")
    ACCEPT_THREAD = Thread(target=accept)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
