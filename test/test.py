import os
from zhipuai import ZhipuAI

client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY"))

# 尝试调用（方法名可能略有不同）
result = client.get_coding_plan_remains()  # 或者 client.query_coding_plan_remains()，根据实际方法名调整
print(result)
