import streamlit as st
from openai import OpenAI

# 1. 페이지 기본 설정
st.set_page_config(page_title="학생부 심화 탐구주제 구체화 도우미", page_icon="🏫", layout="wide")
st.title("💡 학생부 심화 탐구주제 구체화 프로그램")
st.markdown("추상적이고 두루뭉술한 탐구 주제를 진로 목표에 맞춰 구체적이고 체계적으로 다듬어 드립니다.")

# 2. 사이드바: 기본 설정 (OpenRouter API 키 입력)
with st.sidebar:
    st.header("🔑 기본 설정")
    openrouter_api_key = st.text_input("OpenRouter API 키를 입력하세요", type="password")
    st.markdown("[OpenRouter API 발급받기](https://openrouter.ai/)")

# 3. 인적사항 입력 (다섯 번째 조건)
st.subheader("1. 학생 정보 입력")
col1, col2, col3 = st.columns(3)
with col1:
    school_name = st.text_input("학교 이름")
with col2:
    grade = st.selectbox("학년", ["1학년", "2학년", "3학년"])
with col3:
    student_name = st.text_input("이름")

# 4. 진로 목표 및 관심 분야 입력 (두 번째 조건)
st.subheader("2. 진로 목표 및 관심 분야")
career_track = st.selectbox(
    "희망하는 진로 계열을 선택하세요",
    ["공학 계열", "의약학 계열", "교육 계열", "자연과학 계열", "사회과학 계열", "경영/경제 계열", "인문/어학 계열", "예체능 계열", "기타"]
)
specific_interest = st.text_input("구체적인 희망 전공이나 관심 키워드가 있다면 적어주세요 (예: 인공지능, 신약개발, 교육공학 등)")

# 5. 잠정적 탐구 주제 입력 (세 번째 조건)
st.subheader("3. 현재 생각 중인 탐구 주제")
initial_topic = st.text_area(
    "자료조사를 통해 확정한, 혹은 고민 중인 탐구 주제를 자유롭게 적어주세요.",
    placeholder="예) 수학 시간에 배운 미적분이 실생활에 쓰이는 것에 대해 탐구하고 싶음."
)

# 6. 피드백 생성 버튼 및 AI 로직 (첫 번째, 네 번째 조건 및 핵심 목적)
if st.button("🚀 탐구 주제 구체화 및 피드백 받기"):
    if not openrouter_api_key:
        st.error("왼쪽 사이드바에 OpenRouter API 키를 입력해주세요.")
    elif not initial_topic:
        st.warning("탐구 주제를 입력해주세요.")
    else:
        with st.spinner("AI가 학생의 주제를 분석하고 체계적으로 다듬고 있습니다... ⏳"):
            try:
                # OpenRouter 클라이언트 설정
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=openrouter_api_key,
                )
                
                # 시스템 프롬프트 (가이드북 및 특강 자료의 핵심 로직 반영)
                system_prompt = """
                당신은 고등학교 학생부종합전형(입학사정관) 및 교과 세특 전문가입니다. 
                학생이 입력한 추상적이고 단순한 탐구 주제를 학생의 '진로 계열'에 맞춰 매우 구체적이고 깊이 있는 학업/진로 역량이 드러나는 주제로 발전시켜야 합니다.

                다음 4가지 형식으로 답변을 제공하세요:
                1. [주제 진단]: 학생이 입력한 기존 주제에 대한 긍정적인 피드백과 보완점.
                2. [구체화된 탐구 주제 제안]: 진로와 연계된 구체적인 소주제 2~3가지 제안 (문제해결 과정이나 논리적 분석이 포함되도록).
                3. [탐구 과정 가이드]: 제안된 주제 중 하나를 골라, 어떤 순서로 탐구(가설-조사-결론)해야 하는지 가이드.
                4. [맞춤형 도서 및 연계 활동 제안]: 해당 주제의 깊이를 더할 수 있는 추천 도서 2권과, 이후 창체(자율/동아리)나 다른 과목으로 연계할 수 있는 후속 활동 제안.
                """
                
                user_prompt = f"""
                - 학생 정보: {school_name} {grade} {student_name}
                - 진로 계열: {career_track} ({specific_interest})
                - 학생의 초기 탐구 주제: {initial_topic}
                
                이 정보를 바탕으로 학생의 탐구 주제를 구체화하고 피드백을 제공해주세요.
                """

                # API 호출 (모델은 필요에 따라 변경 가능, 예: anthropic/claude-3.5-sonnet, openai/gpt-4o)
                response = client.chat.completions.create(
                   model="google/gemini-2.0-flash-lite-preview-02-05:free", 
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                
                # 결과 출력
                st.success("분석이 완료되었습니다!")
                st.markdown("---")
                st.markdown(response.choices[0].message.content)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
