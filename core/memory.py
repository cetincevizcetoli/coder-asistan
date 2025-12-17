import os
import shutil
import chromadb
import torch
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import config
from config import Colors

class MemoryManager:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.memory_path = os.path.join(project_root, config.MEMORY_DIR_NAME)
        self.bm25_path = os.path.join(self.memory_path, "keyword_index.json")
        
        # 1. Donanım Algılama
        self.device = self._detect_device()
        print(f"{Colors.MAGENTA}🧠 Hibrit Hafıza Motoru Başlatılıyor... ({self.device}){Colors.RESET}")
        
        # 2. Vektör Motoru (ChromaDB)
        self.embedder = SentenceTransformer(config.EMBEDDING_MODEL, device=self.device)
        os.makedirs(self.memory_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.memory_path)
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

        # 3. Anahtar Kelime Motoru (BM25)
        self.bm25 = None
        self.indexed_files = []
        self._load_bm25()

    def _detect_device(self):
        if torch.cuda.is_available(): return "cuda"
        if torch.backends.mps.is_available(): return "mps"
        return "cpu"

    def _load_bm25(self):
        """BM25 indeksini diskten yükler."""
        if os.path.exists(self.bm25_path):
            try:
                with open(self.bm25_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.indexed_files = data['files']
                    corpus = [doc.split() for doc in data['corpus']]
                    self.bm25 = BM25Okapi(corpus)
            except: pass

    def index_files(self, file_paths: list):
        """Dosyaları hem Vektör hem de BM25 için indeksler."""
        documents = []
        metadatas = []
        ids = []
        corpus_for_bm25 = []

        print(f"{Colors.CYAN}📥 {len(file_paths)} dosya hibrit indeksleniyor...{Colors.RESET}")

        for fpath in file_paths:
            full_path = os.path.join(self.project_root, fpath)
            if not os.path.exists(full_path): continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if not content.strip(): continue

                documents.append(content)
                metadatas.append({"source": fpath})
                ids.append(fpath)
                corpus_for_bm25.append(content)
                if fpath not in self.indexed_files: self.indexed_files.append(fpath)

            except Exception as e:
                print(f"{Colors.YELLOW}Uyarı: {fpath} okunamadı ({e}){Colors.RESET}")

        if documents:
            # Vektör Kayıt
            embeddings = self.embedder.encode(documents, normalize_embeddings=True).tolist()
            self.collection.upsert(documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids)
            
            # BM25 Kayıt
            current_data = {"files": self.indexed_files, "corpus": documents} 
            with open(self.bm25_path, 'w', encoding='utf-8') as f:
                json.dump(current_data, f)
            self._load_bm25()
            print(f"{Colors.GREEN}✅ Hibrit hafıza güncellendi.{Colors.RESET}")

    def query(self, prompt: str, n_results=config.MAX_CONTEXT_RESULTS):
        """Hibrit Arama: Vektör + BM25 sonuçlarını birleştirir."""
        # 1. Vektör Araması (Anlamsal)
        query_embedding = self.embedder.encode([prompt], normalize_embeddings=True).tolist()
        vector_results = self.collection.query(query_embeddings=query_embedding, n_results=n_results)
        
        vector_docs = []
        if vector_results['documents']:
            for i, doc in enumerate(vector_results['documents'][0]):
                source = vector_results['metadatas'][0][i]['source']
                vector_docs.append((source, doc, "Vektör"))

        # 2. BM25 Araması (Anahtar Kelime)
        bm25_docs = []
        if self.bm25:
            tokenized_query = prompt.split()
            top_n = self.bm25.get_top_n(tokenized_query, self.indexed_files, n=n_results)
            for source in top_n:
                # BM25'ten gelen dosyanın içeriğini Chroma'dan çekelim
                res = self.collection.get(ids=[source])
                if res['documents']:
                    bm25_docs.append((source, res['documents'][0], "Keyword"))

        # 3. Sonuçları Birleştir (Tekilleştir)
        seen_sources = set()
        final_context = []
        
        # Öncelik: BM25 (Nokta atışı kelime eşleşmesi) sonra Vektör
        for source, doc, mtype in (bm25_docs + vector_docs):
            if source not in seen_sources:
                final_context.append(f"--- BAĞLAM ({mtype}): {source} ---\n{doc}\n")
                seen_sources.add(source)
                if len(final_context) >= n_results: break
        
        return "\n".join(final_context)