import streamlit as st
from openai import OpenAI
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# 1. 페이지 기본 설정
st.set_page_config(page_title="학생부 심화 탐구주제 구체화 도우미", page_icon="🏫", layout="wide")
st.title("💡 학생부 심화 탐구주제 구체화 프로그램")
st.markdown("추상적이고 두루뭉술한 탐구 주제를 진로 목표에 맞춰 구체적이고 체계적으로 다듬어 드립니다.")

# --- 웹 크롤링 함수 정의 (캐시 적용으로 속도 향상) ---
@st.cache_data(ttl=3600) # 1시간 동안 크롤링 결과를 기억하여 앱 속도를 높임
def scrape_reference_data():
    url = "https://nojaesu.com/category/DIRECTORY/%EA%B5%90%EA%B3%BC%EC%97%B0%EA%B3%84%26%EC%A0%84%EA%B3%B5%EC%A0%81%ED%95%A9%EC%84%9C%20%EA%B8%B0%EC%82%AC%20%EB%AA%A8%EC%9D%8C"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 블로그의 제목(기사/도서명) 위주로 텍스트를 추출
        extracted_texts = []
        # 제목 태그인 h2, h3, a 태그에서 텍스트 수집
        for tag in soup.find_all(['h2', 'h3', 'a']):
            text = tag.get_text(strip=True)
            if len(text) > 5 and text not in extracted_texts:
                extracted_texts.append(text)
                
        # 너무 길어지지 않게 상위 50개 텍스트만 합쳐서 반환
        result = " | ".join(extracted_texts[:50])
        return result
    except Exception as e:
        return f"크롤링 실패 (AI 자체 데이터 활용 요망): {e}"
# --------------------------------------------------

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

# 6. 시스템 프롬프트
system_prompt = """
당신은 고등학교 학생부종합전형(입학사정관) 및 교과 세특 전문가입니다. 
학생이 입력한 추상적이고 단순한 탐구 주제를 학생의 '진로 계열'에 맞춰 매우 구체적이고 깊이 있는 주제로 발전시켜야 합니다.

반드시 다음 4가지 형식과 조건에 맞춰 답변을 제공하세요:

1. [주제 진단]: 학생이 입력한 기존 주제에 대한 긍정적인 피드백과 보완점.
2. [구체화된 탐구 주제 제안]: 진로와 연계된 구체적이고 심화된 탐구 소주제를 **반드시 5가지** 제안하세요. (단순 조사가 아닌 문제해결, 논리적 분석, 교과 개념의 실생활 적용이 포함되도록 구성).
3. [탐구 과정 가이드 (상세화)]: 제안된 5가지 주제 중 가장 추천하는 1가지를 골라, 다음 4단계에 따라 구체적으로 가이드하세요.
   - [동기 및 가설 설정]: 왜 이 주제를 탐구해야 하는지, 어떤 가설을 세울 수 있는지.
   - [핵심 탐구 질문]: 이 탐구를 관통하는 구체적인 리서치 퀘스천(Research Question).
   - [조사 및 분석 방법]: 분석 방식 및 참고할 만한 교과서 단원 등 구체적 안내.
   - [예상 결론 및 시사점]: 탐구를 통해 얻을 수 있는 결론과 진로와의 연결 고리.
4. [맞춤형 도서 및 연계 활동 제안]: 
   - [추천 도서/기사]: 대학 전공 서적 등 어려운 책은 절대 배제하십시오. 사용자가 제공한 **[참고 웹 크롤링 데이터]**를 최우선으로 분석하여, 고등학생 수준에서 충분히 읽고 소화할 수 있는 관련 도서나 기사 **2권(편)**을 추천하세요. (저자와 고등학생 맞춤 추천 이유 필수 포함).
   - [연계 활동 제안]: 이 탐구를 바탕으로 창체(자율/동아리/진로)나 타 과목 세특으로 확장할 수 있는 후속 연계 활동을 **반드시 3가지** 제안하세요.
"""

# 7. 피드백 생성 버튼 및 실행 로직
if st.button("🚀 탐구 주제 구체화 및 피드백 받기"):
    if not api_key:
        st.error("왼쪽 사이드바에 해당 제공자의 API 키를 입력해주세요.")
    elif not initial_topic:
        st.warning("탐구 주제를 입력해주세요.")
    else:
        with st.spinner("웹사이트 크롤링 및 AI 분석을 진행 중입니다... ⏳"):
            try:
                # 1) 웹 크롤링 수행
                crawled_data = scrape_reference_data()
                
                # 2) AI에게 전달할 유저 프롬프트 완성 (크롤링 데이터 포함)
                user_prompt = f"""
                [학생 정보] {school_name} {grade} {student_name}
                [진로 계열] {career_track} ({specific_interest})
                [초기 탐구 주제] {initial_topic}
                
                [참고 웹 크롤링 데이터 - 이 데이터를 바탕으로 고등학생 수준에 맞는 책/기사를 추천할 것]
                {crawled_data}
                """
                
                # 3) 분기 1: Google AI Studio 공식 API를 사용할 때
                if api_provider == "Google AI Studio (공식)":
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name=selected_model,
                        system_instruction=system_prompt
                    )
                    response = model.generate_content(user_prompt)
                    result_text = response.text
                
                # 4) 분기 2: OpenRouter API를 사용할 때
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
                
                # 5) 결과 출력
                st.success("분석이 완료되었습니다!")
                st.markdown("---")
                st.markdown(result_text)

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
