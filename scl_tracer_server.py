import asyncio
import json
from pathlib import Path

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI(title="SCL Tracer Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CHAT_WONDER_TRACE_URL = "http://127.0.0.1:8000/trace-stream"

_trace_queues: set = set()


async def _relay_from_chat_wonder():
    """Background task: subscribes to chat-wonder-v2-api's SSE stream and fans
    events out to all connected browser subscribers. Auto-reconnects on failure."""
    while True:
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", CHAT_WONDER_TRACE_URL) as response:
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        payload = line[6:]
                        for q in list(_trace_queues):
                            try:
                                q.put_nowait(payload)
                            except asyncio.QueueFull:
                                pass
        except Exception:
            await asyncio.sleep(3)  # wait before reconnecting


@app.on_event("startup")
async def startup():
    asyncio.create_task(_relay_from_chat_wonder())


@app.get("/trace-stream")
async def trace_stream():
    """SSE endpoint for browser — receives events relayed from chat-wonder-v2-api."""
    async def _generator():
        q: asyncio.Queue = asyncio.Queue(maxsize=200)
        _trace_queues.add(q)
        try:
            yield "data: {\"type\":\"connected\"}\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=25)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    yield "data: {\"type\":\"ping\"}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            _trace_queues.discard(q)
    return StreamingResponse(
        _generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


@app.get("/")
async def serve_tracer():
    """Serves the glass-box tracer HTML — open http://127.0.0.1:8004 in browser."""
    html_path = Path(__file__).parent / "run_glass_box_tracer.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))
