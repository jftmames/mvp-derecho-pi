import os
import shutil
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

class RAGAEngine:
    def __init__(self, persist_directory="./chroma_db"):
        """
        Inicializa el motor RAGA con persistencia local.
        """
        self.persist_directory = persist_directory
        # Usamos embeddings de OpenAI (requiere variable de entorno OPENAI_API_KEY)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Conexión a la Base de Datos Vectorial (Si existe, la carga; si no, espera ingestión)
        if os.path.exists(persist_directory):
            self.vector_store = Chroma(
                persist_directory=persist_directory, 
                embedding_function=self.embeddings
            )
        else:
            self.vector_store = None

    def ingest_document(self, file_path):
        """
        1. Carga el PDF.
        2. Lo trocea en fragmentos manejables (Chunks).
        3. Genera vectores y los guarda.
        """
        if not os.path.exists(file_path):
            return f"❌ Error: No encuentro el archivo {file_path}"

        print(f"📥 Ingestando {file_path}...")
        
        # 1. Cargar
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        
        # 2. Trocear (Split)
        # Usamos chunks de 1000 caracteres con solapamiento para no cortar frases
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        
        # 3. Vectorizar y Guardar
        # Si ya existía DB, la borramos para este Sprint (limpieza)
        if os.path.exists(self.persist_directory):
            shutil.rmtree(self.persist_directory)
            
        self.vector_store = Chroma.from_documents(
            documents=splits, 
            embedding=self.embeddings, 
            persist_directory=self.persist_directory
        )
        print(f"✅ Ingestión completada: {len(splits)} fragmentos indexados.")
        return True

    def retrieve(self, query, k=3):
        """
        Busca los k fragmentos más similares a la pregunta.
        Devuelve el texto exacto y la fuente (página).
        """
        if not self.vector_store:
            return []

        # Búsqueda por similitud (Similarity Search)
        results = self.vector_store.similarity_search_with_score(query, k=k)
        
        evidence = []
        for doc, score in results:
            evidence.append({
                "content": doc.page_content,
                "source": f"Página {doc.metadata.get('page', 'N/A')}",
                "relevance": f"{score:.4f}" # Score de distancia (menor es mejor)
            })
        
        return evidence
