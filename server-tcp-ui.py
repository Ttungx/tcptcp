import streamlit as st
import socket
import threading
import time
from streamlit.runtime.scriptrunner import add_script_run_ctx

# 设置页面标题
st.title("TCP 服务端 (Streamlit 版)")

# 配置信息（保持与 server-tcp.py 一致）
HOST = '127.0.0.1'
PORT = 8000

# 初始化 session_state
if 'server_thread' not in st.session_state:
    st.session_state.server_thread = None
if 'server_logs' not in st.session_state:
    st.session_state.server_logs = []
if 'stop_event' not in st.session_state:
    st.session_state.stop_event = threading.Event()
if 'client_socket' not in st.session_state:
    st.session_state.client_socket = None

def server_loop():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 允许端口重用
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((HOST, PORT))
        s.listen(5)
        st.session_state.server_logs.append("监听中....")
        s.settimeout(1.0) # 设置超时以便检查停止标志
        
        while not st.session_state.stop_event.is_set():
            try:
                c, addr = s.accept()
                st.session_state.client_socket = c
                st.session_state.server_logs.append(f"连接地址：{addr}")
                c.send("连接成功！请发送你的信息(发送close关闭程序)".encode('utf-8'))
                
                # 客户端通信循环
                while not st.session_state.stop_event.is_set():
                    try:
                        c.settimeout(1.0)
                        msg = c.recv(1024)
                        if not msg:
                            c.close()
                            st.session_state.client_socket = None
                            break

                        msg = msg.decode('utf-8')
                        st.session_state.server_logs.append(f"收到消息: {msg}")

                        if 'close' in msg.lower():
                            c.send("服务器关闭".encode('utf-8'))
                            c.close()
                            st.session_state.client_socket = None
                            break
                        else:
                            send_msg = "你发送了" + msg
                            c.send(send_msg.encode('utf-8'))
                    except socket.timeout:
                        continue
                    except Exception as e:
                        st.session_state.server_logs.append(f"客户端连接异常: {e}")
                        st.session_state.client_socket = None
                        break
            except socket.timeout:
                continue
            except Exception as e:
                if not st.session_state.stop_event.is_set():
                    st.session_state.server_logs.append(f"服务端异常: {e}")
                break
    except Exception as e:
        st.session_state.server_logs.append(f"启动失败: {e}")
    finally:
        s.close()
        st.session_state.server_logs.append("服务端关闭成功！")
        st.session_state.server_thread = None
        st.session_state.client_socket = None

def start_server():
    st.session_state.stop_event.clear()
    if st.session_state.server_thread is None:
        thread = threading.Thread(target=server_loop, daemon=True)
        add_script_run_ctx(thread) # 允许线程访问 session_state
        st.session_state.server_thread = thread
        thread.start()

def stop_server():
    st.session_state.stop_event.set()

# UI 布局
if st.session_state.server_thread is None:
    if st.button("启动服务端"):
        start_server()
        st.rerun()
else:
    st.success("服务端正在运行...")
    
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
        if st.button("刷新状态 (检查连接)"):
            st.rerun()

    if st.button("停止服务端"):
        stop_server()
        st.rerun()

if st.button("刷新日志"):
    st.rerun()

# 显示日志
st.divider()
st.subheader("聊天记录 / 运行日志")
if st.button("手动刷新界面"):
    st.rerun()

for log in reversed(st.session_state.server_logs):
    st.text(log)
