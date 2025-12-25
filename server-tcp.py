import socket
HOST = '127.0.0.1'
PORT = 8000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))

s.listen(5) # 最大连接数
print("监听中....")
try:
    while True:
        try:
            c, addr = s.accept() # 客户端连接
            print("连接地址：", addr)
            c.send("连接成功！请发送你的信息(发送close关闭程序)".encode('utf-8'))
        except Exception as e:
            print("======================")
            print("服务端意外关闭，原因如下：")
            print(e)
            exit(0)

        try:
            while True:
                msg = c.recv(1024)
                if not msg:
                    c.close()
                    continue

                msg = msg.decode('utf-8')
                print(f"收到消息: {msg}")

                if 'close' in msg.lower():
                    c.send("服务器关闭".encode('utf-8'))
                    c.close()
                    break
                else:
                    send_msg = "你发送了" + msg
                    c.send(send_msg.encode('utf-8'))
        except Exception:
            print(Exception())
            
except KeyboardInterrupt:
    print("服务端正在退出...")
finally:
    s.close()
    print("服务端关闭成功！")
    