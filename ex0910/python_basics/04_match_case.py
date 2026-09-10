# =============================================================================
# 04_match_case.py  -  match / case (구조적 패턴 매칭, Python 3.10+)
# =============================================================================
# 하나의 값을 여러 "패턴"과 차례로 대조해서, 처음 맞는 case 블록을 실행한다.
# 다른 언어의 switch 문과 비슷하지만 훨씬 강력하다.
#
#   match 검사할_값:
#       case 패턴1:
#           ...
#       case 패턴2:
#           ...
#       case _:            # _ 는 "그 외 전부" (와일드카드). default 역할.
#           ...
#
# case 를 위에서부터 순서대로 검사하므로, 좁은(구체적인) 패턴을 위에 둔다.
# =============================================================================

# -----------------------------------------------------------------------------
# 1) 값 매칭 + case _ (그 외 처리)
# -----------------------------------------------------------------------------
def http_message(status: int) -> str:
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Server Error"
        case _:                     # 위 어느 것도 아니면 여기로
            return f"알 수 없는 상태 코드: {status}"


print(http_message(200))
print(http_message(404))
print(http_message(302))            # -> 알 수 없는 상태 코드: 302


# -----------------------------------------------------------------------------
# 2) 여러 값을 한 case 에서 ( | 로 OR )
# -----------------------------------------------------------------------------
def category(status: int) -> str:
    match status:
        case 200 | 201 | 204:
            return "성공"
        case 400 | 401 | 403 | 404 | 422:
            return "클라이언트 오류"
        case 500 | 502 | 503:
            return "서버 오류"
        case _:
            return "기타"


print(category(422))                # -> 클라이언트 오류


# -----------------------------------------------------------------------------
# 3) "데이터 타입이 달라도 처리"  -  case 에 타입을 쓰기
# -----------------------------------------------------------------------------
# case int():  -> 값이 int 이면 매칭 (그리고 그 값을 변수에 담을 수도 있음)
# 들어오는 값이 int든 str든 list든 dict든, 타입별로 갈라서 처리할 수 있다.
def describe(value) -> str:
    match value:
        case bool():                        # 주의: bool 은 int 의 하위라 먼저 검사
            return f"불리언: {value}"
        case int() | float():
            return f"숫자: {value} (제곱은 {value ** 2})"
        case str():
            return f"문자열: '{value}' (길이 {len(value)})"
        case [first, *rest]:                # 리스트/시퀀스: 첫 원소 + 나머지
            return f"리스트: 첫 항목={first}, 나머지 {len(rest)}개"
        case {"name": name}:                # 딕셔너리: 'name' 키가 있으면
            return f"딕셔너리: name={name}"
        case None:
            return "값이 없음(None)"
        case _:
            return f"처리 규칙이 없는 타입: {type(value).__name__}"


print(describe(10))                  # 숫자: 10 (제곱은 100)
print(describe(3.5))                 # 숫자: 3.5 (제곱은 12.25)
print(describe("안녕"))              # 문자열: '안녕' (길이 2)
print(describe([1, 2, 3, 4]))        # 리스트: 첫 항목=1, 나머지 3개
print(describe({"name": "홍길동", "age": 20}))  # 딕셔너리: name=홍길동
print(describe(True))                # 불리언: True
print(describe(None))                # 값이 없음(None)
print(describe(3 + 4j))              # 처리 규칙이 없는 타입: complex


# -----------------------------------------------------------------------------
# 4) 가드(guard) : case 뒤에 if 조건 추가
# -----------------------------------------------------------------------------
def grade(score: int) -> str:
    match score:
        case n if n >= 90:
            return "A"
        case n if n >= 80:
            return "B"
        case n if n >= 70:
            return "C"
        case _:
            return "F"


print(grade(95), grade(83), grade(40))   # A B F
