@echo off
python --version 2>&1 | findstr /r "Python 3\.10\." > nul
if errorlevel 1 (echo Error: Python 3.10.x required & exit /b 1)

set SCL_MAX_TOKENS=4096
set SCL_MIN_CALL_INTERVAL=1.5

rem === 실험 1: basic_functions만 사용 (위 두 줄 comment out) ===
set SCL_RAG_ENABLED=True
set SCL_RAG_TOP_N=5

rem === 실험 2: priority_banking 세트 ===
rem set SCL_RAG_ENABLED=False
rem set SCL_CUSTOM_PACKAGE_PATHS=%~dp0examples\priority_banking\priority_banking.zip
rem set SCL_CUSTOM_REGULATIONS_PATHS=%~dp0examples\priority_banking\priority_banking.txt

set SCL_LLM_PROVIDER=openai
set SCL_MODEL=chat-latest
rem set SCL_MODEL=gpt-5.5
rem set OPENAI_API_KEY=...

rem set SCL_LLM_PROVIDER=anthropic
rem set SCL_MODEL=claude-sonnet-4-6
rem set SCL_MODEL=claude-opus-4-7
rem rem set ANTHROPIC_API_KEY=...

rem set SCL_LLM_PROVIDER=gemini_openai
rem set SCL_MODEL=gemini-3-flash-preview
rem set SCL_MODEL=gemini-2.5-pro
rem set GEMINI_API_KEY=...

rem set SCL_LLM_PROVIDER=deepseek
rem set SCL_MODEL=deepseek-v4-flash
rem set SCL_MODEL=deepseek-v4-pro
rem set DEEPSEEK_API_KEY=...

rem set SCL_LLM_PROVIDER=qwen
rem set SCL_MODEL=
rem set LOCAL_LLM_HOST=varworld.ai
rem set LOCAL_LLM_PORT=8700
rem set LOCAL_LLM_API_KEY=EMPTY

rem set SCL_LLM_PROVIDER=exaone
rem set SCL_MODEL=
rem set LOCAL_LLM_HOST=varworld.ai
rem set LOCAL_LLM_PORT=8710
rem set LOCAL_LLM_API_KEY=EMPTY

python -m uvicorn scl_api_server:app --host 0.0.0.0 --port 8003 --timeout-keep-alive 3600 --ws-ping-interval 20 --ws-ping-timeout 60

