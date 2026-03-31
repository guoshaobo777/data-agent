import uuid

from fastapi import FastAPI
from starlette.requests import Request

from app.api.routers.query_router import query_router
from app.core.context import request_id_ctx_var
from app.core.lifespan import lifespan

app = FastAPI(lifespan=lifespan)
app.include_router(query_router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # 调用路径函数之前
    request_id_ctx_var.set(uuid.uuid4())
    # 调用路径函数
    response = await call_next(request)
    # 调用路径函数之后
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
