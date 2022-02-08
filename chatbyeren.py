import socket, select, sys

def display():
    #FIXME: display() fonsiyonunda saat yok
	you="\33[33m\33[1m"+" sen: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def main():
    if len(sys.argv)<2: host = input("bağlanılacak sunucu: ")
    else: host = sys.argv[1]
    port = 5001
    msg=0
    name=input("\33[34m\33[1m kimlik oluşturuluyor:\n sizi mükemmel bir şekilde tanımlayan bir kullanıcı adı girin: \33[0m")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    # bağlanmayı deniyoruz
    try: s.connect((host, port))
    except:
        print("\33[31m\33[1m sunucuya bağlanılamadı \33[0m")
        sys.exit()
    # bağlanıldıysa
    s.send(bytes(name,'utf-8'))
    while True:
        socket_list = [sys.stdin, s]
        rList, wList, error_list = select.select(socket_list , [], [])# diğerleri bizi ilgilendirmiyor
        for sock in rList:
            if sock == s: # sunucudan gelen mesaj
                data = sock.recv(4096)
                if not data:
                    if msg=='exit\n': print('\33[31m\33[1m \rayrıldınız\n \33[0m')
                    else: print('\33[31m\33[1m \rbağlantı kesildi!\n \33[0m')
                    sys.exit()
                else:
                    sys.stdout.write(data.decode())
                    display()
            else: # bizim göndereceğimiz mesaj
                msg=sys.stdin.readline()
                s.send(bytes(msg,'utf-8'))
                display()

if __name__ == "__main__":
    main()
