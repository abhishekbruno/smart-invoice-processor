import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import chromadb
from chromadb.config import Settings as ChromaSettings

from config.settings import settings
from core.document_chunker import DocumentChunk, document_chunker
from core.embedding_service import LocalChromaEmbeddingFunction, embedding_service
from utils.logger import logger


class VectorStore:
    """
    Persistent ChromaDB vector store for invoice documents.
    Links semantic vector chunks to relational SQLite invoice records.
    Provides idempotent indexing, similarity retrieval, and synchronization.
    """

    _instance: Optional["VectorStore"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, chroma_dir: Optional[Path] = None, collection_name: str = "invoice_documents"):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.chroma_dir = chroma_dir or settings.CHROMA_DIR
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.collection_name = collection_name
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection = None
        self._init_lock = threading.Lock()
        self._initialized = True

    def _get_collection(self):
        """Initializes ChromaDB PersistentClient and retrieves or creates the collection."""
        if self._collection is None:
            with self._init_lock:
                if self._collection is None:
                    try:
                        logger.info(f"Connecting to persistent ChromaDB at: {self.chroma_dir}")
                        self._client = chromadb.PersistentClient(
                            path=str(self.chroma_dir),
                            settings=ChromaSettings(anonymized_telemetry=False),
                        )
                        emb_fn = LocalChromaEmbeddingFunction(embedding_service)
                        self._collection = self._client.get_or_create_collection(
                            name=self.collection_name,
                            embedding_function=emb_fn,
                            metadata={"hnsw:space": "cosine"},
                        )
                        logger.info(
                            f"ChromaDB collection '{self.collection_name}' ready. (Current chunks: {self._collection.count()})"
                        )
                    except Exception as e:
                        logger.error(f"Failed to initialize ChromaDB collection: {e}", exc_info=True)
                        raise RuntimeError(f"ChromaDB initialization error: {str(e)}")

        return self._collection

    # =========================================================================
    # Document Indexing & Idempotent Updates
    # =========================================================================

    def index_invoice(
        self,
        invoice_record: Dict[str, Any],
        raw_text: Optional[str] = None,
        pages_data: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """
        Indexes an invoice into the vector database.
        Automatically removes prior chunks for this invoice ID to guarantee idempotency.
        Returns the number of chunks indexed.
        """
        invoice_id = int(invoice_record.get("id", 0))
        if not invoice_id:
            logger.warning("Cannot index invoice record without a valid database 'id'.")
            return 0

        # 1. Clean existing chunks for this invoice
        self.delete_by_invoice_id(invoice_id)

        # 2. Chunk document
        chunks: List[DocumentChunk] = document_chunker.chunk_invoice(
            invoice_record=invoice_record,
            raw_text=raw_text,
            pages_data=pages_data,
        )

        if not chunks:
            logger.warning(f"No chunks produced for invoice ID #{invoice_id}.")
            return 0

        # 3. Insert chunks into ChromaDB
        collection = self._get_collection()

        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [c.to_chroma_metadata() for c in chunks]

        try:
            collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            logger.info(
                f"Successfully indexed {len(chunks)} chunks for invoice #{invoice_id} "
                f"({invoice_record.get('vendor_name', 'Unknown')})."
            )
            return len(chunks)
        except Exception as e:
            logger.error(f"Error adding chunks to ChromaDB for invoice #{invoice_id}: {e}", exc_info=True)
            raise

    def delete_by_invoice_id(self, invoice_id: int) -> int:
        """Removes all vector chunks associated with an invoice ID."""
        try:
            collection = self._get_collection()
            # Find matching chunk IDs
            results = collection.get(where={"invoice_id": invoice_id})
            ids_to_del = results.get("ids", [])
            if ids_to_del:
                collection.delete(ids=ids_to_del)
                logger.info(f"Deleted {len(ids_to_del)} vector chunks for invoice ID #{invoice_id}.")
                return len(ids_to_del)
            return 0
        except Exception as e:
            logger.warning(f"Error removing chunks for invoice #{invoice_id}: {e}")
            return 0

    def delete_by_file_hash(self, file_hash: str) -> int:
        """Removes all vector chunks associated with a file SHA-256 hash."""
        try:
            collection = self._get_collection()
            results = collection.get(where={"file_hash": file_hash})
            ids_to_del = results.get("ids", [])
            if ids_to_del:
                collection.delete(ids=ids_to_del)
                logger.info(f"Deleted {len(ids_to_del)} vector chunks for hash {file_hash[:8]}...")
                return len(ids_to_del)
            return 0
        except Exception as e:
            logger.warning(f"Error removing chunks for hash {file_hash}: {e}")
            return 0

    # =========================================================================
    # Similarity Search & Retrieval
    # =========================================================================

    def search(
        self,
        query: str,
        n_results: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes semantic similarity search against the indexed invoice chunks.
        Returns a formatted list of matching chunks with metadata and similarity scores.
        """
        if not query or not query.strip():
            return []

        collection = self._get_collection()
        total_count = collection.count()
        if total_count == 0:
            return []

        limit = min(n_results, total_count)

        try:
            results = collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_filter if where_filter else None,
                include=["documents", "metadatas", "distances"],
            )

            hits: List[Dict[str, Any]] = []
            if results and results.get("ids") and results["ids"][0]:
                ids = results["ids"][0]
                docs = results["documents"][0] if results.get("documents") else []
                metas = results["metadatas"][0] if results.get("metadatas") else []
                distances = results["distances"][0] if results.get("distances") else []

                for i in range(len(ids)):
                    dist = float(distances[i]) if i < len(distances) else 1.0
                    # Cosine distance to similarity score in [0, 1]
                    similarity = max(0.0, 1.0 - (dist / 2.0))
                    hits.append(
                        {
                            "chunk_id": ids[i],
                            "content": docs[i] if i < len(docs) else "",
                            "metadata": metas[i] if i < len(metas) else {},
                            "distance": dist,
                            "similarity": round(similarity, 4),
                        }
                    )

            return hits
        except Exception as e:
            logger.error(f"ChromaDB search failed for query '{query}': {e}", exc_info=True)
            return []

    # =========================================================================
    # Diagnostics & Synchronization
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the vector store."""
        try:
            collection = self._get_collection()
            count = collection.count()
            # Fetch all metadata to determine unique indexed invoice IDs
            indexed_ids: Set[int] = set()
            if count > 0:
                data = collection.get(include=["metadatas"])
                for meta in data.get("metadatas", []):
                    if meta and "invoice_id" in meta:
                        try:
                            indexed_ids.add(int(meta["invoice_id"]))
                        except (ValueError, TypeError):
                            pass

            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "unique_invoices_indexed": len(indexed_ids),
                "indexed_invoice_ids": sorted(list(indexed_ids)),
                "storage_directory": str(self.chroma_dir),
                "is_ready": True,
            }
        except Exception as e:
            logger.warning(f"Error fetching vector store stats: {e}")
            return {
                "collection_name": self.collection_name,
                "total_chunks": 0,
                "unique_invoices_indexed": 0,
                "indexed_invoice_ids": [],
                "storage_directory": str(self.chroma_dir),
                "is_ready": False,
                "error": str(e),
            }

    def get_indexed_invoice_ids(self) -> Set[int]:
        """Returns the set of SQLite invoice IDs currently indexed in ChromaDB."""
        stats = self.get_stats()
        return set(stats.get("indexed_invoice_ids", []))

    def reindex_all(self, db_manager, force: bool = True) -> Dict[str, int]:
        """
        Reindexes all invoices found in the SQLite database into ChromaDB.
        """
        invoices = db_manager.get_all_invoices()
        success_count = 0
        total_chunks = 0
        failed_count = 0

        logger.info(f"Starting batch reindex of {len(invoices)} invoices into ChromaDB...")

        for inv_summary in invoices:
            inv_id = inv_summary["id"]
            full_inv = db_manager.get_invoice_by_id(inv_id)
            if not full_inv:
                continue

            try:
                chunks_indexed = self.index_invoice(full_inv)
                if chunks_indexed > 0:
                    success_count += 1
                    total_chunks += chunks_indexed
            except Exception as e:
                logger.error(f"Failed to reindex invoice #{inv_id}: {e}")
                failed_count += 1

        logger.info(
            f"Reindex complete: {success_count} invoices indexed ({total_chunks} chunks), {failed_count} failed."
        )
        return {
            "invoices_indexed": success_count,
            "total_chunks": total_chunks,
            "failed": failed_count,
        }

    def index_unindexed(self, db_manager) -> Dict[str, int]:
        """
        Finds any invoices in the SQLite database that are not yet indexed in ChromaDB
        and indexes them.
        """
        indexed_ids = self.get_indexed_invoice_ids()
        all_invoices = db_manager.get_all_invoices()
        unindexed = [inv for inv in all_invoices if inv["id"] not in indexed_ids]

        if not unindexed:
            return {"invoices_indexed": 0, "total_chunks": 0}

        success_count = 0
        total_chunks = 0
        for inv_summary in unindexed:
            full_inv = db_manager.get_invoice_by_id(inv_summary["id"])
            if not full_inv:
                continue
            try:
                cnt = self.index_invoice(full_inv)
                if cnt > 0:
                    success_count += 1
                    total_chunks += cnt
            except Exception as e:
                logger.error(f"Failed to index unindexed invoice #{inv_summary['id']}: {e}")

        return {"invoices_indexed": success_count, "total_chunks": total_chunks}


# Global vector store singleton
vector_store = VectorStore()

