from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from rag.chunker import chunk_text
from rag.document_loader import load_documents
from rag.vector_store import LocalVectorStore
from services.response_formatter import unified_response
from src.config import POLICY_DIR, RAG_INDEX_PATH


class RAGAgent:
    def __init__(self, policy_dir: Path = POLICY_DIR, index_path: Path = RAG_INDEX_PATH) -> None:
        self.policy_dir = policy_dir
        self.store = LocalVectorStore(index_path)
        if not self.store.load():
            self.build_index()

    def load_documents(self):
        return load_documents(self.policy_dir)

    def create_chunks(self) -> list[dict[str, str]]:
        chunks = []
        for document in self.load_documents():
            for index, text in enumerate(chunk_text(document.text, chunk_size=500, overlap=100), start=1):
                section = "Section"
                for line in text.splitlines():
                    if line.startswith("Section:"):
                        section = line.replace("Section:", "").strip()
                        break
                chunks.append({"source": document.source, "section": section or f"Chunk {index}", "text": text})
        return chunks

    def build_index(self) -> None:
        chunks = self.create_chunks()
        self.store.build([chunk["text"] for chunk in chunks], chunks)

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        return self.store.search(query, top_k=top_k)

    def generate_answer(self, query: str, chunks: list[dict[str, Any]]) -> str:
        if not chunks or chunks[0]["score"] < 0.08:
            return "I could not find a grounded answer in the synthetic hospital policy documents."
        selected = self._select_best_chunk(query, chunks)
        return self._answer_from_chunk(selected)

    def _answer_from_chunk(self, selected: dict[str, Any]) -> str:
        section_body = self._section_body(str(selected["text"]))
        source = str(selected["source"]).replace("_", " ").replace(".txt", "").title()
        return f"According to {source}, {section_body}"

    def answer(self, query: str, *, confidence: float = 0.9, route_reason: str = "") -> dict[str, Any]:
        start = time.perf_counter()
        chunks = self.retrieve(query, top_k=10)
        retrieval_ok = bool(chunks) and max(float(chunk.get("score", 0)) for chunk in chunks) >= 0.08
        if not retrieval_ok:
            return unified_response(
                query=query,
                selected_agent="RAG Agent",
                answer="I could not find a grounded answer in the synthetic hospital policy documents.",
                sources=[],
                confidence=confidence,
                start_time=start,
                status="not_found",
                route_reason=route_reason,
            )
        selected = self._select_best_chunk(query, chunks) if chunks else None
        answer = self._answer_from_chunk(selected) if selected else self.generate_answer(query, chunks)
        if selected:
            chunks = [selected] + [
                chunk
                for chunk in chunks
                if not (chunk.get("source") == selected.get("source") and chunk.get("section") == selected.get("section"))
            ]
        return unified_response(
            query=query,
            selected_agent="RAG Agent",
            answer=answer,
            sources=chunks,
            confidence=confidence,
            start_time=start,
            status="success",
            route_reason=route_reason,
        )

    def _select_best_chunk(self, query: str, chunks: list[dict[str, Any]]) -> dict[str, Any]:
        normalized = query.lower()
        chunks = self._expand_candidates(normalized, chunks)
        preferred_sections: list[str] = []
        if any(word in normalized for word in ["timing", "time", "hours", "visiting", "visitor"]):
            preferred_sections.extend(["Procedure", "Exceptions"])
        if "policy" in normalized:
            preferred_sections.extend(["Purpose", "Procedure"])
        if any(word in normalized for word in ["escalate", "escalation", "report", "reported"]):
            preferred_sections.extend(["Escalation Process", "Procedure"])
        if any(word in normalized for word in ["purpose", "why"]):
            preferred_sections.append("Purpose")
        for section in preferred_sections:
            for chunk in chunks:
                if chunk.get("section") == section:
                    return chunk
        non_review_chunks = [chunk for chunk in chunks if chunk.get("section") != "Review Date"]
        return non_review_chunks[0] if non_review_chunks else chunks[0]

    def _expand_candidates(self, normalized: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        source_hint = None
        if any(word in normalized for word in ["visitor", "visitors", "visiting"]):
            source_hint = "visitor_policy.txt"
        elif "discharge" in normalized:
            source_hint = "discharge_policy.txt"
        elif "privacy" in normalized:
            source_hint = "privacy_policy.txt"
        elif "medication" in normalized:
            source_hint = "medication_policy.txt"
        elif "infection" in normalized:
            source_hint = "infection_control_policy.txt"
        elif "billing" in normalized or "insurance" in normalized:
            source_hint = "billing_insurance_policy.txt"

        if not source_hint:
            return chunks

        expanded = list(chunks)
        existing = {(chunk.get("source"), chunk.get("section")) for chunk in expanded}
        for item in self.store.metadata:
            key = (item.get("source"), item.get("section"))
            if item.get("source") == source_hint and key not in existing:
                expanded.append({**item, "score": 0.0})
        return expanded

    def _section_body(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        body = [
            line
            for line in lines
            if not line.startswith(("Policy Title:", "Policy ID:", "Section:", "Notice:"))
        ]
        return " ".join(body)
