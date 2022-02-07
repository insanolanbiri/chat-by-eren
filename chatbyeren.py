import socket, select, string, sys

#Helper function (formatting)
def display() :
	you="\33[33m\33[1m"+" sen: "+"\33[0m"
	sys.stdout.write(you)
	sys.stdout.flush()

def main():

    if len(sys.argv)<2:
        host = input("bağlanılacak sunucu: ")
    else:
        host = sys.argv[1]

    port = 5001
    
    #asks for user name
    name=input("\33[34m\33[1m kimlik oluşturuluyor:\n sizi mükemmel bir şekilde tanımlayan bir kullanıcı adı girin: \33[0m")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    
    # connecting host
    try :
        s.connect((host, port))
    except :
        print("\33[31m\33[1m sunucuya bağlanılamadı \33[0m")
        sys.exit()

    #if connected
    s.send(bytes(name,'utf-8'))
    display()
    while 1:
        socket_list = [sys.stdin, s]
        
        # Get the list of sockets which are readable
        rList, wList, error_list = select.select(socket_list , [], [])
        
        for sock in rList:
            #incoming message from server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print('\33[31m\33[1m \rbağlantı kesildi!\n \33[0m')
                    sys.exit()
                else :
                    sys.stdout.write(data.decode())
                    display()
        
            #user entered a message
            else :
                msg=sys.stdin.readline()
                s.send(bytes(msg,'utf-8'))
                display()

if __name__ == "__main__":
    main()
