import socket, select,datetime

#Function to send message to all connected clients
def send_to_all (sock, message):
	#Message not forwarded to server and sender itself
	for socket in connected_list:
		if socket != server_socket and socket != sock :
			try :
				socket.send(message)
			except :
				# if connection not available
				socket.close()
				connected_list.remove(socket)

if __name__ == "__main__":
	name=""
	#dictionary to store address corresponding to username
	record={}
	# List to keep track of socket descriptors
	connected_list = []
	buffer = 4096
	port = 5001

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	server_socket.bind(("localhost", port))
	server_socket.listen(20) #listen atmost 10 connection at one time

	# Add server socket to the list of readable connections
	connected_list.append(server_socket)

	print("\33[32m \t\t\t\tChat by Eren: Sunucu çalışır durumda\33[0m")

	while 1:
        # Get the list sockets which are ready to be read through select
		rList,wList,error_sockets = select.select(connected_list,[],[])

		for sock in rList:
			#New connection
			if sock == server_socket:
				# Handle the case in which there is a new connection recieved through server_socket
				sockfd, addr = server_socket.accept()
				name=sockfd.recv(buffer)
				connected_list.append(sockfd)
				record[addr]=""
				#print "record and conn list ",record,connected_list
                
                #if repeated username
				if name in record.values():
					sockfd.send(bytes("\r\33[31m\33[1m bu kullanıcı adı alınmış\n\33[0m",'utf-8'))
					del record[addr]
					connected_list.remove(sockfd)
					sockfd.close()
					continue
				else:
                    #add name and address
					record[addr]=name
					print("%s, %s bağlandı" % addr," [",record[addr].decode(),"]")
					sockfd.send(bytes("\33[32m\r\33[1m Chat by Eren'e hoşgeldiniz\n ==========================\n\n chatten ayrılmak istediğiniz zaman exit yazın\n not: istenmeyecek mesajlar gönderildiği taktirde banlanacaksınız.\n\n\33[0m",'utf-8'))
					send_to_all(sockfd, bytes("\33[32m\33[1m\r "+name.decode()+" bağlandı \n\33[0m",'utf-8'))
					continue

			#Some incoming message from a client
			else:
				# Data from client
				try:
					data1 = sock.recv(buffer).decode()
					data=data1.rstrip("\n")
                    
                    #get addr of client sending the message
					i,p=sock.getpeername()
					if data == "exit":
						msg="\r\33[1m"+"\33[31m "+record[(i,p)].decode()+" ayrıldı\33[0m\n"
						send_to_all(sock,bytes(msg,'utf-8'))
						print("%s, %s çevrimdışı" % (i,p)," [",record[(i,p)].decode(),"]")
						del record[(i,p)]
						connected_list.remove(sock)
						sock.close()
						continue

					else:
						msg="\r\33[1m"+"\33[35m "+datetime.datetime.now().strftime("%H:%M: ")+record[(i,p)].decode()+": "+"\33[0m"+data+"\n"
						send_to_all(sock,bytes(msg,'utf-8'))
            
                #abrupt user exit
				except:
					(i,p)=sock.getpeername()
					send_to_all(sock, bytes("\r\33[31m \33[1m"+record[(i,p)].decode()+" bağlantısı kayboldu\33[0m\n",'utf-8'))
					print("Hata: %s, %s çevrimdışı" % (i,p)," [",record[(i,p)].decode(),"]\n")
					del record[(i,p)]
					connected_list.remove(sock)
					sock.close()
					continue

	server_socket.close()

