import socket

host = "192.168.0.1"
#port = 

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(2)
conn,addr = s.accept()

print(addr, "Conneted")
conn.send("Thank you!")
conn.close
