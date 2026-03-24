import asyncio

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from loguru import logger

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.agent.test_suit import test_node_framework
from app.entities.column_info import ColumnInfo
from app.prompt.prompt_loader import load_prompt


async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回字段", "status": "running"})

    query = state['query']
    keywords = state['keywords']

    embedding_client = runtime.context['embedding_client']
    column_qdrant_repository = runtime.context['column_qdrant_repository']

    try:
        # 使用 LLM 扩展关键词
        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_column_recall"),
            input_variables=["query"]
        )
        output_parser = JsonOutputParser()

        chain = prompt | llm | output_parser

        result = await chain.ainvoke({"query": query})
        # 使用扩展后的关键词 召回 字段信息
        retrieved_columns_map: dict[str, ColumnInfo] = {}
        keywords = list(set(keywords + result))
        logger.info(f"召回字段信息扩展关键词: {keywords}")
        for keyword in keywords:
            # 转换成向量
            embedding_vector = await embedding_client.aembed_query(keyword)
            # 通过向量搜索语义相近的字段信息
            payloads: list[ColumnInfo] = await column_qdrant_repository.search(embedding_vector)
            for payload in payloads:
                column_id = payload.id  # 表名.字段名
                if column_id not in retrieved_columns_map:
                    retrieved_columns_map[column_id] = payload

        retrieved_column_ids = list(retrieved_columns_map.keys())
        retrieved_columns = list(retrieved_columns_map.values())


        writer({"type": "progress", "step": "召回字段", "status": "success"})
        logger.info(f"召回字段信息: {retrieved_column_ids}")
        return {"retrieved_columns": retrieved_columns}
    except Exception as e:
        writer({"type": "progress", "step": "召回字段", "status": "error"})
        logger.error(f"召回字段失败: {str(e)}")
        raise e

if __name__ == '__main__':
    async def test_recall_column():
        state = {
            "query": "统计去年各个地区的销售额",
            "keywords": ["统计", "地区", "销售额", "统计去年各个地区的销售额"]
        }
        await test_node_framework(state, recall_column)
    asyncio.run(test_recall_column())
