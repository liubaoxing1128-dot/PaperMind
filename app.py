from rag.answer_cache import get_cached_result, save_result
from rag.citation import parse_citations
from rag.llm import generate_answer
from rag.retriever import retrieve_top_chunks


def ask(question):
    """执行 Citation V2 RAG 流程，返回答案及 LLM 明确引用的来源。"""
    cached_result = get_cached_result(question)
    if cached_result is not None:
        return cached_result

    top3_chunks = retrieve_top_chunks(question, top_k=3)
    raw_answer = generate_answer(top3_chunks, question)
    answer, sources = parse_citations(raw_answer, top3_chunks)
    result = {"answer": answer, "sources": sources}
    save_result(question, answer, sources)
    return result


def main():
    """运行命令行版本的 RAG 问答流程。"""
    try:
        question = "Transformer是哪一年提出的？"
        result = ask(question)

        print(result["answer"])
        print("\n来源：")
        for source in result["sources"]:
            page = source["page"] if source["page"] is not None else "N/A"
            print(source["file"])
            print(f"Page {page}")
    except Exception as error:
        print(f"程序运行失败：{error}")


if __name__ == "__main__":
    main()
