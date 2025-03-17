from langchain_openai import ChatOpenAI
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
import os

'''
DeepSeek版本
1）提供deepseekAPI密钥
2）文本编码模型使用通义的“text-embedding-v3”模型
3）需使用两个密钥
'''
# def pdf_agent(openai_api_key, memory, uploade_file, question):
#     model = ChatOpenAI(model="deepseek-chat",
#                        base_url="https://api.deepseek.com",
#                        openai_api_key=openai_api_key)
#
#     file_content = uploade_file.read()
#     temp_file_path = 'temp.pdf'
#     with open(temp_file_path, 'wb') as temp_file:
#         temp_file.write(file_content)
#
#     loader = PyPDFLoader(temp_file_path)
#     docs = loader.load()
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=50,
#         separators=["\n\n", "\n", "。", "！", "？", "，", "、", ""],
#     )
#     texts = text_splitter.split_documents(docs)
#
#     embedding_model = DashScopeEmbeddings(model="text-embedding-v3",
#                                           dashscope_api_key=os.getenv("DASHSCOPE_API_KEY"))
#
#     db = FAISS.from_documents(texts, embedding_model)
#     retriever = db.as_retriever()
#     qa = ConversationalRetrievalChain.from_llm(
#         llm=model,
#         retriever=retriever,
#         memory=memory
#     )
#     response = qa.invoke({"chat_history": memory,
#                           "question": question})
#     return response


"""
引入ChatTongyi，文本编码和语言模型通义使用阿里云百炼，API只需一个
1)通义版本
2）RAG检索增强步骤
    1> 加载文件到加载器，并返回文件加载内容（Document类）
    2> 对文件进行分割
    3> 对分割后的文本片段进行文本嵌入
    4> 将嵌入完成的文本向量存入本地向量数据库
"""


def pdf_agent2(tongyi_api_key, memory, uploade_file, question, model):
    # 创建通义对话模型
    model = ChatTongyi(model=model,
                       dashscope_api_key=tongyi_api_key)

    # 读取文件为二进制，保存文件到本地，使用PDFloader加载文件
    file_content = uploade_file.read()
    temp_file_path = 'temp.pdf'
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(file_content)
    loader = PyPDFLoader(temp_file_path)
    docs = loader.load()

    # 创建文件检索分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "，", "、", ""],
    )
    texts = text_splitter.split_documents(docs)

    # 创建文本嵌入模型
    embedding_model = DashScopeEmbeddings(model="text-embedding-v3",
                                          dashscope_api_key=tongyi_api_key)

    # 将对应文本进行编码并创建数据库
    db = FAISS.from_documents(texts, embedding_model)
    # 加载数据库检索器
    retriever = db.as_retriever()

    # 使用Langchain实例化检索对话链
    qa = ConversationalRetrievalChain.from_llm(
        llm=model,
        retriever=retriever,
        memory=memory
    )

    response = qa.invoke({"chat_history": memory,
                          "question": question})
    return response
