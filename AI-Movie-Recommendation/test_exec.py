import streamlit as st
st.write('Hello')
@st.cache_data
def cached_func(): return [1,2,3]
st.write(cached_func())
