#!/usr/bin/env bash
# 考研英语智学Agent 一键启动脚本
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -x .venv/bin/streamlit ]; then
  echo "==> 首次运行，创建虚拟环境并安装依赖..."
  python3 -m venv .venv
  .venv/bin/pip install --upgrade pip
  .venv/bin/pip install -r kaoyan_agent/requirements.txt
fi

PORT="${PORT:-8501}"
echo "==> 启动考研英语智学Agent: http://localhost:${PORT}"
cd kaoyan_agent
exec ../.venv/bin/streamlit run app.py \
  --server.port "${PORT}" \
  --server.address 0.0.0.0 \
  --server.headless true \
  --browser.gatherUsageStats false
