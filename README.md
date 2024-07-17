```markdown
# Jekyll Blog with Firebase RAG DB

This repository provides a set of Python scripts to help you use Firebase as a Retrieval-Augmented Generation (RAG) database for embedding and querying your Jekyll (GitHub Pages) blog content.

## Scripts Overview

1. **git_query.py**: Basic GitHub query tutorial.
2. **embedding.py**: Tutorial on embedding data into Firebase DB.
3. **blog_query.py**: How to query data within your blog.
4. **blog_embedding.py**: Helps you create a RAG DB from your Jekyll GitHub Pages content.

## Getting Started

### Prerequisites

- Python 3.x
- Firebase account and project setup
- GitHub account with a Jekyll blog repository

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/kkdai/jekyll-rag-firebase.git
    cd jekyll-rag-firebase
    ```

2. Install required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

### Usage

#### 1. GitHub Query Tutorial (`git_query.py`)

This script demonstrates how to perform basic queries on GitHub repositories.

```sh
python git_query.py
```

#### 2. Embedding Data into Firebase DB (`embedding.py`)

Learn how to embed data into your Firebase database.

```sh
python embedding.py
```

#### 3. Querying Blog Data (`blog_query.py`)

This script shows how to query data within your Jekyll blog.

```sh
python blog_query.py
```

#### 4. Creating RAG DB from Jekyll GitHub Pages (`blog_embedding.py`)

Use this script to embed your Jekyll GitHub Pages content into a RAG DB.

```sh
python blog_embedding.py
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, feel free to open an issue or contact me at [your-email@example.com](mailto:your-email@example.com).
