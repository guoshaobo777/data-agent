# data-agent

一个基于 FastAPI 的数据问答服务：接收自然语言问题，经过检索和 SQL 生成流程，返回流式结果（SSE）。

## 环境要求

- Python `>=3.12`
- `uv`（推荐）
- Docker / Docker Compose（用于本地依赖服务）

## 1. 启动本地依赖服务（推荐）

项目已提供 `docker-compose.yml`，可一键启动：

```bash
cd data-agent
docker compose up -d
```

如果出现 `Cannot connect to the Docker daemon`，请先启动 Docker Desktop（或启动本机 Docker 服务）后再执行。

会启动以下服务：

- MySQL：`localhost:3307`
- Qdrant：`localhost:6333`
- Elasticsearch：`localhost:9200`

MySQL 初始化脚本已内置，会自动创建数据库：

- `meta`
- `dw`

如果你之前已经启动过 MySQL（卷里是旧数据），初始化脚本不会自动重跑，可手动执行：

```bash
docker exec -i data-agent-mysql mysql -uroot -proot1234 < docker/mysql/meta_seed.sql
docker exec -i data-agent-mysql mysql -uroot -proot1234 < docker/mysql/dw_seed.sql
```

## 2. 配置项目

### 2.1 配置 API Key

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env`，填入：

```bash
DASHSCOPE_API_KEY=sk-你的key
```

### 2.2 检查 `conf/app_config.yaml`

若使用本地 Docker，请确保以下配置为本地地址：

- `db_meta.host: localhost`
- `db_dw.host: localhost`
- `qdrant.host: localhost`
- `es.host: localhost`

默认端口建议保持：

- MySQL: `3307`
- Qdrant: `6333`
- Elasticsearch: `9200`

## 3. 安装依赖并启动应用

```bash
uv sync --python python3.12
uv run uvicorn application:app --host 0.0.0.0 --port 8000
```

## 4. 初始化元数据（首次必做）

首次启动后，执行一次元数据构建（会写入 MySQL / Qdrant / ES）：

```bash
uv run python -m app.scripts.build_meta_knowledge
```

如果你重复执行该命令，建议先清空 `meta` 库中的元数据表（避免主键重复）：

```bash
docker exec -i data-agent-mysql mysql -uroot -proot1234 -e "use meta; SET FOREIGN_KEY_CHECKS=0; TRUNCATE TABLE column_metric; TRUNCATE TABLE metric_info; TRUNCATE TABLE column_info; TRUNCATE TABLE table_info; SET FOREIGN_KEY_CHECKS=1;"
```

## 功能入口

- Playground：`http://127.0.0.1:8000/`
- Swagger 文档：`http://127.0.0.1:8000/docs`

核心接口：

- `POST /api/query`
- 请求体：

```json
{
  "query": "最近30天各省份销售额排名"
}
```

返回类型：`text/event-stream`（SSE）。

## 命令行调用示例

```bash
curl -N -X POST "http://127.0.0.1:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"最近30天各省份销售额排名"}'
```

## 常见问题

1. `Did not find dashscope_api_key`
   - 原因：未配置 `.env` 中的 `DASHSCOPE_API_KEY`
   - 解决：补充 `.env` 后重启应用

2. `index_not_found_exception: no such index [data-agent-value]`
   - 原因：未执行元数据初始化
   - 解决：执行 `uv run python -m app.scripts.build_meta_knowledge`

3. `address already in use`（8000 端口占用）
   - 解决方案 A：改端口（如 `--port 8001`）
   - 解决方案 B：释放占用端口后重启

4. `Access denied for user 'root'@'localhost'`
   - 原因：3306 上可能连到了你本机已有 MySQL（非 docker-compose 创建）或密码不一致
   - 解决方案 A：停止本机 MySQL，确保 `docker compose` 的 MySQL 成功占用 3306
   - 解决方案 B：本项目默认已改为 `3307`，如你继续自定义端口，请同步修改 `conf/app_config.yaml`

5. `Table 'dw.xxx' doesn't exist`
   - 原因：`dw` 业务表示例数据未初始化
   - 解决：执行 `docker/mysql/dw_seed.sql` 导入命令

6. `analyzer [ik_max_word] has not been configured`
   - 原因：使用的是标准 ES 镜像，未安装 IK 分词插件
   - 解决：项目已默认改为 `standard` 分词器，无需额外安装插件

