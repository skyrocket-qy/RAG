#!/usr/bin/env bash
set -e

# 1. Clone llama.cpp into your home directory if it doesn't already exist
if [ ! -d "$HOME/llama.cpp" ]; then
  git clone https://github.com/ggerganov/llama.cpp.git "$HOME/llama.cpp"
fi

cd "$HOME/llama.cpp"
# pip install -r requirements.txt
pip install "torch==2.2.2" --index-url https://download.pytorch.org/whl/cpu
pip install mistral-common sentencepiece tqdm numpy
# 2. Build the binaries with CMake
mkdir -p build
cd build
cmake ..
cmake --build . --config Release

# 3. Find the conversion script in the repo root
cd ..
if [ -f "convert_hf_to_gguf.py" ]; then
  CONVERT_SCRIPT="convert_hf_to_gguf.py"
elif [ -f "convert.py" ]; then
  CONVERT_SCRIPT="convert.py"
else
  echo "❌ No convert script found in $HOME/llama.cpp"
  exit 1
fi

# 4. Convert your model to GGUF (quantized to q4_k_m)
INPUT_DIR="$HOME/.llama/checkpoints/Llama3.1-8B"
OUTPUT_FILE="$HOME/Llama3.1-8B.Q4_K_M.gguf"

python3 ~/llama.cpp/convert_hf_to_gguf.py \
  --outfile /Users/qy/Llama3.1-8B.Q4_K_M.gguf \
  --outtype q8_0 \
  /Users/qy/.llama/checkpoints/Llama3.1-8B

echo "✅ Conversion complete: $OUTPUT_FILE"

# 5. Run a quick test prompt (binary now in build/bin)
./build/bin/llama-cli -m "$OUTPUT_FILE" -p "Hello! Who are you?"
