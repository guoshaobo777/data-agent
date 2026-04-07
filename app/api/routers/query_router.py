from fastapi import APIRouter
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema
from app.services.query_service import QueryService

query_router = APIRouter()

PLAYGROUND_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Data Agent Playground</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; }
    h1 { margin-bottom: 12px; }
    #query { width: 100%; max-width: 900px; height: 88px; padding: 10px; box-sizing: border-box; }
    .row { margin-top: 12px; display: flex; gap: 8px; align-items: center; }
    button { padding: 8px 16px; cursor: pointer; }
    #status { color: #666; }
    #output {
      margin-top: 16px;
      background: #0f172a;
      color: #e2e8f0;
      border-radius: 8px;
      padding: 12px;
      min-height: 260px;
      max-width: 900px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 13px;
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <h1>Data Agent 功能体验</h1>
  <textarea id="query" placeholder="输入你的问题，例如：最近30天各省份销售额排名"></textarea>
  <div class="row">
    <button id="send">发送</button>
    <button id="clear">清空输出</button>
    <span id="status">就绪</span>
  </div>
  <div id="output"></div>

  <script>
    const queryEl = document.getElementById("query");
    const outputEl = document.getElementById("output");
    const statusEl = document.getElementById("status");
    const sendBtn = document.getElementById("send");
    const clearBtn = document.getElementById("clear");

    const appendLine = (text) => {
      outputEl.textContent += text + "\\n";
      outputEl.scrollTop = outputEl.scrollHeight;
    };

    clearBtn.addEventListener("click", () => {
      outputEl.textContent = "";
    });

    sendBtn.addEventListener("click", async () => {
      const query = queryEl.value.trim();
      if (!query) {
        statusEl.textContent = "请先输入问题";
        return;
      }

      statusEl.textContent = "请求中...";
      sendBtn.disabled = true;
      appendLine(">>> " + query);

      try {
        const res = await fetch("/api/query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query })
        });

        if (!res.ok || !res.body) {
          throw new Error(`HTTP ${res.status}`);
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const events = buffer.split("\\n\\n");
          buffer = events.pop() || "";

          for (const event of events) {
            const lines = event.split("\\n");
            for (const line of lines) {
              if (!line.startsWith("data:")) continue;
              const payload = line.slice(5).trim();
              appendLine(payload);
            }
          }
        }

        statusEl.textContent = "完成";
      } catch (err) {
        statusEl.textContent = "失败";
        appendLine("[error] " + String(err));
      } finally {
        sendBtn.disabled = false;
      }
    });
  </script>
</body>
</html>
"""


@query_router.get("/", response_class=HTMLResponse)
async def playground():
    return PLAYGROUND_HTML

@query_router.post("/api/query")
async def query(query: QuerySchema, query_service: QueryService=Depends(get_query_service)):
    return StreamingResponse(
        query_service.query(query.query), media_type="text/event-stream"
    )
