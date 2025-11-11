from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status

from .kyc_repository import upsert_kyc, KYC_PENDING, KYC_REVIEWING, KYC_APPROVED, KYC_REJECTED
from .kyc_storage import save_kyc_blob
from .schemas import KycPayload, KycResponse

VALID_STATUSES = {KYC_PENDING, KYC_REVIEWING, KYC_APPROVED, KYC_REJECTED}


class KycService:
    def save_kyc(self, user_id: str, payload: KycPayload) -> KycResponse:
        if payload.status not in VALID_STATUSES:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='invalid KYC status')

        blob_path = save_kyc_blob(user_id, payload.dict())

        record = upsert_kyc(
            user_id,
            status=payload.status,
            doc_type=payload.docType,
            doc_number=payload.docNumber,
            selfie_url=payload.selfieUrl,
            doc_front_url=payload.docFrontUrl,
            doc_back_url=payload.docBackUrl,
            meta=payload.meta or {},
            reviewer=payload.reviewer,
            reviewed_at=payload.reviewedAt
        )
        return KycResponse(
            userId=user_id,
            status=record['kyc_status'],
            docType=record['doc_type'],
            docNumber=record['doc_number'],
            selfieUrl=record['selfie_url'],
            docFrontUrl=record['doc_front_url'],
            docBackUrl=record['doc_back_url'],
            reviewer=record['reviewer'],
            reviewedAt=record['reviewed_at'],
            updatedAt=record['updated_at'],
            metaPath=blob_path
        )
