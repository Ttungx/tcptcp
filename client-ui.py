import streamlit as st
import socket
import threading
import time
from streamlit.runtime.scriptrunner import add_script_run_ctx

# 设置页面标题
st.title("TCP 客户端 (Streamlit 版)")

# 配置连接信息（统一使用 127.0.0.1:8000 以便本地测试）
HOST = '127.0.0.1'
PORT = 8000

# 初始化 session_state
if 'socket' not in st.session_state:
    st.session_state.socket = None
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'receive_thread' not in st.session_state:
    st.session_state.receive_thread = None
if 'connected' not in st.session_state:
    st.session_state.connected = False

def receive_loop(s):
    while True:
        try:
            s.settimeout(1.0)
            try:
                msg = s.recv(1024)
                if not msg:
                    break
                msg = msg.decode('utf-8')
                st.session_state.logs.append(f"收到消息：{msg}")
                
                if '关闭' in msg or '服务器关闭' in msg:
                    st.session_state.logs.append("服务端关闭成功，客户端即将退出")
                    s.close()
                    st.session_state.socket = None
                    st.session_state.connected = False
                    break
            except socket.timeout:
                if not st.session_state.connected: # Check if closed manually
                    break
                continue
        except Exception as e:
            st.session_state.logs.append(f"接收出错: {e}")
            st.session_state.connected = False
            break

def connect_to_server():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        st.session_state.socket = s
        st.session_state.connected = True
        
        # 启动接收线程
        thread = threading.Thread(target=receive_loop, args=(s,), daemon=True)
        add_script_run_ctx(thread)
        st.session_state.receive_thread = thread
        thread.start()
        
        # 接收欢迎消息 (注意：如果服务端发送欢迎消息很快，可能已经被线程接收了，这里需要小心)
        # 由于线程已经启动，我们不再这里接收欢迎消息，而是让线程去接收
        # 或者，我们先接收欢迎消息，再启动线程。
        # 之前的代码是先接收欢迎消息。
        # 为了避免竞争，我们改为：先接收欢迎消息，再启动线程。
        
        # 但是，如果服务端发送欢迎消息是在 accept 之后立即发送，
        # 这里的 connect 成功后，服务端就已经发送了。
        # 我们可以在这里 recv。
        
        # 修正逻辑：先不启动线程，先尝试接收欢迎消息（带超时）
        s.settimeout(2.0)
        try:
            welcome = s.recv(1024).decode('utf-8')
            st.session_state.logs.append(f"服务端: {welcome}")
        except socket.timeout:
            pass # 没收到欢迎消息也不影响连接
        
        # 恢复超时设置并启动线程
        s.settimeout(1.0)
        thread = threading.Thread(target=receive_loop, args=(s,), daemon=True)
        add_script_run_ctx(thread)
        st.session_state.receive_thread = thread
        thread.start()

        st.success("连接成功！")
        time.sleep(0.5) # 等待一下让状态同步
        st.rerun() 
    except Exception as e:
        st.error(f"连接失败，原因如下：{e}")
        st.session_state.connected = False

def send_message():
    msg = st.session_state.input_text
    if msg and st.session_state.socket:
        try:
            st.session_state.socket.send(msg.encode('utf-8'))
            st.session_state.logs.append(f"你: {msg}")
        except Exception as e:
            st.session_state.logs.append(f"发送失败: {e}")
            st.session_state.socket.close()
            st.session_state.socket = None
            st.session_state.connected = False
        
        # 清空输入框
        st.session_state.input_text = ""

# UI 布局
if not st.session_state.connected:
    if st.button("连接服务器"):
        connect_to_server()
else:
    st.text_input("键入你想发送的信息：", key="input_text", on_change=send_message)
    if st.button("发送"):
        send_message()
    
    if st.button("断开连接"):
        if st.session_state.socket:
            st.session_state.socket.close()
        st.session_state.socket = None
        st.session_state.connected = False
        st.rerun()

# 显示日志
st.divider()
st.subheader("聊天记录")
if st.button("刷新消息"):
    st.rerun()

for log in reversed(st.session_state.logs):
    st.text(log)
