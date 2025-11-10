import socket

MESSAGE_DELIMITER = b"*"

s = socket.socket()
s.connect(("127.0.0.1", 9000))

buf = b""
while True:
    data = s.recv(1024)
    if not data:
        break
    buf += data
    while MESSAGE_DELIMITER in buf:
        msg, buf = buf.split(MESSAGE_DELIMITER, 1)
        print(msg.decode())
