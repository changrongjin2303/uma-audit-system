# 仓库指南

## 项目结构与模块组织
- `backend/`（FastAPI）：业务代码位于 `app/`（`api/`、`models/`、`schemas/`、`services/`），数据库迁移在 `migrations/`，入口为 `main.py`。
- `frontend/`（Vue 3 + Vite）：源码在 `src/`（`components/`、`views/`、`store/`、`router/`），配置在 `vite.config.js`。
- 编排：`docker-compose.yml`、`docker/`，以及辅助脚本 `start.sh`、`start-local.sh`、`start-hybrid.sh`。
- 文档与资产：`docs/`、`reports/`、`database/`、`scripts/`。根目录工具：`test_report_api.py`、`test_report_generation.py`。

## 构建、测试与开发命令
- 全栈（Docker）：`docker-compose up -d --build`（停止：`docker-compose down`）。快速启动：`./start.sh`。
- 本地后端：`cd backend && pip install -r requirements.txt && python -m uvicorn main:app --reload --port 8000`。
- 仅本地数据库：`./start-local.sh`（启动 Postgres 与 Redis 供本地开发）。
- 后端测试：`cd backend && pytest -q` 或 `python run_tests.py`（支持标记；见“测试指南”）。
- 前端开发：`cd frontend && npm install && npm run dev`（构建：`npm run build`，代码检查：`npm run lint`，格式化：`npm run format`，单元测试：`npm run test:unit`）。
- 迁移（可选）：`cd backend && alembic revision -m "feat: ..." --autogenerate && alembic upgrade head`。

## 代码风格与命名约定
- Python：4 空格缩进，新代码需添加类型注解。使用 `black .` 与 `isort .` 格式化；使用 `flake8` 静态检查。文件使用 `snake_case.py`；类名 `PascalCase`；函数/变量 `snake_case`。API 路由置于 `app/api/<domain>.py`；Pydantic 模型置于 `app/schemas/`。
- 前端：ESLint + Prettier（2 空格缩进）。Vue SFC 文件名 `PascalCase.vue`；组件放在 `src/components/`，视图放在 `src/views/`，Pinia 仓库放在 `src/store/`（文件 camelCase，如 `user.js`）。可复用逻辑优先写为 composables，命名为 `useXxx.ts/js`，存放于 `src/utils`（或 `src/composables`）。

## 测试指南
- 后端（pytest）：测试位于 `backend/tests`，命名为 `test_*.py`。常用命令：`pytest -m "not slow"`、`pytest -m integration`。异步测试使用 `pytest-asyncio`（见 `pytest.ini`）。运行前确保 DB/Redis 已启动（可用 `./start-local.sh`）。
- 前端（Vitest）：将测试放在 `frontend/tests` 或与代码同级为 `*.spec.ts|*.test.ts`；运行 `npm run test:unit`。

## 提交与 Pull Request 指南
- 使用 Conventional Commits：`feat(api): add report preview endpoint`、`fix(ui): correct chart legend`、`chore: update deps`。
- PR 需包含：清晰的描述与范围、关联的 Issue、复现步骤、UI 变更前后截图，以及测试/代码检查通过的证据。

## 安全与配置提示
- 不要提交任何密钥；使用 `.env` 与 `backend/.env`。生产环境请将 `DEBUG=false` 并收紧 CORS。配置 `DATABASE_URL`、`REDIS_URL`，以及可选的 `OPENAI_API_KEY`/`DASHSCOPE_API_KEY`。
