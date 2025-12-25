import streamlit as st
import socket

HOST = '111.228.4.63'
PORT = 2000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

st.set_page_config("")