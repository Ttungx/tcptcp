import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

HOST = '111.228.4.63'
PORT = 2000
print("正在尝试连接...")
try:
    s.connect((HOST, PORT))
except Exception as e:
    print("=================")
    print("连接失败，原因如下：")
    print(e)
    exit(0)

weclome = s.recv(1024).decode('utf-8')
print(weclome)

try:
    while True:
        msg = input("键入你想发送的信息：")
        s.send(msg.encode('utf-8'))
        print("发送成功")
        
        try:
            recive_msg = s.recv(1024).decode('utf-8')
            print("收到消息：", recive_msg)
            if '关闭' in recive_msg:
                print("服务端关闭成功，客户端即将退出")
                break
        except:
            continue
except KeyboardInterrupt:
    print("客户端正在关闭...")
finally:
    s.close()
    print("客户端关闭成功！")