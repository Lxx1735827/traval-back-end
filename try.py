from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
#星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = 'f5f377c0'
SPARKAI_API_SECRET = 'YjFiNWZmYTQwMGMyZDZhOGIwMzk0NDYw'
SPARKAI_API_KEY = '3d7cdb75e47c594d01a98d691b950aa2'
#星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'generalv3.5'

def semantic_split(key: str):
    spark = ChatSparkLLM(
        spark_api_url=SPARKAI_URL,
        spark_app_id=SPARKAI_APP_ID,
        spark_api_key=SPARKAI_API_KEY,
        spark_api_secret=SPARKAI_API_SECRET,
        spark_llm_domain=SPARKAI_DOMAIN,
        streaming=False,
    )
    messages = [
        ChatMessage(role="system",
                    content="你是一个语义分析助手，专注于将中文短语拆分成有意义的最小单元，保留核心名词，并尽可能涵盖上下层次的含义。"),
        ChatMessage(
            role="user",
            content=f"将搜索词'{key}'拆分成有意义的最小单元，保留核心名词或短语，并尽量涵盖整体及子层次的含义。"
                    f"输出格式为：'keywords: xxx, xxx, xxx'。例如："
                    f"1. '成都大熊猫基地'拆分为'成都, 熊猫, 基地'；"
                    f"2. '四川大学江安校区'拆分为'四川大学, 江安校区, 四川, 大学, 江安'。"
        )
    ]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    # 获取包含 city 和 keywords 的文本
    text = a.generations[0][0].text  # 从数据中提取文本
    keywords = text.strip("'").replace('keywords:', '').strip()
    print(f"Keywords:{keywords}")
    result = [item.strip() for item in keywords.split(',')]
    return result

if __name__ == "__main__":
    semantic_split("成都大熊猫基地")
