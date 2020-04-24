import socket

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port

serversocket.bind(("192.168.1.136", 11234))
# become a server socket
serversocket.listen(5)

serversocket.settimeout(5)

try:
    serversocket.accept()
except socket.timeout as e:
    print(2333)
