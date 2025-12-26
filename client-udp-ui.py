import streamlit as st
import socket
import time

st.title("UDP 客户端")

HOST = '111.228.4.63'
PORT = 2001

# 初始化 session_state
if 'socket' not in st.session_state:
    st.session_state.socket = None
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'connected' not in st.session_state:
    st.session_state.connected = False

def connect_to_server():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setblocking(False) # 非阻塞
        st.session_state.socket = s
        st.session_state.connected = True
        
        # 发送握手包 (打洞/FRP需要)
        try:
            s.sendto("客户端上线".encode('utf-8'), (HOST, PORT))
            st.session_state.logs.append("已发送握手包")
        except BlockingIOError:
            pass
        except Exception as e:
            st.error(f"握手失败: {e}")

    except Exception as e:
        st.error(f"启动失败: {e}")
        st.session_state.connected = False

def disconnect_server():
    if st.session_state.socket:
        try:
            st.session_state.socket.close()
        except:
            pass
    st.session_state.socket = None
    st.session_state.connected = False
    st.session_state.logs.append("已断开连接")

# 接收消息逻辑 (轮询)
if st.session_state.connected and st.session_state.socket:
    try:
        while True:
            try:
                data, addr = st.session_state.socket.recvfrom(1024)
                msg = data.decode('utf-8')
                st.session_state.logs.append(f"收到消息: {msg}")
            except BlockingIOError:
                break # 没有数据了
    except Exception as e:
        st.session_state.logs.append(f"接收异常: {e}")

# UI 布局
if not st.session_state.connected:
    if st.button("启动客户端"):
        connect_to_server()
        st.rerun()
else:
    st.success(f"UDP 客户端运行中 (目标: {HOST}:{PORT})")
    
    with st.form("send_form", clear_on_submit=True):
        msg_input = st.text_input("输入消息")
        if st.form_submit_button("发送"):
            if msg_input:
                try:
                    st.session_state.socket.sendto(msg_input.encode('utf-8'), (HOST, PORT))
                    st.session_state.logs.append(f"你: {msg_input}")
                    st.rerun()
                except Exception as e:
                    st.error(f"发送失败: {e}")

    if st.button("断开连接"):
        disconnect_server()
        st.rerun()

# 自动刷新控制
auto_refresh = st.checkbox("自动刷新消息 (每秒)", value=True)

# 显示日志
st.divider()
st.subheader("聊天记录")
if st.button("手动刷新"):
    st.rerun()

for log in reversed(st.session_state.logs):
    st.text(log)

if auto_refresh and st.session_state.connected:
    time.sleep(1)
    st.rerun()
