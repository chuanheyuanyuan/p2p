# 下一位工程师提示词

你接手的是一个 FastAPI 微服务集合的本地开发环境，核心服务（loan/payment/ledger/collection）已全部切换为 SQLite 持久化，相关 DB 文件位于各自服务根目录（`loan.db`、`payment.db`、`ledger.db`、`collection.db`）。当前任务重点是继续完善 T13 及以后的需求，保持以下约定：

1. **环境与运行**
   - 每个服务独立 `python3 -m venv .venv` 并使用 `uvicorn app.main:app --reload --port <端口>`。
   - 启动服务前如果需要建表，只需 import 对应 `app/database.py`（例如运行 `uvicorn`）即可。
   - 样例调用、curl、调试流程记录在 `临时文件` 与各服务 README。

2. **持久化现状**
   - `loan-svc`: 草稿、还款 schedule 写入 `loan.db`；`LoanBillingService` 负责扣减逻辑。
   - `payment-svc`: 放款/还款记录写入 `payment.db`，`txnRef` 唯一；`POST /payments/repayments` 会回调 loan-svc。
   - `ledger-svc`: `POST /ledger/entries` 写入 `ledger.db`，已处理 Decimal 序列化。
   - `collection-svc`: `/collections/*` 与 `/events/*` 操作落在 `collection.db`，事件日志打印在控制台。

3. **继续开发建议**
   - 参考 `PROGRESS.md` 的任务 T13 之后条目，按顺序推进；若需新表/字段，扩展现有 `database.py` 并考虑迁移策略。
   - 优先保持接口契约、日志与文档同步（`README`、`临时文件`、`PROGRESS.md`）。
   - 若要切换到外部 DB/消息队列，可先抽象 repository 层，再实现新后端。

4. **调试快速路径**
   - `临时文件` 中提供了 loan → payment → ledger → collection 的端到端验证脚本，建议接手后先跑一遍，确认 SQLite 数据正常写入。
   - 如遇端口占用，使用 `lsof -i :<port>` + `kill <pid>` 清理旧进程。

你现在接管 p2p 放贷平台后端仓库。请严格遵循以下规则：
【最重要的规则说三遍！！】：所有关于git的操作都需要得到确认后再执行！！所有关于git的操作都需要得到确认后再执行！！所有关于git的操作都需要得到确认后再执行！！
1. 所有开发都使用 git worktree 并行分支：从 main 创建 feature/<任务号> 分支，并通过
   git worktree add ../p2p-<任务号> feature/<任务号>
   进入新目录开发，提交完成后再合并回 main。
2. 任何改动都要在对应 worktree 目录下完成，不能在主仓库直接修改。
3. 开发顺序按 PROGRESS.md 的任务编号继续推进，完成后更新 PROGRESS.md、临时文件以及 README。
4. 运行、调试命令参考 临时文件 与各服务 README，必要时将验证步骤写回临时文件。
5. 交接时写清楚当前分支、worktree 路径、剩余 TODO，方便下一位工程师继续。


请沿用上述约定继续交付，并在有新成果后更新 `PROGRESS.md`/`README`/`临时文件` 以便下一位工程师快速接手。***
