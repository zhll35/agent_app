#!/bin/bash
# 启动调试模式的后端服务

echo "🚀 启动调试模式..."
echo "================================"

# 设置 PYTHONPATH
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

# 设置日志级别为 DEBUG
export LOG_LEVEL=DEBUG

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "请创建 .env 文件并配置以下变量："
    echo "  OPENAI_API_KEY=your_api_key"
    echo "  OPENAI_BASE_URL=https://api.apiyi.com/v1"
    echo "  OPENAI_MODEL_NAME=gpt-4-turbo"
    exit 1
fi

echo "✅ 环境变量已设置"
echo "   PYTHONPATH=${PYTHONPATH}"
echo "   LOG_LEVEL=${LOG_LEVEL}"
echo ""

# 启动服务
echo "🔧 启动 FastAPI 服务器 (调试模式)..."
echo "   地址: http://localhost:8000"
echo "   文档: http://localhost:8000/docs"
echo ""
echo "💡 提示："
echo "   - 使用 Ctrl+C 停止服务"
echo "   - 代码修改会自动重载 (--reload)"
echo "   - 查看详细日志输出"
echo ""
echo "================================"
echo ""

# 使用 uvicorn 启动，开启 reload 和详细日志
uvicorn agent_app.runtime.server:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level debug \
    --access-log

