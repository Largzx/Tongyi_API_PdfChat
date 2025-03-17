import streamlit as st
from langchain.memory import ConversationBufferMemory
from utils import pdf_agent2

st.title("🧾PDF阅读助手，问答工具")
'''
设置侧边栏功能
1)模型API密钥输入
2)语言模型选择
'''
with st.sidebar:
    tongyi_api_key = st.text_input("请输入阿里百炼API密钥：", type="password")
    st.markdown("[获取阿里百炼API密钥](https://bailian.console.aliyun.com/?apiKey=1#/api-keyw)")
    st.markdown("---")
    model_kind = st.selectbox(
        "语言模型选择",
        ["qwen-max", "qwen-plus", "qwen-turbo"],
        index=1,
        help="从下到上，依次变强！🥇"
    )
    st.markdown(
        "[模型参考文档](https://help.aliyun.com/zh/model-studio/user-guide/text-generation/?spm=a2c4g.11186623.help-menu-2400256.d_1_0_0.553c535duUTiYc)")
    st.markdown("---")

'''当对话状态存在Memory时，不创建记忆对话实例，防止当前对话记忆被重置'''
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        output_key="answer"
    )

uploaded_file = st.file_uploader("上传你的PDF文件(文件限制10MB)", type="pdf")
question = st.chat_input("对PDF的内容进行提问", disabled=not uploaded_file)

if uploaded_file and question and not tongyi_api_key:
    st.info("请输入你的百炼API密钥")
if uploaded_file and question and tongyi_api_key:
    with st.spinner("AI助手看文档，请稍后....."):
        response = pdf_agent2(
            tongyi_api_key=tongyi_api_key,
            memory=st.session_state["memory"],
            uploade_file=uploaded_file,
            question=question,
            model=model_kind
        )
    st.write("### 回答")
    st.write(response["answer"])
    st.session_state["chat_history"] = response["chat_history"]

if "chat_history" in st.session_state:
    with st.expander("历史消息"):
        for i in range(0, len(st.session_state["chat_history"]), 2):
            human_messages = st.session_state["chat_history"][i]
            ai_messages = st.session_state["chat_history"][i + 1]
            st.write(human_messages.content)
            st.write(ai_messages.content)
            if i < len(st.session_state["chat_history"]) - 2:
                st.write("---")
