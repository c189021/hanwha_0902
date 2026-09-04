title = "AI 서비스 백엔드 프로그래밍 실무"

topics = ["파이썬 기본 문법", "클래스", "데코레이터", "예외 처리", "로깅"]
hours = 8

print(title)

for x in range(32):
	print("=", end="")
	
print("")

for topic in topics:
	print(f"{topic}, 시간:{hours}")
	print(topic, hours, sep=", 시간:")