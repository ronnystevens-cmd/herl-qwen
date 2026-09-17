#!/usr/bin/env python3
# Merge HERL-Qwen LoRA in de 4-bit base -> Q8_0 GGUF (bewezen HERL-Gemma route)
import time
from unsloth import FastLanguageModel
from peft import PeftModel

BASE = "/home/flitsken/models/qwen3.8-27b-hf"
ADAPTER = "/home/flitsken/herl-qwen-lora-v1"
OUT_GGUF = "/home/flitsken/herl-qwen-gguf"
t0 = time.time()

print("=== 1. Laad base (4-bit NF4) ===", flush=True)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=BASE, max_seq_length=2048, dtype=None,
    load_in_4bit=True, device_map={"": 0},
)

print("=== 2. Laad HERL-adapter ===", flush=True)
model = PeftModel.from_pretrained(model, ADAPTER)

print("=== 3. Merge + Q8_0 GGUF-export ===", flush=True)
try:
    # Directe export: unsloth verwerkt de LoRA in de gewichten (geheugenvriendelijk)
    model.save_pretrained_gguf(OUT_GGUF, tokenizer=tokenizer, quantization_method="q8_0")
except Exception as e:
    print(f"directe export mislukt ({e}); probeer merge_and_unload eerst", flush=True)
    model = model.merge_and_unload()
    model.save_pretrained_gguf(OUT_GGUF, tokenizer=tokenizer, quantization_method="q8_0")

print(f"Q8_GGUF KLAAR in {time.time()-t0:.0f}s -> {OUT_GGUF}", flush=True)
