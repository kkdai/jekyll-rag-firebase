from github import Github
import os

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
            files_data.append({
                'file_name': file_content.name,
                'content': file_content.decoded_content.decode('utf-8')
            })
            print(f"Downloaded {file_content.name}")
    
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
        print(f"Downloaded {result['total_count']} files.")