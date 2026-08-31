from openai import OpenAI

from config import BASE_URL, DEEPSEEK_API_KEY, DEEPSEEK_MODEL


def build_prompt(chunks, question):
    """为 Chunk 标注 Citation ID，并构造要求精确引用的 Prompt。"""
    context_blocks = []
    for position, chunk in enumerate(chunks, start=1):
        page = chunk["page"] if chunk["page"] is not None else "null"
        context_blocks.append(
            f"[C{position}]\n"
            f"source: {chunk['source']}\n"
            f"page: {page}\n"
            f"text: {chunk['text']}"
        )
    context = "\n\n".join(context_blocks)

    return f"""你是一名AI助手，请严格遵守以下规则：
1. 只能根据提供的知识 Chunk 回答问题。
2. 回答中必须在相关陈述后标注真正支持该陈述的 Citation ID，例如：[C1]。
3. 不要引用没有真正支撑答案的 Chunk。
4. 如果资料不足，请明确说明资料不足，不要编造答案，也不要添加无依据的 Citation ID。

知识：
{context}

问题：
{question}

回答："""


def generate_answer(chunks, question):
    """将 Prompt 发送给 DeepSeek，并返回最终回答。"""
    if not DEEPSEEK_API_KEY:
        raise ValueError("请先在 .env 文件中配置 DEEPSEEK_API_KEY")

    prompt = build_prompt(chunks, question)
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=BASE_URL)

    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
