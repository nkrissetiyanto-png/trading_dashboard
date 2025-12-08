# components/ai_memory.py

from collections import deque
import time

# Simpan max 200 data
AI_HISTORY = deque(maxlen=200)

def save_ai_result(result):
    AI_HISTORY.append({
        "time": time.time(),
        "direction": result["direction"],
        "confidence": result["confidence"],
        "prob_up": result["prob_up"],
        "prob_down": result["prob_down"]
    })

def get_history():
    return list(AI_HISTORY)

