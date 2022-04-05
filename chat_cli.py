import os, sys, rsa, hashlib, socket, threading
from aes import aes

# bad code örneği için bu dosyayı kullanabilirsiniz


# çok ilginç bir şekilde windowsta bunu yapmayınca ansi kaçış karakterleri çalışmıyor
# bkz: https://stackoverflow.com/a/54955094
os.system("")

username = hashlib.sha256(os.urandom(32)).hexdigest()
SHOW_ESCAPE = False
RSA_KEY_SIZE = 2048  # 2048 bit
PORT = 5544
BUFFSIZE = 16384
s = None
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


def writeline(line, color=str, head=""):
    FILE = sys.stdout
    line = color(line)
    if head:
        line = f"[{head}] {line}"
    FILE.write(line + "\n")
    FILE.flush()


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


def receive():
    while True:
        try:
            msg = s.recv(BUFFSIZE)
            msg = aes.decrypt(aeskey, msg).decode("utf-16")
            msg = msg.replace("\uFEFF", "")
            msg = msg.rstrip("\n")
            if msg.startswith("\\\\?"):
                if SHOW_ESCAPE:
                    writeline(msg)
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
                            char += 2
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
                    line = line[:char] + line[char:].replace(username, green(username))
                    replacements = {
                        "fizik": green("fizik"),
                        "Fizik": green("Fizik"),
                        "FİZİK": green("FİZİK"),
                    }
                    for word in line.split(" "):
                        if word[:1] == "/" and len(word) > 2:
                            line = line.replace(word, turquoise(word))
                    for before in replacements:
                        line = line.replace(before, replacements[before])
                    writeline(line)
        except socket.error as e:
            writeline(f"bağlantı kesildi: {e}", red)
            close(e)


def write(event=None):
    while True:
        msg = sys.stdin.readline()
        msg = msg.replace("\n", "")
        if msg:
            sys.stdout.write("\033[A\r")
            sys.stdout.flush()
        if msg == "exit":
            try:
                s.send(aes.encrypt(aeskey, bytes("exit", "utf16")))
                close()
            except socket.error as e:
                writeline(f"bağlantı kesildi: {e}", red)
                close(e)
        elif len(msg) > 500:
            writeline("mesajın çok uzundu, gönderemedim", red)
        elif msg:
            try:
                s.send(aes.encrypt(aeskey, bytes(msg, "utf16")))
            except socket.error as e:
                writeline(f"bağlantı kesildi: {e}", red)
                close(e)


def close(e=None):
    writeline(red(f"chat kapatılıyor"))
    os._exit(1 if e else 0)


writeline("çıkmak istediğin zaman `exit` yazabilir ya da EOF karakteri gönderebilirsin", green)
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
        writeline("\n\nBT4'ü (kutsal bilgisayarımızı) kullanmadığına üzüldüm doğrusu.",blue)
        HOST = input(turquoise("\n\nher neyse, hangi sunucu: "))
    else:
        raise ValueError
except ValueError:
    writeline("\ntek yapman gereken klavyedeki lanet olası sayıya basmak gerizekalı\n", red)
    sys.exit(1)
except (EOFError, KeyboardInterrupt) as e:
    close(e)

threads = os.cpu_count()

writeline("şifreleme algoritması olarak aes (rsa üzerinden) kullanılıyor", blue)
writeline(f"anahtar oluşturuluyor: {RSA_KEY_SIZE} bit", turquoise, "rsa")
writeline(f"anahtar algoritması {threads} iş parçacığı kullanıyor", turquoise, "rsa")

pubkey, privkey = rsa.newkeys(RSA_KEY_SIZE, poolsize=threads)
pub_sha256 = hashlib.sha256(str(pubkey).encode("utf-16")).hexdigest()

writeline("anahtar oluşturuldu")
writeline("açık anahtarımızın sha256 hash'i:", turquoise, "rsa")
writeline(pub_sha256, green, "rsa")

ADDR = (HOST, PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.connect(ADDR)
except socket.error as e:
    writeline(red(f"bağlantı kurulamadı: {e}"))
    close(e)

writeline("anahtar değiş tokuşu yapılıyor", head="rsa")

s_pubkey = rsa.PublicKey.load_pkcs1(s.recv(BUFFSIZE), "DER")
s.send(pubkey.save_pkcs1("DER"))

writeline("sunucunun açık anahtarının sha256 hash'i:", turquoise, "rsa")
writeline(hashlib.sha256(str(s_pubkey).encode("utf-16")).hexdigest(), green, "rsa")

writeline("aes anahtarı bekleniyor", head="rsa")
aeskey = rsa.decrypt(s.recv(BUFFSIZE), privkey)
writeline("şifrelenmiş aes anahtarı alındı", turquoise, "rsa")

sign = s.recv(BUFFSIZE)
try:
    sign_algorithm = rsa.verify(aeskey, sign, s_pubkey)
    if sign_algorithm != "SHA-1":
        raise rsa.pkcs1.VerificationError
    writeline("aes anahtarı sunucu tarafından imzalanmış", green, "rsa")
except rsa.pkcs1.VerificationError as e:
    writeline("AES ANAHTAR İMZASI GEÇERSİZ!", red, "rsa")
    writeline("BU BİRİLERİNİN BİR İŞLER ÇEVİRDİĞİ ANLAMINA GELEBİLİR", red, "rsa")
    writeline("imza geçersiz, bağlantı kapatılıyor", red, "rsa")
    close(e)


if __name__ == "__main__":
    receive_thread = threading.Thread(target=receive)
    write_thread = threading.Thread(target=write)
    receive_thread.start()
    write_thread.start()
