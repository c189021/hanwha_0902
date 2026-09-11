from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-5-mini",
    input="API 키 연결 테스트입니다. '정상 연결' 이라고만 답해주세요."
)

print(response.output_text)