import re


CITATION_PATTERN = re.compile(r"\[C(\d+)\]", re.IGNORECASE)


def parse_citations(answer, chunks):
    """解析回答中的 Citation ID，并映射为去重后的来源。"""
    sources = []
    seen_sources = set()

    # 按回答中第一次出现的顺序处理 Citation ID。
    seen_citation_ids = set()
    for match in CITATION_PATTERN.finditer(answer):
        citation_number = int(match.group(1))
        if citation_number in seen_citation_ids:
            continue
        seen_citation_ids.add(citation_number)

        chunk_position = citation_number - 1
        if chunk_position < 0 or chunk_position >= len(chunks):
            continue

        chunk = chunks[chunk_position]
        source_key = (chunk["source"], chunk["page"])
        if source_key in seen_sources:
            continue

        seen_sources.add(source_key)
        sources.append({"file": chunk["source"], "page": chunk["page"]})

    # API 返回自然答案；Citation ID 已转换为结构化 sources。
    clean_answer = CITATION_PATTERN.sub("", answer)
    clean_answer = re.sub(r"[ \t]+([，。！？；：,.!?;:])", r"\1", clean_answer)
    clean_answer = re.sub(r"[ \t]{2,}", " ", clean_answer)
    clean_answer = re.sub(r"\n{3,}", "\n\n", clean_answer).strip()
    return clean_answer, sources
