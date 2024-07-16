import os
import json
import firebase_admin
from firebase_admin import credentials, db
from github import Github
import numpy as np
import google.generativeai as genai

# 初始化 Firebase Admin SDK
firebase_url = os.getenv('FIREBASE_URL')
credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
cred = credentials.Certificate('../service_account.json')
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
    try:
        ref = db.reference('blog_embeddings')
        return ref.child(file_id).get() is not None
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def git_article(github_token, repo_owner, repo_name, directory_path):
    g = Github(github_token)
    repo = g.get_repo(f"{repo_owner}/{repo_name}")
    contents = repo.get_contents(directory_path)
    
    files_data = []
    
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            # get file name without extension
            file_id = file_content.name.split('.')[0]
            print(f"Processing file_id:{file_id}")
            if check_if_exists(file_id):
                print(f"File {file_id} already exists in the database. Skipping.")
                continue
            
            file_content_decoded = file_content.decoded_content.decode('utf-8')
            embedding = generate_embedding(file_content_decoded)
            
            embedding_data = {
                'id': file_id,
                'vector': embedding.tolist()  # 将 numpy 数组转换为列表
            }
            store_embedding(embedding_data)
            
            files_data.append({
                'file_name': file_id,
                'content': file_content_decoded
            })
            print(f"Downloaded and processed {file_id}")
    
    result = {
        'files': files_data,
        'total_count': len(files_data)
    }
    return result

# 示例调用
if __name__ == "__main__":
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    
    REPO_OWNER = 'kkdai'
    REPO_NAME = 'kkdai.github.io'
    DIRECTORY_PATH = '_posts'
    
    result = git_article(GITHUB_TOKEN, REPO_OWNER, REPO_NAME, DIRECTORY_PATH)
    if result:
        print(f"Downloaded and processed {result['total_count']} files.")