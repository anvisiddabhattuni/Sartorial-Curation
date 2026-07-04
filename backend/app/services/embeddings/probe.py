"""Subprocess probe for CLIP checkpoints.

On this machine the FashionCLIP text tower can die with SIGBUS (a hard
process crash, not a catchable exception) on some torch/macOS combinations.
Probing in a throwaway subprocess lets the factory reject a broken checkpoint
without taking the API server down with it."""

import logging
import subprocess
import sys

logger = logging.getLogger("muse.embeddings")

_PROBE_SCRIPT = """
import sys
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

model_id = sys.argv[1]
m = CLIPModel.from_pretrained(model_id)
m.eval()
p = CLIPProcessor.from_pretrained(model_id)
img = Image.new("RGB", (224, 224), (180, 170, 160))
with torch.no_grad():
    fi = m.get_image_features(**p(images=[img], return_tensors="pt"))
    ft = m.get_text_features(**p(
        text=["beige linen blazer"], return_tensors="pt",
        padding=True, truncation=True, max_length=77,
    ))
if torch.isnan(fi).any() or torch.isnan(ft).any():
    sys.exit(3)
print("PROBE_OK")
"""


_REPAIR_SCRIPT = """
import sys
from transformers import CLIPModel, CLIPProcessor

src, dst = sys.argv[1], sys.argv[2]
m = CLIPModel.from_pretrained(src, low_cpu_mem_usage=False)
sd = {k: v.detach().clone().contiguous() for k, v in m.state_dict().items()}
fresh = CLIPModel(m.config)
fresh.load_state_dict(sd)
fresh.save_pretrained(dst, safe_serialization=True)
CLIPProcessor.from_pretrained(src).save_pretrained(dst)
print("REPAIR_OK")
"""


def repair_clip_model(model_id: str, dest_dir: str, timeout: int = 600) -> bool:
    """Rewrite a checkpoint as fresh safetensors. Fixes SIGBUS-on-forward we
    hit with the original FashionCLIP pickle checkpoint on this machine
    (loading is fine; only inference on the mmap'd weights crashes)."""
    logger.info("Attempting checkpoint repair: %s -> %s", model_id, dest_dir)
    try:
        result = subprocess.run(
            [sys.executable, "-c", _REPAIR_SCRIPT, model_id, dest_dir],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        logger.warning("Repair of %s timed out", model_id)
        return False
    ok = result.returncode == 0 and "REPAIR_OK" in result.stdout
    if not ok:
        logger.warning("Repair of %s failed: %s", model_id, (result.stderr or "").strip()[-500:])
    return ok


def probe_clip_model(model_id: str, timeout: int = 240) -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-c", _PROBE_SCRIPT, model_id],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        logger.warning("Probe of %s timed out", model_id)
        return False
    ok = result.returncode == 0 and "PROBE_OK" in result.stdout
    if not ok:
        logger.warning(
            "Probe of %s failed (exit %s): %s",
            model_id,
            result.returncode,
            (result.stderr or "").strip().splitlines()[-1:] or "no stderr",
        )
    return ok
