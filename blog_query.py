import os
import json
import firebase_admin
from firebase_admin import credentials, db
from github import Github
import numpy as np
import google.generativeai as genai
from scipy.spatial.distance import cosine
from bs4 import BeautifulSoup

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

def store_embedding(embedding_data):
    ref = db.reference('blog_embeddings')
    ref.child(embedding_data['id']).set(embedding_data)
    print(f"Embedding data for {embedding_data['id']} stored successfully.")

def check_if_exists(file_id):
    ref = db.reference('blog_embeddings')
    return ref.child(file_id).get() is not None

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

def git_article(github_token, repo_owner, repo_name, directory_path):
    g = Github(github_token)
    repo = g.get_repo(f"{repo_owner}/{repo_name}")
    contents = repo.get_contents(directory_path)
    
    files_data = []

    limit = 0    
    while contents and limit < 30:
        limit += 1
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            file_id = file_content.name.split('.')[0]
            if check_if_exists(file_id):
                print(f"File {file_id} already exists in the database. Skipping.")
                continue
            
            file_content_decoded = file_content.decoded_content.decode('utf-8')
            cleaned_content = remove_html_tags(file_content_decoded)
            embedding = generate_embedding(cleaned_content)
            
            embedding_data = {
                'id': file_id,
                'vector': embedding.tolist(),  # 将 numpy 数组转换为列表
                'content': cleaned_content
            }
            store_embedding(embedding_data)
            
            files_data.append({
                'file_name': file_id,
                'content': cleaned_content
            })
            print(f"Downloaded and processed {file_id}")
    
    result = {
        'files': files_data,
        'total_count': len(files_data)
    }
    return result

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
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    
    REPO_OWNER = 'kkdai'
    REPO_NAME = 'kkdai.github.io'
    DIRECTORY_PATH = '_posts'
    
    # result = git_article(GITHUB_TOKEN, REPO_OWNER, REPO_NAME, DIRECTORY_PATH)
    # if result:
    #     print(f"Downloaded and processed {result['total_count']} files.")
    
    # 示例查询和生成响应
    question = "如何 openwebmail 邮件服务器配置?"
    response = query_and_generate_response(question, top_k=3)
    for res in response:
        print(f"File ID: {res['file_id']}, Similarity: {res['similarity']}")
        # print(f"Content: {res['content']}")
    
    # ask generation result using gemini using response 
    # Ensure response[0]['content'] is converted to a string properly
    content_str = response[0]['content'] if isinstance(response[0]['content'], str) else str(response[0]['content'])
    prompt = f"question:{question}\nrefer:{content_str}\nanswer it. reply in zh_tw\n"
    print(f'prompt: {prompt}')
    completion = generate_gemini_text_complete(prompt)
    print(completion.text)






    