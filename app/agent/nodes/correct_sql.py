import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime
from loguru import logger

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.prompt.prompt_loader import load_prompt


async def correct_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "修正SQL", "status": "running"})

    sql = state['sql']
    error = state['error']
    query = state['query']
    table_infos = state['table_infos']
    metric_infos = state['metric_infos']
    date_info = state['date_info']
    db_info = state['db_info']

    try:
        prompt = PromptTemplate(
            template=load_prompt("correct_sql"),
            input_variables=["query", "sql", "error", "table_infos", "metric_infos", "date_info", "db_info"]
        )
        output_parser = JsonOutputParser()
        chain = prompt | llm | output_parser
        result = await chain.ainvoke({
            "query": query,
            "sql": sql,
            "error": error,
            # 将复杂的嵌套数据结构转换为 yaml 格式字符串
            "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=True),
            "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=True),
            "date_info": yaml.dump(date_info, allow_unicode=True, sort_keys=True),
            "db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=True)
        })
        writer({"type": "progress", "step": "修正SQL", "status": "success"})
        logger.info(f"修正后的SQL: {result}")
        return {"sql": result}
    except Exception as e:
        writer({"type": "progress", "step": "修正SQL", "status": "error"})
        logger.error(f"修正SQL失败: {str(e)}")
        raise e
