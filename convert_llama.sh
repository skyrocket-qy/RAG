#!/usr/bin/env bash
set -e

# Define key paths

# 1. Clone llama.cpp if it doesn't exist
if [ ! -d "$HOME/llama.cpp" ]; then
  echo "📥 Cloning llama.cpp..."
  git clone https://github.com/ggerganov/llama.cpp.git "$HOME/llama.cpp"
fi

cd "$HOME/llama.cpp"

# 2. Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install "torch==2.2.2" --index-url https://download.pytorch.org/whl/cpu
pip install mistral-common sentencepiece tqdm numpy

# 3. Build the llama.cpp binaries
echo "🔨 Building llama.cpp..."
mkdir -p build
cd build
cmake .. -DLLAMA_METAL=OFF
cmake --build . --config Release
cd .. # Return to the llama.cpp root directory

OUTPUT_FILE="/Users/qy/Llama.gguf"
# 5. Convert the model to GGUF format
echo "🔄 Converting model to GGUF ..."
python3 ~/llama.cpp/convert_hf_to_gguf.py \
  --outfile "$OUTPUT_FILE" \
  --outtype tq2_0 \
  ~/Llama-3.2-1B

echo "✅ Conversion complete: $OUTPUT_FILE"

# 6. Run a quick test prompt
echo "🚀 Running a test prompt..."
./build/bin/llama-cli -m "$OUTPUT_FILE" -p "Hello! Who are you?" \
  -n 10 --n-gpu-layers 0 --verbose   --threads 8 \
  --no-mmap