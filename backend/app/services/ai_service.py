"""AI service — clause extraction and risk analysis via LLM."""

import json
import logging
from typing import Any

import tiktoken
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a contract intelligence analyst. Your job is to extract and analyse
legal clauses from contract documents.

Rules:
1. Extract ONLY clauses that appear in the provided text.
2. Never infer or fabricate clauses not present in the text.
3. Always include the exact source_text verbatim from the document.
4. Return ONLY valid JSON. No preamble, no explanation, no markdown.
5. If a clause type is not present in this chunk, omit it.
6. Confidence score: 0.9+ means the clause is unambiguous.
             0.7–0.9 means moderate confidence, manual review recommended.
             Below 0.7 means uncertain, flag for human review.

Clause types to detect:
liability, indemnification, termination, renewal, payment_terms,
data_privacy, confidentiality, intellectual_property, governing_law, exclusivity"""

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "clauses": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "clause_type", "risk_level", "finding",
                    "explanation", "recommendation", "source_text", "confidence",
                ],
                "properties": {
                    "clause_type": {"type": "string"},
                    "risk_level": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
                    "finding": {"type": "string"},
                    "explanation": {"type": "string"},
                    "recommendation": {"type": "string"},
                    "source_text": {"type": "string"},
                    "confidence": {"type": "number"},
                },
            },
        }
    },
    "required": ["clauses"],
}

VALID_CLAUSE_TYPES = {
    "liability", "indemnification", "termination", "renewal", "payment_terms",
    "data_privacy", "confidentiality", "intellectual_property", "governing_law", "exclusivity",
}

VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


class AIService:
    """Handles LLM calls for clause extraction with model fallback."""

    def __init__(self) -> None:
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.encoding = tiktoken.encoding_for_model("gpt-4o")

    def chunk_text(self, text: str) -> list[str]:
        """Split text into chunks of MAX_TOKENS_PER_CHUNK with overlap."""
        paragraphs = text.split("\n\n")
        chunks: list[str] = []
        current_chunk: list[str] = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = len(self.encoding.encode(para))

            if current_tokens + para_tokens > settings.MAX_TOKENS_PER_CHUNK and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                # Keep overlap: retain last paragraphs up to CHUNK_OVERLAP tokens
                overlap_paras: list[str] = []
                overlap_tokens = 0
                for p in reversed(current_chunk):
                    p_tok = len(self.encoding.encode(p))
                    if overlap_tokens + p_tok > settings.CHUNK_OVERLAP:
                        break
                    overlap_paras.insert(0, p)
                    overlap_tokens += p_tok
                current_chunk = overlap_paras
                current_tokens = overlap_tokens

            current_chunk.append(para)
            current_tokens += para_tokens

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        return chunks

    async def extract_clauses(self, text_chunk: str) -> list[dict[str, Any]]:
        """Extract clauses from a text chunk. Tries primary model, falls back."""
        try:
            return await self._call_openai(text_chunk)
        except Exception as e:
            logger.warning("OpenAI failed: %s. Falling back to Anthropic.", e)
            try:
                return await self._call_anthropic(text_chunk)
            except Exception as e2:
                logger.error("Anthropic also failed: %s", e2)
                return []

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def _call_openai(self, text_chunk: str) -> list[dict[str, Any]]:
        """Call OpenAI for clause extraction."""
        response = await self.openai.chat.completions.create(
            model=settings.PRIMARY_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this contract section:\n\n{text_chunk}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        content = response.choices[0].message.content or "{}"
        return self._validate_response(content)

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def _call_anthropic(self, text_chunk: str) -> list[dict[str, Any]]:
        """Call Anthropic as fallback for clause extraction."""
        response = await self.anthropic.messages.create(
            model=settings.FALLBACK_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Analyze this contract section:\n\n{text_chunk}"},
            ],
            temperature=0.1,
        )
        content = response.content[0].text
        return self._validate_response(content)

    def _validate_response(self, raw_json: str) -> list[dict[str, Any]]:
        """Validate AI response against expected schema."""
        data = json.loads(raw_json)
        clauses = data.get("clauses", [])
        validated: list[dict[str, Any]] = []

        for clause in clauses:
            # Check required fields
            required = ["clause_type", "risk_level", "finding", "explanation",
                        "recommendation", "source_text", "confidence"]
            if not all(k in clause for k in required):
                logger.warning("Skipping clause missing required fields: %s", clause.keys())
                continue
            if clause["clause_type"] not in VALID_CLAUSE_TYPES:
                logger.warning("Skipping unknown clause type: %s", clause["clause_type"])
                continue
            if clause["risk_level"] not in VALID_RISK_LEVELS:
                logger.warning("Skipping invalid risk level: %s", clause["risk_level"])
                continue
            validated.append(clause)

        return validated

    def generate_summary(self, clauses_data: list[dict[str, Any]], risk_score: float) -> str:
        """Generate an executive summary from extracted clause data."""
        risk_counts: dict[str, int] = {}
        for c in clauses_data:
            level = c.get("risk_level", "LOW")
            risk_counts[level] = risk_counts.get(level, 0) + 1

        clause_types = list({c["clause_type"] for c in clauses_data})

        parts = [
            f"Contract analysis identified {len(clauses_data)} clause(s) across "
            f"{len(clause_types)} category(ies).",
            f"Overall risk score: {risk_score:.1f}/10.0.",
        ]

        if risk_counts.get("CRITICAL", 0) > 0:
            parts.append(
                f"⚠️ {risk_counts['CRITICAL']} CRITICAL risk(s) require immediate attention."
            )
        if risk_counts.get("HIGH", 0) > 0:
            parts.append(f"{risk_counts['HIGH']} HIGH risk finding(s) identified.")

        return " ".join(parts)
