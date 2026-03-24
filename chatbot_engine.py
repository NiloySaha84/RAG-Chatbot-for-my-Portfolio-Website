import os
import glob
import shutil
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(override=True)

MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4")
DB_NAME = os.getenv("VECTOR_DB_NAME", "vector_db")

GITHUB_LINK = "https://github.com/niloy-saha"
ABOUT_LINK = "https://niloy-saha84-github-io.vercel.app/#about"
EDUCATION_LINK = "https://niloy-saha84-github-io.vercel.app/#education"
EXPERIENCE_LINK = "https://niloy-saha84-github-io.vercel.app/#experience"
PROJECTS_PAGE_LINK = "https://niloy-saha84-github-io.vercel.app/#projects"
SKILLS_LINK = "https://niloy-saha84-github-io.vercel.app/#skills"
CONTACT_LINK = "https://niloy-saha84-github-io.vercel.app/#contact"

SYSTEM_PROMPT_TEMPLATE = """
You are an AI assistant representing Niloy Saha on his personal portfolio website.

Your job is to answer questions about Niloy using ONLY the provided context (retrieved documents such as resume, project READMEs, and other indexed data). Do NOT make up information. If the answer is not in the context, say you don’t have enough information.

Always speak in a professional, concise, and friendly tone.

IMPORTANT RULES:

1. IDENTITY:
- This website belongs to Niloy Saha.
- If users refer to "you", interpret it as Niloy Saha (not the AI).

2. CONTEXT USAGE:
- Base your answers strictly on the retrieved context.
- Do not hallucinate or assume missing details.
- If unsure, say: "I don't have enough information about that."

3. PROJECT QUESTIONS:
- If the user asks about projects, list relevant projects from context.
- After listing, ALWAYS include:
  "You can explore more projects on GitHub: {GITHUB_LINK} or visit the projects section: {PROJECTS_PAGE_LINK}."

4. EXPERIENCE / EDUCATION QUESTIONS:
- If the user asks about studies, education, or work experience:
  - Summarize clearly using the context.
  - Then ALWAYS include:
  "For more details, you can check his GitHub: {GITHUB_LINK} or visit his portfolio: {EDUCATION_LINK}."

5. SKILLS QUESTIONS:
- If the user asks about skills, list relevant skills from context.
- Then ALWAYS include:
  "For more details, you can check his GitHub: {GITHUB_LINK} or visit his portfolio: {SKILLS_LINK}."

6. STYLE:
- Keep answers short and structured.
- Use bullet points when listing items.
- Avoid long paragraphs.

7. PERSONAL QUESTIONS:
- Answer only if information is available in the context.
- Do not fabricate personality traits or personal life details.

8. FALLBACK:
- If no relevant information is found:
  "I couldn't find that information in Niloy's portfolio data."

9. NO META TALK:
- Do not mention "context", "RAG", or "documents".
- Do not say "based on the provided data".

Context: {context}

Useful Links:
- GitHub: {GITHUB_LINK}
- Projects Page: {PROJECTS_PAGE_LINK}
- Education Page: {EDUCATION_LINK}
- Experience Page: {EXPERIENCE_LINK}
- Skills Page: {SKILLS_LINK}
- Contact Page: {CONTACT_LINK}
""".strip()


def load_documents():
    folders = glob.glob("knowledge-base/*")
    documents = []

    for folder in folders:
        folder_name = os.path.basename(folder).lower()

        if folder_name == "resume":
            pdf_files = glob.glob(f"{folder}/*.pdf")
            for pdf in pdf_files:
                loader = PyPDFLoader(file_path=pdf)
                folder_docs = loader.load()
                for doc in folder_docs:
                    doc.metadata["doc_type"] = "resume"
                    doc.metadata["source"] = pdf
                    documents.append(doc)
        else:
            loader = DirectoryLoader(
                folder,
                glob="*.md",
                loader_cls=TextLoader,
                loader_kwargs={"encoding": "utf-8"},
            )
            folder_docs = loader.load()
            for doc in folder_docs:
                doc.metadata["doc_type"] = folder_name
                doc.metadata["source"] = doc.metadata.get("source", "")
                documents.append(doc)

    return documents


def build_vectorstore():
    rebuild = os.getenv("REBUILD_VECTOR_DB", "false").lower() == "true"
    db_path = Path(DB_NAME)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    if rebuild and db_path.exists():
        shutil.rmtree(db_path)

    if db_path.exists():
        return Chroma(persist_directory=DB_NAME, embedding_function=embeddings)

    documents = load_documents()
    if not documents:
        raise ValueError("No documents found in knowledge-base/")

    print(f"Loaded {len(documents)} documents")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Divided into {len(chunks)} chunks")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_NAME,
    )
    print(f"Vectorstore created with {vectorstore._collection.count()} documents")
    return vectorstore


@lru_cache(maxsize=1)
def get_components():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set")

    vectorstore = build_vectorstore()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    llm = ChatOpenAI(
        model=MODEL,
        api_key=openai_api_key,
        temperature=0.2,
    )
    return retriever, llm


def answer_question(question: str, history=None):
    retriever, llm = get_components()

    docs = retriever.invoke(question)
    context = "\n\n".join(doc.page_content for doc in docs) if docs else ""

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        context=context,
        GITHUB_LINK=GITHUB_LINK,
        ABOUT_LINK=ABOUT_LINK,
        EDUCATION_LINK=EDUCATION_LINK,
        EXPERIENCE_LINK=EXPERIENCE_LINK,
        PROJECTS_PAGE_LINK=PROJECTS_PAGE_LINK,
        SKILLS_LINK=SKILLS_LINK,
        CONTACT_LINK=CONTACT_LINK,
    )

    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=question),
        ]
    )
    return response.content