import socket, select,datetime

def send_to_all (sock, message):
	for socket in connected_list:
		if socket != server_socket and socket != sock:
			try: socket.send(message)
			except:
				socket.close()
				connected_list.remove(socket)

if __name__ == "__main__":
	name=""# kullanıcı adını geçici olarak burada tutuyoruz
	record={}# (ip,port):kullanici_adi eşlenikleri
	connected_list = []
	banned_list=[]
	muted_list=[]
	buffer = 4096
	port = 5001

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("0.0.0.0", port))# 0.0.0.0=tüm arayüzleri dinle
	server_socket.listen(50)# maks. bağlantı sayısı
	connected_list.append(server_socket)
	print("\33[32mChat by Eren: Sunucu çalışır durumda\33[0m")

	while True:
		rList, wList, error_list = select.select(connected_list,[],[])# soketleri filtreliyoruz
		for sock in rList:
			if sock == server_socket: # yeni bir bağlantı
				# bağlantıyı kaydediyoruz
				sockfd, addr = server_socket.accept()
				i, p = addr
				name=sockfd.recv(buffer)
				connected_list.append(sockfd)
				record[addr]=""
				if name in record.values(): # aynı kullanıcı adı
					sockfd.send(bytes("\r\33[31m\33[1m bu kullanıcı adı alınmış, başka bir kullanıcı adı ile tekrar dene\n\33[0m",'utf-8'))
					del record[addr]
					connected_list.remove(sockfd)
					sockfd.close()
				elif i in banned_list: # banlanmış ama bağlanmaya çalışıyor
					sockfd.send(bytes("\r\33[31m\33[1m banlanmışsın dostum\n\33[0m",'utf-8'))
					del record[addr]
					connected_list.remove(sockfd)
					sockfd.close()
				else: # her şey yolunda
                    # kullanıcı adını kaydediyoruz
					record[addr]=name
					print(f"{record[(i,p)].decode()} ({i}:{p}) bağlandı")
					sockfd.send(bytes("\33[32m\r\33\n[1m Chat by Eren'e hoşgeldiniz\n ==========================\n\n chatten ayrılmak istediğiniz zaman exit yazın\n not: istenmeyecek mesajlar gönderdiğiniz taktirde banlanacaksınız.\n\n\33[0m",'utf-8'))
					send_to_all(sockfd, bytes(f"\33[32m\33[1m\r {record[(i,p)].decode()} bağlandı \n\33[0m",'utf-8'))
			else: # zaten bağlı olan bir kullanıcıdan gelen mesaj
				try:
					data1 = sock.recv(buffer).decode()
					data=data1.rstrip("\n")# sondaki \n'i atıyoruz
					i,p=sock.getpeername()
					if data == "exit": # çıkış mesajı
						msg=f"\r\33[1m\33[31m {record[(i,p)].decode()} ayrıldı\33[0m\n"
						send_to_all(sock,bytes(msg,'utf-8'))
						print(f"{record[(i,p)].decode()} ({i}:{p}) ayrıldı")
						del record[(i,p)]
						if i in muted_list: muted_list.remove(i)
						connected_list.remove(sock)
						sock.close()
					elif data[:5] == "/ban ": # biri birini banlamak istiyor
						usertoban=data[5:]
						inv_record = [v for k, v in record.items()]
						if bytes(usertoban,'utf-8') not in inv_record:
							msg=f"\r\33[1m\33[31m öyle biri yok!?\33[0m\n"
							sock.send(bytes(msg,'utf-8'))
							continue
						elif usertoban==record[(i,p)].decode():
							msg=f"\r\33[1m\33[31m kendi kendini banlamak biraz saçma değil mi? banlamıyorum\33[0m\n"
							sock.send(bytes(msg,'utf-8'))
							continue
						ib,pb=[key for key, value in record.items() if value == bytes(usertoban,'utf-8')][0]
						msg=f"\r\33[1m\33[31m {usertoban} kişisi {record[(i,p)].decode()} tarafından banlandı\33[0m\n"
						send_to_all(sock,bytes(msg,'utf-8'))
						sock.send(bytes(msg,'utf-8'))
						print(f"{usertoban} ({ib}:{pb}) kişisi {record[(i,p)].decode()} ({i}:{p}) tarafından banlandı")
						del record[(ib,pb)]
						banned_list.append(ib)
					elif data[:7] == "/unban ": # biri birini unbanlamak istiyor
						iptounban=data[7:]
						if iptounban not in banned_list:
							msg=f"\r\33[1m\33[31m öyle biri yok!?\33[0m\n"
							sock.send(bytes(msg,'utf-8'))
							continue
						banned_list.remove(iptounban)
						msg=f"\r\33[1m\33[31m {iptounban} kişisi {record[(i,p)].decode()} tarafından unbanlandı\33[0m\n"
						send_to_all(sock,bytes(msg,'utf-8'))
						sock.send(bytes(msg,'utf-8'))
						print(f"{iptounban} kişisi {record[(i,p)].decode()} ({i}:{p}) tarafından unbanlandı")
					
					elif data[:6] == "/mute ": # biri birini susturmak istiyor
						usertomute=data[6:]
						inv_record = [v for k, v in record.items()]
						if bytes(usertomute,'utf-8') not in inv_record:
							msg=f"\r\33[1m\33[31m öyle biri yok!?\33[0m\n"
							sock.send(bytes(msg,'utf-8'))
							continue
						elif usertomute==record[(i,p)].decode():
							msg=f"\r\33[1m\33[31m kendi kendini susturmak biraz saçma değil mi? susturmuyorum\33[0m\n"
							sock.send(bytes(msg,'utf-8'))
							continue
						im,pm=[key for key, value in record.items() if value == bytes(usertomute,'utf-8')][0]
						msg=f"\r\33[1m\33[31m {usertomute} kişisi {record[(i,p)].decode()} tarafından susturuldu\33[0m\n"
						send_to_all(sock,bytes(msg,'utf-8'))
						sock.send(bytes(msg,'utf-8'))
						print(f"{usertomute} ({im}:{pm}) kişisi {record[(i,p)].decode()} ({i}:{p}) tarafından susturuldu")
						muted_list.append(im)
					elif data[:8] == "/unmute ": # biri birini sesini açmak istiyor
						idtounmute=data[8:]
						inv_record = [v for k, v in record.items()]
						if idtounmute not in muted_list and bytes(idtounmute,'utf-8') not in inv_record:
							msg=f"\r\33[1m\33[31m öyle biri yok!?\33[0m\n"
							sock.send(bytes(msg,'utf-8'))
							continue
						elif idtounmute in muted_list:
							muted_list.remove(idtounmute)
						else:
							inv_record_d = {v:(i,p) for ((i,p), v) in record.items()}
							muted_list.remove(inv_record_d[bytes(idtounmute,'utf-8')][0])
						msg=f"\r\33[1m\33[31m {idtounmute} kişisi {record[(i,p)].decode()} tarafından un-susturuldu\33[0m\n"
						send_to_all(sock,bytes(msg,'utf-8'))
						sock.send(bytes(msg,'utf-8'))
						print(f"{idtounmute} kişisi {record[(i,p)].decode()} ({i}:{p}) tarafından un-susturuldu")

					elif i in banned_list: # banlanmış ama hala burada
						msg=f"\r\33[1m\33[31m banlandın dostum\33[0m\n"
						sock.send(bytes(msg,'utf-8'))
						sock.send(bytes(''))
						connected_list.remove(sock)
						sock.close()
					elif i in muted_list: # susturulmuş ama konuşmaya çalışıyor
						msg=f"\r\33[1m\33[31m susturuldun dostum, mesajların iletilmiyor\33[0m\n"
						sock.send(bytes(msg,'utf-8'))
					else: # gerçek mesaj
						dt=datetime.datetime.now().strftime("%H:%M")
						msg=f"\r\33[1m\33[35m {dt}: {record[(i,p)].decode()}: \33[0m{data}\n"
						send_to_all(sock,bytes(msg,'utf-8'))
				except OSError as e: print(f"DAHİLİ HATA: {e}")
				except: # bişeyler olmuş, bağlantı kopması gibi
					(i,p)=sock.getpeername()
					send_to_all(sock, bytes(f"\r\33[31m \33[1m{record[(i,p)].decode()} bağlantısı kayboldu\33[0m\n",'utf-8'))
					print(f"HATA: {record[(i,p)].decode()} ({i}:{p}) çevrimdışı")
					del record[(i,p)]
					if i in muted_list: muted_list.remove(i)
					connected_list.remove(sock)
					sock.close()
	server_socket.close()# muhtemelen çalışmayacak ama dursun burada
