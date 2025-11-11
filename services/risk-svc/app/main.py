from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .schemas import EvaluationRequest, EvaluationResponse
from .service import RiskService

settings = get_settings()
app = FastAPI(title='risk-svc', version='0.1.0')
service = RiskService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/healthz')
def healthz() -> dict:
    return {'status': 'ok', 'service': settings.app_name}


@app.post('/risk/evaluations', response_model=EvaluationResponse)
def evaluate_risk(payload: EvaluationRequest) -> EvaluationResponse:
    return service.evaluate(payload)
