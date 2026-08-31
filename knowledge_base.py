from rag.knowledge_base import main, update_knowledge_base


def sync():
    """同步 data 目录与持久化知识库存储。"""
    return update_knowledge_base()


if __name__ == "__main__":
    main()
