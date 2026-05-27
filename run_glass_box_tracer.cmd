@echo off
python -m uvicorn scl_tracer_server:app --host 0.0.0.0 --port 8004 --timeout-keep-alive 3600
