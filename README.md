# data-agent

一个基于 FastAPI 的数据问答服务：输入自然语言问题，经过检索和 SQL 生成后，返回流式结果（SSE）。

## 前置要求

- Python `>=3.12`
- `uv`
- Docker Desktop（或可用的 Docker daemon）

## 一次跑通（推荐按顺序执行）

### 步骤 1：启动依赖服务

```bash
docker compose up -d
```

依赖端口：

- MySQL：`localhost:3307`
- Qdrant：`localhost:6333`
- Elasticsearch：`localhost:9200`

---

### 步骤 2：配置 API Key

```bash
cp .env.example .env
```

编辑 `.env`：

```bash
DASHSCOPE_API_KEY=sk-你的key
```

---

### 步骤 3：确认应用配置

检查 `conf/app_config.yaml`：

- `db_meta.host: localhost`
- `db_meta.port: 3307`
- `db_dw.host: localhost`
- `db_dw.port: 3307`
- `qdrant.host: localhost`
- `qdrant.port: 6333`
- `es.host: localhost`
- `es.port: 9200`

---

### 步骤 4：安装依赖并启动应用

```bash
uv sync --python python3.12
uv run uvicorn application:app --host 127.0.0.1 --port 8000
```

访问：

- Playground：`http://127.0.0.1:8000/`
- Swagger：`http://127.0.0.1:8000/docs`

---

### 步骤 5：首次初始化元数据（必做）

新开一个终端执行：

```bash
uv run python -m app.scripts.build_meta_knowledge
```

出现 `元数据知识库构建完成` 即成功。

---

### 步骤 6：验证功能

```bash
curl -N -X POST "http://127.0.0.1:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"最近30天各省份销售额排名"}'
```

预期：

- 各节点 `progress` 都走到 `success`
- 最终返回 `result`，且包含省份+销售额数据

## 常见问题（只看这一节即可排错）

1. `Cannot connect to the Docker daemon`
   - 先启动 Docker Desktop，再执行 `docker compose up -d`

2. `address already in use`
   - 端口被占用，换端口或释放占用进程

3. `Did not find dashscope_api_key`
   - `.env` 未配置 `DASHSCOPE_API_KEY`

4. `Table 'dw.xxx' doesn't exist`
   - `dw` 样例表未导入，执行：
   ```bash
   docker exec -i data-agent-mysql mysql -uroot -proot1234 < docker/mysql/dw_seed.sql
   ```

5. `Duplicate entry ... for key ...`（重复初始化）
   - 清空 `meta` 表后再执行初始化：
   ```bash
   docker exec -i data-agent-mysql mysql -uroot -proot1234 -e "use meta; SET FOREIGN_KEY_CHECKS=0; TRUNCATE TABLE column_metric; TRUNCATE TABLE metric_info; TRUNCATE TABLE column_info; TRUNCATE TABLE table_info; SET FOREIGN_KEY_CHECKS=1;"
   uv run python -m app.scripts.build_meta_knowledge
   ```

