"""Background analysis worker — processes contracts from Redis queue."""

import asyncio
import logging
from uuid import UUID

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.database import async_session
from app.models.clause import Clause
from app.models.risk import Risk
from app.repositories.contract_repo import ContractRepository
from app.repositories.clause_repo import ClauseRepository
from app.services.ai_service import AIService
from app.services.parsing_service import ParsingService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Risk scoring weights per master context spec
RISK_WEIGHTS = {
    "CRITICAL": 3.0,
    "HIGH": 2.0,
    "MEDIUM": 1.0,
    "LOW": 0.2,
}


def calculate_risk_score(risk_levels: list[str]) -> tuple[float, str]:
    """Calculate contract-level risk score and risk level."""
    score = sum(RISK_WEIGHTS.get(level, 0) for level in risk_levels)
    normalized = min(score / 10.0, 10.0) * 10.0  # Scale to 0-10
    normalized = min(normalized, 10.0)

    # Simpler: just use raw weighted sum capped at 10
    raw = min(sum(RISK_WEIGHTS.get(level, 0) for level in risk_levels), 10.0)

    if raw <= 3.0:
        level = "LOW"
    elif raw <= 5.0:
        level = "MEDIUM"
    elif raw <= 7.5:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return round(raw, 2), level


async def process_contract(contract_id: UUID, company_id: UUID) -> None:
    """Full analysis pipeline for a single contract."""
    ai_service = AIService()
    parsing_service = ParsingService()

    async with async_session() as db:
        contract_repo = ContractRepository(db)
        clause_repo = ClauseRepository(db)

        try:
            # Update status to processing
            await contract_repo.update_status(contract_id, company_id, "processing")
            await db.commit()

            # Get contract
            contract = await contract_repo.get_by_id(contract_id, company_id)
            if contract is None:
                logger.error("Contract %s not found.", contract_id)
                return

            # Parse document
            full_text, page_count = await parsing_service.parse(contract.file_path)

            # Update page count
            contract.page_count = page_count

            # Check page limit
            if page_count > settings.MAX_PAGES_PER_CONTRACT:
                await contract_repo.update_status(
                    contract_id, company_id, "failed",
                    error_message=f"Document exceeds {settings.MAX_PAGES_PER_CONTRACT} page limit.",
                )
                await db.commit()
                return

            # Chunk text
            chunks = ai_service.chunk_text(full_text)
            logger.info("Contract %s: %d chunks to process.", contract_id, len(chunks))

            # Process each chunk through AI
            all_findings: list[dict] = []
            for i, chunk in enumerate(chunks):
                logger.info("Processing chunk %d/%d for contract %s", i + 1, len(chunks), contract_id)
                findings = await ai_service.extract_clauses(chunk)
                all_findings.extend(findings)

            # Create clause and risk records
            clause_models: list[Clause] = []
            risk_models: list[Risk] = []

            for finding in all_findings:
                clause = Clause(
                    contract_id=contract_id,
                    clause_type=finding["clause_type"],
                    clause_text=finding["source_text"],
                    risk_level=finding["risk_level"],
                )
                clause_models.append(clause)

            await clause_repo.bulk_create_clauses(clause_models)

            for i, finding in enumerate(all_findings):
                risk = Risk(
                    contract_id=contract_id,
                    clause_id=clause_models[i].id if i < len(clause_models) else None,
                    risk_type=finding["clause_type"],
                    severity=finding["risk_level"],
                    finding=finding["finding"],
                    explanation=finding["explanation"],
                    recommendation=finding["recommendation"],
                    source_text=finding["source_text"],
                    confidence=finding.get("confidence"),
                )
                risk_models.append(risk)

            await clause_repo.bulk_create_risks(risk_models)

            # Calculate risk score
            risk_levels = [f["risk_level"] for f in all_findings]
            risk_score, risk_level = calculate_risk_score(risk_levels)

            # Generate summary
            summary = ai_service.generate_summary(all_findings, risk_score)

            # Update contract as completed
            await contract_repo.update_status(
                contract_id, company_id, "completed",
                risk_score=risk_score,
                risk_level=risk_level,
                summary=summary,
            )
            await db.commit()
            logger.info("Contract %s analysis completed. Score: %s", contract_id, risk_score)

        except Exception as e:
            logger.exception("Contract %s analysis failed: %s", contract_id, e)
            await db.rollback()
            async with async_session() as error_db:
                error_repo = ContractRepository(error_db)
                await error_repo.update_status(
                    contract_id, company_id, "failed",
                    error_message=str(e),
                )
                await error_db.commit()


async def worker_loop() -> None:
    """Main worker loop — polls Redis queue for analysis jobs."""
    logger.info("Analysis worker started. Listening for jobs...")
    r = aioredis.from_url(settings.REDIS_URL)

    try:
        while True:
            # Blocking pop with 5-second timeout
            result = await r.brpop("contractiq:analysis_queue", timeout=5)
            if result is None:
                continue

            _, payload = result
            payload_str = payload.decode("utf-8")

            try:
                contract_id_str, company_id_str = payload_str.split(":")
                contract_id = UUID(contract_id_str)
                company_id = UUID(company_id_str)
                await process_contract(contract_id, company_id)
            except Exception as e:
                logger.exception("Failed to process job payload '%s': %s", payload_str, e)
    finally:
        await r.aclose()


if __name__ == "__main__":
    asyncio.run(worker_loop())
