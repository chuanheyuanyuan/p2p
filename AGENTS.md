# Repository Guidelines

## Project Structure & Module Organization
- **Root layout**: domain documents (`PROGRESS.md`, `任务分解表.md`), shared config (`Taskfile.yml`), and DB artifacts (`*.db`).  
- **services/**: FastAPI microservices (e.g., `loan-svc`, `payment-svc`, `bff-mobile`). Each service contains `app/` source, `requirements.txt`, optional `README.md`, and `tests/`.  
- **apps/**: front-end and gateway scaffolds (`admin-web`, `bff-admin`, etc.).  
- **临时文件/** & docs folders record debugging scripts and requirements—update them whenever workflows change.

## Build, Test, and Development Commands
Common flow (run inside a service directory):
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port <port>
pytest -q
```
Use `Taskfile.yml` for canned tasks (`task run:loan-svc`, `task test:bff-mobile`, etc.). Database schema initializes automatically when `app/database.py` is imported.

## Coding Style & Naming Conventions
- Python code follows **PEP 8**, 4-space indentation, explicit imports. Prefer `typing.Optional` instead of `| None` (Python 3.9 target).  
- Keep modules small: `app/routers`, `app/services`, `app/schemas`, etc.  
- Use descriptive environment variables with service prefixes (e.g., `BFF_MOBILE_LOAN_BASE_URL`).  
- Format/lint using editors or `ruff` where available; retain ASCII unless files already contain localized text.

## Testing Guidelines
- Primary framework: **pytest** with `httpx.ASGITransport` for FastAPI services.  
- Place tests under `tests/` mirroring service modules, naming files `test_<module>.py`.  
- Run `pytest -q` before committing; integration tests may rely on stub clients, so mock downstream dependencies (`respx`, in-memory fakes). Aim to cover new routes and error paths.

## Commit & Pull Request Guidelines
- Commit messages use imperative style with optional scopes, e.g., `feat: add loan list API`, `fix(bff-mobile): handle payment failures`.  
- Each PR should describe **what** changed, **why**, associated ticket (T#), validation steps (commands run), and screenshots/log excerpts when UI or HTTP behavior changes.  
- Ensure `PROGRESS.md`, service `README.md`, and relevant docs reflect new capabilities; reviewers expect updated curl/http samples and testing notes.

## Security & Configuration Tips
- Store secrets in `.env` files per service (`BFF_MOBILE_JWT_SECRET`, `LOAN_SVC_BASE_URL`, etc.); never commit credentials.  
- API responses may include PII—mask logs (e.g., phone numbers) and enforce ownership checks (`userId` comparisons) when aggregating data across services.
