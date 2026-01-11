import streamlit as st

st.title("测试页面")
st.write("如果你能看到这个，说明 Streamlit 基本功能正常")

if st.button("点击测试"):
    st.success("按钮工作正常！")

