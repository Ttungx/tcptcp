import streamlit as st
import socket
import time

st.title("UDP 服务端")

HOST = '127.0.0.1'
PORT = 9000

# 初始化 session_state
if 'server_logs' not in st.session_state:
    st.session_state.server_logs = []
if 'client_addr' not in st.session_state:
    st.session_state.client_addr = None
if 'server_socket' not in st.session_state:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.setblocking(False) # 非阻塞
        st.session_state.server_socket = s
        st.session_state.server_logs.append(f"UDP 服务端启动，监听 {HOST}:{PORT}")
    except Exception as e:
        st.error(f"启动失败: {e}")
        st.session_state.server_socket = None

# 轮询逻辑
if st.session_state.server_socket:
    try:
        while True:
            try:
                data, addr = st.session_state.server_socket.recvfrom(1024)
                st.session_state.client_addr = addr # 更新最近的客户端地址
                
                msg = data.decode('utf-8')
                st.session_state.server_logs.append(f"来自 {addr} 的消息: {msg}")

                if 'close' in msg.lower():
                    st.session_state.server_socket.sendto("服务器已收到关闭指令".encode('utf-8'), addr)
                else:
                    send_msg = "你发送了" + msg
                    st.session_state.server_socket.sendto(send_msg.encode('utf-8'), addr)
            except BlockingIOError:
                break # 没有数据了
    except Exception as e:
        st.session_state.server_logs.append(f"接收异常: {e}")

# UI 布局
st.success("服务端正在运行 (轮询模式)...")

# 发送消息区域
if st.session_state.client_addr:
    st.info(f"当前目标客户端: {st.session_state.client_addr}")
    with st.form("server_send_form", clear_on_submit=True):
        server_msg = st.text_input("发送给客户端的消息")
        if st.form_submit_button("发送"):
            if server_msg and st.session_state.server_socket:
                try:
                    st.session_state.server_socket.sendto(server_msg.encode('utf-8'), st.session_state.client_addr)
                    st.session_state.server_logs.append(f"服务端发送: {server_msg}")
                    st.rerun()
                except Exception as e:
                    st.error(f"发送失败: {e}")
else:
    st.info("等待客户端消息以获取地址...")

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
