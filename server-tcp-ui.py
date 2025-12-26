import streamlit as st
import socket
import time

# 设置页面标题
st.title("TCP 服务端")

# 配置信息
HOST = '127.0.0.1'
PORT = 8000

# 初始化 session_state
if 'server_logs' not in st.session_state:
    st.session_state.server_logs = []
if 'client_socket' not in st.session_state:
    st.session_state.client_socket = None
if 'server_socket' not in st.session_state:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        s.setblocking(False) # 非阻塞
        st.session_state.server_socket = s
        st.session_state.server_logs.append("监听中....")
    except Exception as e:
        st.error(f"启动失败: {e}")
        st.session_state.server_socket = None

# 轮询逻辑
if st.session_state.server_socket:
    # 1. 检查新连接
    if st.session_state.client_socket is None:
        try:
            c, addr = st.session_state.server_socket.accept()
            c.setblocking(False)
            st.session_state.client_socket = c
            st.session_state.server_logs.append(f"连接地址：{addr}")
            c.send("连接成功！请发送你的信息(发送close关闭程序)".encode('utf-8'))
        except BlockingIOError:
            pass
        except Exception as e:
            st.session_state.server_logs.append(f"Accept 异常: {e}")

    # 2. 检查消息接收
    if st.session_state.client_socket:
        try:
            while True:
                try:
                    data = st.session_state.client_socket.recv(1024)
                    if not data:
                        st.session_state.client_socket.close()
                        st.session_state.client_socket = None
                        st.session_state.server_logs.append("客户端断开连接")
                        break
                    
                    msg = data.decode('utf-8')
                    st.session_state.server_logs.append(f"收到消息: {msg}")

                    if 'close' in msg.lower():
                        st.session_state.client_socket.send("服务器关闭".encode('utf-8'))
                        st.session_state.client_socket.close()
                        st.session_state.client_socket = None
                        break
                    else:
                        send_msg = "你发送了" + msg
                        st.session_state.client_socket.send(send_msg.encode('utf-8'))
                except BlockingIOError:
                    break
        except Exception as e:
            st.session_state.server_logs.append(f"接收异常: {e}")
            if st.session_state.client_socket:
                st.session_state.client_socket.close()
            st.session_state.client_socket = None

# UI 布局
st.success("服务端正在运行 (轮询模式)...")

# 发送消息区域
if st.session_state.client_socket:
    st.success("客户端已连接")
    with st.form("server_send_form", clear_on_submit=True):
        server_msg = st.text_input("发送给客户端的消息")
        if st.form_submit_button("发送"):
            if server_msg:
                try:
                    st.session_state.client_socket.send(server_msg.encode('utf-8'))
                    st.session_state.server_logs.append(f"服务端发送: {server_msg}")
                    st.rerun()
                except Exception as e:
                    st.error(f"发送失败: {e}")
else:
    st.info("等待客户端连接...")

# 自动刷新控制
auto_refresh = st.checkbox("自动刷新消息", value=True)

# 显示日志
st.divider()
st.subheader("聊天记录 / 运行日志")
if st.button("手动刷新界面"):
    st.rerun()

for log in reversed(st.session_state.server_logs):
    st.text(log)

if auto_refresh:
    time.sleep(1)
    st.rerun()
