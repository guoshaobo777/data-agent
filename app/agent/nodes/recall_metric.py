import asyncio

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from loguru import logger

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.agent.test_suit import test_node_framework
from app.entities.metric_info import MetricInfo
from app.prompt.prompt_loader import load_prompt
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回指标", "status": "running"})

    query = state['query']
    keywords = state['keywords']

    embedding_client = runtime.context['embedding_client']
    metric_qdrant_repository: MetricQdrantRepository = runtime.context['metric_qdrant_repository']

    try:
        # 使用 LLM 扩展关键词
        prompt = PromptTemplate(
            template=load_prompt("extend_keywords_for_metric_recall"),
            input_variables=["query"]
        )
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser
        result = await chain.ainvoke({"query": query})

        # 使用扩展后的关键词 召回 字段信息
        retrieved_metrics_map: dict[str, MetricInfo] = {}
        keywords = list(set(keywords + result))
        logger.info(f"召回指标信息扩展关键词: {keywords}")
        for keyword in keywords:
            # 转换成向量
            embeddings = await embedding_client.aembed_query(keyword)
            # 通过向量搜索语义相近的字段信息
            payloads: list[MetricInfo] = await metric_qdrant_repository.search(embeddings)
            for payload in payloads:
                metric_id = payload.id
                if metric_id not in retrieved_metrics_map:
                    retrieved_metrics_map[metric_id] = payload
        retrieved_metrics_ids = list(retrieved_metrics_map.keys())
        retrieved_metrics = list(retrieved_metrics_map.values())

        writer({"type": "progress", "step": "召回指标", "status": "success"})
        logger.info(f"召回指标信息: {retrieved_metrics_ids}")
        return {"retrieved_metrics": retrieved_metrics}
    except Exception as e:
        writer({"type": "progress", "step": "召回指标", "status": "error"})
        logger.error(f"召回指标失败: {str(e)}")
        raise e

if __name__ == '__main__':
    async def test_recall_metric():
        state = {
            "query": "统计去年各个地区的销售额",
            "keywords": ["统计", "地区", "销售额", "统计去年各个地区的销售额"]
        }
        await test_node_framework(state, recall_metric)
    asyncio.run(test_recall_metric())

