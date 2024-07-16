import firebase_admin
from firebase_admin import credentials, db
import numpy as np
import google.generativeai as genai
import os

# 初始化 Firebase Admin SDK
firebase_url = os.getenv('FIREBASE_URL')
credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
cred = credentials.Certificate(credentials_path)
firebase_admin.initialize_app(cred, {'databaseURL': firebase_url})

# 初始化 Google Gemini
gemini_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_key)


def generate_embedding(text):
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document",
        title="Embedding of single string"
    )
    embedding = result['embedding']
    return embedding

def store_embedding(embedding_data):
    ref = db.reference('embeddings')
    ref.child(embedding_data['id']).set(embedding_data)
    print(f"Embedding data for {embedding_data['id']} stored successfully.")

def get_embedding(embedding_id):
    ref = db.reference('embeddings')
    embedding_data = ref.child(embedding_id).get()
    return embedding_data

def get_all_embeddings():
    ref = db.reference('embeddings')
    all_embeddings = ref.get()
    return all_embeddings

def find_nearest_neighbors(target_embedding, num_neighbors=1):
    all_embeddings = get_all_embeddings()
    distances = []

    target_vector = np.array(target_embedding['vector'])

    for embedding_id, embedding_data in all_embeddings.items():
        vector = np.array(embedding_data['vector'])
        distance = np.linalg.norm(target_vector - vector)
        distances.append((embedding_id, distance))

    distances.sort(key=lambda x: x[1])
    nearest_neighbors = distances[:num_neighbors]
    return nearest_neighbors

# 示例文本
text_1 = "What is the meaning of life?"
text_2 = "How to learn Python programming?"
text_3 = "The quick brown fox jumps over the lazy dog."

# 生成嵌入
embedding_vector_1 = generate_embedding(text_1)
embedding_vector_2 = generate_embedding(text_2)
embedding_vector_3 = generate_embedding(text_3)

# 创建嵌入数据
embedding_data_1 = {
    'id': 'embedding_1',
    'vector': embedding_vector_1
}

embedding_data_2 = {
    'id': 'embedding_2',
    'vector': embedding_vector_2
}

embedding_data_3 = {
    'id': 'embedding_3',
    'vector': embedding_vector_3
}

# 存储嵌入数据
store_embedding(embedding_data_1)
store_embedding(embedding_data_2)
store_embedding(embedding_data_3)

# 获取并打印嵌入数据
retrieved_embedding = get_embedding('embedding_1')
print('Retrieved embedding data:', retrieved_embedding)

# 查找最近邻
target_embedding = embedding_data_1
nearest_neighbors = find_nearest_neighbors(target_embedding, num_neighbors=2)
print('Nearest neighbors:', nearest_neighbors)

# find another string embedding_11
text_11 = "How to learn Python programming?"
embedding_vector_11 = generate_embedding(text_11)
embedding_data_11 = {
    'id': 'embedding_11',
    'vector': embedding_vector_11
}   
store_embedding(embedding_data_11)

# find nearest neighbors for embedding_11
target_embedding = embedding_data_11
nearest_neighbors = find_nearest_neighbors(target_embedding, num_neighbors=2)
print('Nearest neighbors:', nearest_neighbors)
