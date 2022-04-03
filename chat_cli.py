import os, sys, rsa, hashlib, time
import threading
from aes import aes
from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

# bad code örneği için bu dosyayı kullanabilirsiniz

isFirstMsg = True
username = "kesinlikleolamayacakbirstring"


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


sys.path.append(os.path.abspath(__file__))

PORT = 5544
BUFFSIZE = 16384
NAME = "Chat by Eren"
clientSocket = None
aeskey = None


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

insertline(blue("şifreleme algoritması olarak aes (rsa üzerinden) kullanılıyor"))
insertline("[rsa] " + turquoise("anahtar oluşturuluyor: 2048 bit"))
insertline("[rsa] " + turquoise("anahtar algoritması 1 iş parçacığı kullanıyor"))
pubkey, privkey = rsa.newkeys(2048)  # 2048 bit
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
            for line in msg.split("\n"):
                if line != "":
                    char = 0
                    try:
                        if line[2] == ":" and line[5] == ":":
                            char = find_nth(line, ":", 3)
                            line = (
                                yellow(line[:5])
                                + ": "
                                + blue(line[7:char])
                                + ": "
                                + line[char + 2 :]
                            )
                        elif line[:4] == "dm: ":
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
                    message = line[char:]
                    message = message.replace(username, green(username))
                    line = line[:char] + message
                    for word in line.split(" "):
                        if word[:1] == "/":
                            line = line.replace(word, turquoise(word))
                    line = (
                        line.replace("fizik", green("fizik"))
                        .replace("Fizik", green("Fizik"))
                        .replace("FİZİK", green("FİZİK"))
                    )
                    insertline(line)
        except:
            close()


def write(event=None):
    global username, isFirstMsg
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
            if isFirstMsg:
                username = msg
                if (
                    hashlib.sha256(bytes(username, "utf16")).hexdigest()
                    == "a8cd9e8bac481f76fc0bf19bd51276e1e7e47f43880267bc3a21fad20639c5f1"
                ):  # hakan ne gerek vardı dimi buna
                    username = "insanolanbiri"
                isFirstMsg = False
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
