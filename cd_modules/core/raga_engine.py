import os
import shutil
import gc
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


class RAGAEngine:
    """Motor de ingesta y recuperación de evidencia para H‑ANCHOR."""

    def __init__(self, persist_directory: str = "./chroma_db") -> None:
        """
        Inicializa el motor RAGA con posibilidad de persistencia local.

        :param persist_directory: Directorio donde se almacenarán los
            vectores generados. Si existe, se intenta reutilizar; de lo
            contrario, se creará al realizar una ingesta.
        """
        self.persist_directory = persist_directory
        # Usamos embeddings de OpenAI (requiere variable de entorno OPENAI_API_KEY)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        # Conexión a la Base de Datos Vectorial
        # Solo cargamos si existe, para evitar crear bases vacías
        if os.path.exists(persist_directory):
            self.vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings,
            )
        else:
            self.vector_store = None

    def ingest_document(self, file_path: str):
        """
        Ingesta un documento en la base vectorial.

        1. Carga el PDF desde ``file_path``.
        2. Lo trocea en fragmentos manejables (chunks) usando un divisor
           de caracteres recursivo.
        3. Genera vectores para cada fragmento y los guarda en
           ``self.persist_directory``.

        :param file_path: Ruta del archivo PDF a ingerir.
        :return: ``True`` si la ingesta fue exitosa, o un mensaje de error.
        """
        if not os.path.exists(file_path):
            return f"❌ Error: No encuentro el archivo {file_path}"

        print(f"📥 Ingestando {file_path}...")

        # 1. Cargar
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        # 2. Trocear (Split)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        # 3. Vectorizar y Guardar
        # IMPORTANTE: Liberar conexión anterior antes de borrar
        if self.vector_store:
            self.vector_store = None
            gc.collect()  # Forzar al recolector de basura a soltar el archivo

        # Si ya existía DB, la borramos para empezar de cero (limpieza)
        if os.path.exists(self.persist_directory):
            try:
                shutil.rmtree(self.persist_directory)
            except Exception as e:
                print(f"⚠️ No se pudo borrar el directorio antiguo: {e}")

        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
        )
        print(f"✅ Ingestión completada: {len(splits)} fragmentos indexados.")
        return True

    def retrieve(self, query: str, k: int = 3):
        """
        Busca los ``k`` fragmentos más similares a la consulta.

        Devuelve una lista de diccionarios con el texto exacto, la fuente
        (número de página) y la relevancia de cada fragmento.

        :param query: Cadena que describe la pregunta o término de búsqueda.
        :param k: Número de fragmentos a recuperar.
        :return: Lista de evidencias, o lista vacía si no hay base cargada.
        """
        if not self.vector_store:
            return []

        # Búsqueda por similitud (Similarity Search)
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
        except Exception as e:
            print(f"Error en retrieve: {e}")
            return []

        evidence = []
        for doc, score in results:
            evidence.append(
                {
                    "content": doc.page_content,
                    "source": f"Página {doc.metadata.get('page', 'N/A')}",
                    "relevance": f"{score:.4f}",
                }
            )

        return evidence
