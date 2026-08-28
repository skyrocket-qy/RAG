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
pip install mistral-common sentencepiece tqdm numpy
pip install -r requirements.txt

# 3. Build the llama.cpp binaries
echo "🔨 Building llama.cpp..."
mkdir -p build
cd build
cmake .. -DGGML_USE_BUILTIN_TRANSFORMERS=ON -DCMAKE_ASM_COMPILER=/home/linuxbrew/.linuxbrew/opt/llvm/bin/clang -DCMAKE_LINKER=/home/linuxbrew/.linuxbrew/opt/llvm/bin/clang -DOpenMP_ROOT=/home/linuxbrew/.linuxbrew/Cellar/llvm/21.1.0 -DCMAKE_EXE_LINKER_FLAGS="-Wl,-rpath,/home/linuxbrew/.linuxbrew/Cellar/llvm/21.1.0/lib/x86_64-unknown-linux-gnu" -DCMAKE_C_FLAGS="-fopenmp=libomp" -DCMAKE_CXX_FLAGS="-fopenmp=libomp" -DCMAKE_SHARED_LINKER_FLAGS="-L/home/linuxbrew/.linuxbrew/Cellar/llvm/21.1.0/lib/x86_64-unknown-linux-gnu -lomp"
cmake --build . --config Release
cd .. # Return to the llama.cpp root directory

OUTPUT_FILE="/home/qy/Llama.gguf"
# 5. Convert the model to GGUF format
#"f32", "f16", "bf16", "q8_0", "tq1_0", "tq2_0", "auto"
echo "🔄 Converting model to GGUF ..."
python3 ~/llama.cpp/convert_hf_to_gguf.py \
  --outfile "$OUTPUT_FILE" \
  --outtype f32 \
  ~/Llama-3.1-8B

echo "✅ Conversion complete: $OUTPUT_FILE"

# 6. Run a quick test prompt
echo "🚀 Running a test prompt..."
env LD_LIBRARY_PATH="/home/linuxbrew/.linuxbrew/Cellar/llvm/21.1.0/lib/x86_64-unknown-linux-gnu:$LD_LIBRARY_PATH" ./build/bin/llama-cli -m "$OUTPUT_FILE" -p "Hello! Who are you?" \
  -n 24  --threads 8 \


