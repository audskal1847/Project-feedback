import streamlit as st
from openai import OpenAI
import google.generativeai as genai

# 1. 페이지 기본 설정
st.set_page_config(page_title="학생부 심화 탐구주제 구체화 도우미", page_icon="🏫", layout="wide")
st.title("💡 학생부 심화 탐구주제 구체화 프로그램")
st.markdown("추상적이고 두루뭉술한 탐구 주제를 진로 목표에 맞춰 구체적이고 체계적으로 다듬어 드립니다.")

# 2. 사이드바: API 제공자 및 키 설정
with st.sidebar:
    st.header("🔑 API 설정")
    
    api_provider = st.radio(
        "사용할 API 제공자를 선택하세요",
        ["Google AI Studio (공식)", "OpenRouter"]
    )
    
    if api_provider == "Google AI Studio (공식)":
        api_key = st.text_input("Google API 키를 입력하세요", type="password")
        selected_model = st.selectbox(
            "Gemini 모델 선택",
            ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash"]
        )
        st.markdown("[Google AI Studio 키 발급받기](https://aistudio.google.com/)")
        
    else:  # OpenRouter 선택 시
        api_key = st.text_input("OpenRouter API 키를 입력하세요", type="password")
        selected_model = st.selectbox(
            "OpenRouter 모델 선택",
            [
                "openai/gpt-4o",
                "anthropic/claude-3.5-sonnet",
                "google/gemma-2-9b-it:free",
                "meta-llama/llama-3.3-70b-instruct:free"
            ]
        )
        st.markdown("[OpenRouter 키 발급받기](https://openrouter.ai/)")

# 3. 인적사항 입력
st.subheader("1. 학생 정보 입력")
col1, col2, col3 = st.columns(3)
with col1:
    school_name = st.text_input("학교 이름")
with col2:
    grade = st.selectbox("학년", ["1학년", "2학년", "3학년"])
with col3:
    student_name = st.text_input("이름")

# 4. 진로 목표 및 관심 분야 입력
st.subheader("2. 진로 목표 및 관심 분야")
career_track = st.selectbox(
    "희망하는 진로 계열을 선택하세요",
    ["공학 계열", "의약학 계열", "교육 계열", "자연과학 계열", "사회과학 계열", "경영/경제 계열", "인문/어학 계열", "예체능 계열", "기타"]
)
specific_interest = st.text_input("구체적인 희망 전공이나 관심 키워드가 있다면 적어주세요 (예: 인공지능, 신약개발, 교육공학 등)")

# 5. 잠정적 탐구 주제 입력
st.subheader("3. 현재 생각 중인 탐구 주제")
initial_topic = st.text_area(
    "자료조사를 통해 확정한, 혹은 고민 중인 탐구 주제를 자유롭게 적어주세요.",
    placeholder="예) 수학 시간에 배운 미적분이 실생활에 쓰이는 것에 대해 탐구하고 싶음."
)

# 6. 시스템 프롬프트 (요구사항 완벽 반영)
system_prompt = """
당신은 고등학교 학생부종합전형(입학사정관) 및 교과 세특 전문가입니다. 
학생이 입력한 추상적이고 단순한 탐구 주제를 학생의 '진로 계열'에 맞춰 매우 구체적이고 깊이 있는 학업/진로 역량이 드러나는 주제로 발전시켜야 합니다.
제시하는 모든 내용은 주요 대학 입학사정관의 평가 기준(학업역량, 진로역량, 탐구의 구체성)에 완벽히 부합해야 합니다.

반드시 다음 4가지 형식과 조건에 맞춰 답변을 제공하세요:

1. [주제 진단]: 학생이 입력한 기존 주제에 대한 긍정적인 피드백과 보완점.
2. [구체화된 탐구 주제 제안]: 진로와 연계된 구체적이고 심화된 탐구 소주제를 **반드시 5가지** 제안하세요. (단순 조사가 아닌 문제해결, 논리적 분석, 교과 개념의 실생활 적용이 포함되도록 구성).
3. [탐구 과정 가이드 (상세화)]: 제안된 5가지 주제 중 가장 추천하는 1가지를 골라, 다음 4단계에 따라 매우 구체적으로 가이드하세요.
   - [동기 및 가설 설정]: 왜 이 주제를 탐구해야 하는지, 어떤 가설을 세울 수 있는지.
   - [핵심 탐구 질문]: 이 탐구를 관통하는 구체적인 리서치 퀘스천(Research Question).
   - [조사 및 분석 방법]: 어떤 통계자료, 논문 검색 키워드, 혹은 실험/사례분석 방식을 활용해야 하는지 구체적 안내.
   - [예상 결론 및 시사점]: 탐구를 통해 얻을 수 있는 결론과 진로와의 연결 고리.
4. [맞춤형 도서 및 연계 활동 제안]: 
   - [추천 도서]: '교과연계 및 전공적합성 기사 모음' 데이터베이스를 기반으로 하듯, 학생의 진로와 탐구 주제의 깊이를 더할 수 있는 관련 전문 도서 **2권**을 추천하세요 (저자와 추천 이유 필수 포함).
   - [연계 활동 제안]: 이 탐구를 바탕으로 창체(자율/동아리/진로)나 타 과목 세특으로 확장할 수 있는 후속 연계 활동을 **반드시 3가지** 제안하세요.
"""

# 7. 피드백 생성 버튼 및 실행 로직
if st.button("🚀 탐구 주제 구체화 및 피드백 받기"):
    if not api_key:
        st.error("왼쪽 사이드바에 해당 제공자의 API 키를 입력해주세요.")
    elif not initial_topic:
        st.warning("탐구 주제를 입력해주세요.")
    else:
        user_prompt = f"""
        - 학생 정보: {school_name} {grade} {student_name}
        - 진로 계열: {career_track} ({specific_interest})
        - 학생의 초기 탐구 주제: {initial_topic}

        이 정보를 바탕으로 학생의 탐구 주제를 구체화하고 피드백을 제공해주세요.
        """
        
        with st.spinner("AI가 선생님의 요구사항에 맞춰 5가지 주제와 3가지 연계활동을 포함해 심층 분석 중입니다... ⏳"):
            try:
                # 분기 1: Google AI Studio 공식 API를 사용할 때
                if api_provider == "Google AI Studio (공식)":
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name=selected_model,
                        system_instruction=system_prompt
                    )
                    response = model.generate_content(user_prompt)
                    result_text = response.text
                
                # 분기 2: OpenRouter API를 사용할 때
                else:
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=api_key,
                    )
                    response = client.chat.completions.create(
                        model=selected_model, 
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    result_text = response.choices[0].message.content
                
                # 결과 출력 (공통)
                st.success("분석이 완료되었습니다!")
                st.markdown("---")
                st.markdown(result_text)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
