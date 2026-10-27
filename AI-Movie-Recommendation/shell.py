import streamlit as st
with open('test_exec.py') as f: exec(f.read(), globals())
