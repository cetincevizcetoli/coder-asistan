import os
import shutil
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import torch
import config
from config import Colors

class MemoryManager:
    def __init__(self, project_root: str):
        """
        Belirtilen proje dizini için izole hafıza yöneticisi.
        """
        self.project_root = project_root
        self.memory_path = os.path.join(project_root, config.MEMORY_DIR_NAME)
        
        # 1. Donanım Algılama ve Embedding Modelini Yükleme
        self.device = self._detect_device()
        print(f"{Colors.MAGENTA}🧠 Hafıza Motoru Başlatılıyor... ({self.device}){Colors.RESET}")
        
        try:
            self.embedder = SentenceTransformer(config.EMBEDDING_MODEL, device=self.device)
        except Exception as e:
            print(f"{Colors.RED}Model yükleme hatası, CPU'ya geçiliyor: {e}{Colors.RESET}")
            self.embedder = SentenceTransformer(config.EMBEDDING_MODEL, device="cpu")

        # 2. ChromaDB İstemcisini Başlatma (Persistent)
        os.makedirs(self.memory_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.memory_path)
        
        # Koleksiyonu al veya oluştur
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"} # Kod benzerliği için kosinüs idealdir
        )

    def _detect_device(self) -> str:
        """Sistemi tarar: NVIDIA GPU -> Apple Silicon (MPS) -> CPU"""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    def index_files(self, file_paths: list):
        """Dosyaları okur, vektörleştirir ve veritabanına kaydeder."""
        documents = []
        metadatas = []
        ids = []

        print(f"{Colors.CYAN}📥 {len(file_paths)} dosya indeksleniyor...{Colors.RESET}")

        for fpath in file_paths:
            full_path = os.path.join(self.project_root, fpath)
            if not os.path.exists(full_path):
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basit chunking: Dosyayı olduğu gibi alıyoruz (küçük dosyalar için)
                # Büyük projelerde buraya "TextSplitter" eklenmeli.
                if len(content.strip()) == 0: continue

                documents.append(content)
                metadatas.append({"source": fpath})
                ids.append(fpath) # ID olarak dosya yolu benzersizdir

            except Exception as e:
                print(f"{Colors.YELLOW}Uyarı: {fpath} okunamadı ({e}){Colors.RESET}")

        if documents:
            # Embedding işlemini manuel yapıp Chroma'ya veriyoruz (Daha fazla kontrol için)
            embeddings = self.embedder.encode(documents, normalize_embeddings=True).tolist()
            
            # Upsert: Varsa güncelle, yoksa ekle
            self.collection.upsert(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"{Colors.GREEN}✅ Hafıza güncellendi.{Colors.RESET}")

    def query(self, prompt: str, n_results=config.MAX_CONTEXT_RESULTS):
        """Prompt ile alakalı kod parçalarını getirir."""
        query_embedding = self.embedder.encode([prompt], normalize_embeddings=True).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        context_parts = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                source = results['metadatas'][0][i]['source']
                context_parts.append(f"--- BAĞLAM: {source} ---\n{doc}\n")
        
        return "\n".join(context_parts)

    def clear_memory(self):
        """Hafızayı sıfırlar."""
        self.client.delete_collection(config.COLLECTION_NAME)
        shutil.rmtree(self.memory_path)
        print(f"{Colors.YELLOW}🧹 Hafıza temizlendi.{Colors.RESET}")