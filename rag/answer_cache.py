import json
import os
import tempfile
from datetime import date
from pathlib import Path


DEFAULT_CACHE_PATH = "answer_cache.json"
CITATION_CACHE_VERSION = 2


def _load_cache(cache_path):
    """读取缓存文件；文件不存在时返回空字典。"""
    cache_path = Path(cache_path)

    if not cache_path.exists():
        return {}

    with open(cache_path, "r", encoding="utf-8") as file:
        return json.load(file)


def clear_cache(cache_path=DEFAULT_CACHE_PATH):
    """原子地清空答案缓存，并始终保留合法的 JSON 文件。"""
    cache_path = Path(cache_path)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=cache_path.parent,
            prefix=f".{cache_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump({}, temporary_file, ensure_ascii=False, indent=4)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, cache_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def get_cached_result(question, cache_path=DEFAULT_CACHE_PATH):
    """读取包含 answer 和 sources 的 Citation V2 缓存。"""
    cache = _load_cache(cache_path)
    cached_item = cache.get(question)

    if cached_item is None:
        return None

    # 旧缓存只有 answer，无法证明来源；将其视为未命中并重新生成。
    if cached_item.get("citation_version") != CITATION_CACHE_VERSION:
        return None

    answer = cached_item.get("answer")
    sources = cached_item.get("sources")
    if not isinstance(answer, str) or not isinstance(sources, list):
        return None

    return {"answer": answer, "sources": sources}


def save_result(question, answer, sources, cache_path=DEFAULT_CACHE_PATH):
    """将自然答案与结构化来源一起保存。"""
    cache_path = Path(cache_path)
    cache = _load_cache(cache_path)

    cache[question] = {
        "answer": answer,
        "sources": sources,
        "citation_version": CITATION_CACHE_VERSION,
        "time": date.today().isoformat(),
    }

    with open(cache_path, "w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=4)
