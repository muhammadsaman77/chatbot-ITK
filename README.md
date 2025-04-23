  # 🎓 RAG-Powered Academic Info Assistant

  **Retrieval-Augmented Generation (RAG)** system designed to help university students quickly find information about academic activities like **Internships**, **Field Work**, **MBKM**, and **Thesis Seminars**.

  ---

## 🛠️ Tech Stack

  | Component         | Technology                |
|-------------------|---------------------------|
| Programming Lang  | Python 3.10+              |
| RAG Framework     | Langchain                 |
| Embedding Model   | LLaMA3.2:1.b / LLaMA3.2:3.b /Indo-Sentence-BERT        |
| Vector Database   | Chroma   |
| LLM               | LLaMA3.2:1.b / LLaMA3.2:3.b  |
| PDF Parsing       | PyMuPDF |

## 🧪 Running `experimentation.ipynb` (Using Poetry)

This project uses [Poetry](https://python-poetry.org/) for Python dependency management. To run the `experimentation.ipynb` notebook, follow these steps:

---
### ✅ 1. Install Poetry

If you don't have Poetry installed, use the following command:

```bash
curl -sSL https://install.python-poetry.org | python3 - 
```
For other installation methods, visit: https://python-poetry.org/docs/#installation
### 🔧 2. Set Up the Project Environment
Clone this repository and install the dependencies:
```
git clone https://github.com/muhammadsaman77/chatbot-ITK.git
cd chatbot-ITK

# Install project dependencies
poetry install
```

### 💻 3. Launch Poetry Shell and Add Jupyter Kernel
Run the following commands to create a Poetry-managed virtual environment and install the Jupyter kernel:
```
# Enter Poetry virtual environment
poetry shell

# Install the Jupyter kernel for the project
python -m ipykernel install --user --name=chatbot-ITK

```
This will create a new Jupyter kernel named chatbot-ITK that you'll use in your notebook.

---
### 🧠 Contributions & Extensions


We welcome contributions! You can help by:

- Adding new academic documents (e.g., scholarship application)
- Improving the extraction of document text or handling of new file formats

Feel free to open a pull request or contact us for more information.

---

### ✨ Created by

👨‍💻 [@muhammadsaman77](https://github.com/muhammadsaman77) — Backend & AI Engineer  
📘  Department of Informatics, Kalimantan Institute Technology

