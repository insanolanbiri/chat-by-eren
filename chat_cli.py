import os, sys, rsa, hashlib, time
from typing import TextIO
import threading
from aes import aes
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

# bad code örneği için bu dosyayı kullanabilirsiniz
sys.path.append(os.path.abspath(__file__))

username = hashlib.sha256(os.urandom(32)).hexdigest()
SHOW_ESCAPE = False
RSA_KEY_SIZE = 2048  # 2048 bit
PORT = 5544
BUFFSIZE = 16384
clientSocket = None
aeskey = None




def blue(string):
    return "\033[34m\033[1m" + string + "\033[0m"


def red(string):
    return "\033[31m\033[1m" + string + "\033[0m"


def yellow(string):
    return "\033[33m\033[1m" + string + "\033[0m"


def green(string):
    return "\033[32m\033[1m" + string + "\033[0m"


def turquoise(string):
    return "\033[36m\033[1m" + string + "\033[0m"


def insertline(line):
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def find_nth(haystack, needle, n):  # https://stackoverflow.com/a/1884277
    try:
        start = haystack.find(needle)
        while start >= 0 and n > 1:
            start = haystack.find(needle, start + len(needle))
            n -= 1
        return start
    except:
        return -1


def escape(msg: str):
    global username
    if msg.startswith("\\\\?\\user\\name\\"):
        username = msg[14:]


print(
    green("çıkmak istediğin zaman `exit` yazabilir ya da EOF karakteri gönderebilirsin")
)
try:
    inp = int(
        input(
            """
{}
 {} BT4 (exclusive bilgisayarımız)
 {} localhost
 {} başka bir sunucu

{}""".format(
                turquoise("sunucu seç:"),
                turquoise("1)"),
                turquoise("2)"),
                turquoise("3)"),
                turquoise("seçtiğin sunucunun numarası: "),
            )
        )
    )
    if inp == 1:
        HOST = "BT4"
    elif inp == 2:
        HOST = "localhost"
    elif inp == 3:
        HOST = input(
            """
BT4'ü (kutsal bilgisayarımızı) kullanmadığına üzüldüm doğrusu."""
            + turquoise(
                """

her neyse, hangi sunucu: """
            )
        )
    else:
        raise ValueError
except ValueError:
    print(
        red("\n\ttek yapman gereken klavyedeki lanet olası sayıya basmak gerizekalı\n")
    )
    sys.exit(1)
except (EOFError, KeyboardInterrupt):
    print("")
    sys.exit(1)

threads = os.cpu_count()
insertline(blue("şifreleme algoritması olarak aes (rsa üzerinden) kullanılıyor"))
insertline("[rsa] " + turquoise(f"anahtar oluşturuluyor: {RSA_KEY_SIZE} bit"))
insertline(
    "[rsa] " + turquoise(f"anahtar algoritması {threads} iş parçacığı kullanıyor")
)
pubkey, privkey = rsa.newkeys(RSA_KEY_SIZE, poolsize=threads)
pub_sha256 = hashlib.sha256(str(pubkey).encode("utf-16")).hexdigest()
insertline("[rsa] " + blue("anahtar oluşturuldu"))
insertline("[rsa] " + blue("açık anahtarımızın sha256 hash'i:"))
insertline("[rsa] " + green(pub_sha256))
ADDR = (HOST, PORT)
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect(ADDR)
insertline("[rsa] " + turquoise("anahtar değiş tokuşu yapılıyor"))
s_pubkey = rsa.PublicKey.load_pkcs1(clientSocket.recv(BUFFSIZE), "DER")
clientSocket.send(pubkey.save_pkcs1("DER"))
insertline("[rsa] " + blue("sunucunun açık anahtarının sha256 hash'i:"))
insertline("[rsa] " + green(hashlib.sha256(str(s_pubkey).encode("utf-16")).hexdigest()))
insertline("[rsa] " + turquoise("aes anahtarı bekleniyor"))
aeskey = rsa.decrypt(clientSocket.recv(BUFFSIZE), privkey)
insertline("[rsa] " + blue("şifrelenmiş aes anahtarı alındı"))
sign = clientSocket.recv(BUFFSIZE)
try:
    sign_algorithm = rsa.verify(aeskey, sign, s_pubkey)
    if sign_algorithm != "SHA-1":
        raise rsa.pkcs1.VerificationError
    insertline("[rsa] " + green("[rsa] aes anahtarı sunucu tarafından imzalanmış"))
except rsa.pkcs1.VerificationError:
    insertline("[rsa] " + red("#####################################"))
    insertline("[rsa] " + red("#UYARI UYARI UYARI UYARI UYARI UYARI#"))
    insertline("[rsa] " + red("#AES ANAHTAR İMZASI GEÇERSİZ        #"))
    insertline("[rsa] " + red("#BU BİRİLERİNİN BİR İŞLER ÇEVİRDİĞİ #"))
    insertline("[rsa] " + red("#ANLAMINA GELEBİLİR                 #"))
    insertline("[rsa] " + red("#####################################"))
    insertline(red("[rsa] imza geçersiz, bağlantı kapatılıyor"))
    clientSocket.close()
    while True:
        time.sleep(1000)


def receive():
    while True:
        try:
            msg = clientSocket.recv(BUFFSIZE)
            msg = aes.decrypt(aeskey, msg).decode("utf-16")
            msg = msg.replace("\uFEFF", "")
            msg = msg.rstrip("\n")
            if msg.startswith("\\\\?"):
                if SHOW_ESCAPE:
                    insertline(msg)
                escape(msg)
                continue
            for line in msg.split("\n"):
                if line != "":
                    char = 0
                    try:
                        if line[2] == ":" and line[5] == ":":  # hh:mm: user: message
                            char = find_nth(line, ":", 3)
                            line = (
                                yellow(line[:5])
                                + ": "
                                + blue(line[7:char])
                                + ": "
                                + line[char + 2 :]
                            )
                            char+=2
                        elif line[:4] == "dm: ":  # dm: hh:mm: user: message
                            char = find_nth(line, ":", 4)
                            line = (
                                green(line[:2])
                                + ": "
                                + yellow(line[4:9])
                                + ": "
                                + blue(line[11:char])
                                + line[char:]
                            )
                    except IndexError:
                        pass
                    line=line[:char]+line[char:].replace(username,green(username))
                    replacements = {
                        "fizik": green("fizik"),
                        "Fizik": green("Fizik"),
                        "FİZİK": green("FİZİK"),
                    }
                    for word in line.split(" "):
                        if word[:1] == "/" and len(word) > 2:
                            line = line.replace(word, turquoise(word))
                    for before in replacements:
                        line=line.replace(before,replacements[before])
                    insertline(line)
        except:
            close()


def write(event=None):
    while True:
        msg = sys.stdin.readline()
        msg = msg.replace("\n", "")
        if msg:
            sys.stdout.write("\033[A\r")
            sys.stdout.flush()
        if msg == "exit":
            close()
        elif len(msg) > 500:
            insertline(red("mesajın çok uzundu, gönderemedim"))
        elif msg != "":
            try:
                clientSocket.send(aes.encrypt(aeskey, bytes(msg, "utf16")))
            except:
                close()


def close(event=None):
    try:
        clientSocket.send(aes.encrypt(aeskey, bytes("exit", "utf16")))
    except:
        sys.stdout.write(red("bir şey oldu\n"))
    else:
        sys.stdout.write(red("ayrıldın\n"))
    finally:
        sys.stdout.flush()
        os._exit(0)


if __name__ == "__main__":
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
    write_thread = threading.Thread(target=write)
    write_thread.start()
