import os
import json
import firebase_admin
from firebase_admin import credentials, db
import numpy as np
import google.generativeai as genai
from scipy.spatial.distance import cosine

# 初始化 Firebase Admin SDK
firebase_url = os.getenv('FIREBASE_URL')
credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
cred = credentials.Certificate(credentials_path)
firebase_admin.initialize_app(cred, {'databaseURL': firebase_url})

# 初始化 Google Gemini
gemini_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_key)

def generate_embedding(text):
    paragraphs = text.split('\n\n')  # 假设段落之间用两个换行符分隔

    embeddings = []
    for paragraph in paragraphs:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=paragraph,
            task_type="retrieval_document",
            title="Embedding of paragraph"
        )
        embedding = result['embedding']
        embeddings.append(embedding)

    combined_embedding = np.mean(embeddings, axis=0)
    return combined_embedding

def query_embedding(question, top_k=1):
    # 生成问句的嵌入
    question_embedding = generate_embedding(question)
    
    # 从数据库中获取所有存储的嵌入
    ref = db.reference('blog_embeddings')
    all_embeddings = ref.get()
    
    if not all_embeddings:
        return "No embeddings found in the database."
    
    # 计算问句嵌入与存储嵌入之间的相似度
    similarities = []
    for file_id, embedding_data in all_embeddings.items():
        stored_embedding = np.array(embedding_data['vector'])
        similarity = 1 - cosine(question_embedding, stored_embedding)
        similarities.append((file_id, similarity))
    
    # 按相似度排序并返回最相关的结果
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_results = similarities[:top_k]
    
    results = []
    for file_id, similarity in top_results:
        file_content = ref.child(file_id).get()
        results.append({
            'file_id': file_id,
            'similarity': similarity,
            'content': file_content
        })
    
    return results

def query_and_generate_response(question, top_k=1):
    # 查询嵌入以获取最相关的结果
    query_results = query_embedding(question, top_k=top_k)
    
    if not query_results:
        return "No relevant documents found."
    
    # 返回最相关的原始内容
    return query_results

def generate_gemini_text_complete(prompt):
    """
    Generate a text completion using the generative model.
    """
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response

# 示例调用
if __name__ == "__main__":    
    # 示例查询和生成响应
    question = "我哪一天架設 oracle8i 的?"
    response = query_and_generate_response(question, top_k=1)
    for res in response:
        print(f"File ID: {res['file_id']}, Similarity: {res['similarity']}")
        # print(f"Content: {res['content']}")
        content_str = res['content']
        # print(f'content_str: {content_str}')
        prompt = f"""
        use the following CONTEXT to answer the QUESTION at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.

        CONTEXT: {content_str}
        QUESTION: {question}

        reply in zh_tw
        """

        # print(f'prompt: {prompt}')
        completion = generate_gemini_text_complete(prompt)
        print(completion.text)

    






    