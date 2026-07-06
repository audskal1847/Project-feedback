import streamlit as st
from openai import OpenAI
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# 1. 페이지 기본 설정
st.set_page_config(page_title="학생부 심화 탐구주제 구체화 도우미", page_icon="🏫", layout="wide")
st.title("💡 학생부 심화 탐구주제 구체화 프로그램")
st.markdown("추상적이고 두루뭉술한 탐구 주제를 기존 활동 및 진로 목표에 맞춰 체계적인 '꼬리물기 심화 탐구'로 다듬어 드립니다.")

# --- 웹 크롤링 함수 정의 (캐시 적용으로 속도 향상) ---
@st.cache_data(ttl=3600)
def scrape_reference_data():
    url = "https://nojaesu.com/category/DIRECTORY/%EA%B5%90%EA%B3%BC%EC%97%B0%EA%B3%84%26%EC%A0%84%EA%B3%B5%EC%A0%81%ED%95%A9%EC%84%9C%20%EA%B8%B0%EC%82%AC%20%EB%AA%A8%EC%9D%8C"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        extracted_texts = []
        for tag in soup.find_all(['h2', 'h3', 'a']):
            text = tag.get_text(strip=True)
            if len(text) > 5 and text not in extracted_texts:
                extracted_texts.append(text)
                
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
        
    else:
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

# 5. 기존(사전) 활동 입력
st.subheader("3. 기존 수행 활동 (사전 연계 주제)")
prior_activity = st.text_area(
    "지금까지 수행했던 활동 중, 이번 탐구와 연계하고 싶은 이전 활동 내용이나 주제를 적어주세요. (없을 경우 비워두셔도 됩니다.)",
    placeholder="예) 1학년 통합과학 시간에 '신재생 에너지의 한계'에 대해 발표했었음."
)

# 6. 잠정적 탐구 주제 입력
st.subheader("4. 현재 생각 중인 탐구 주제")
initial_topic = st.text_area(
    "자료조사를 통해 확정한, 혹은 고민 중인 탐구 주제를 자유롭게 적어주세요.",
    placeholder="예) 2학년 물리 시간에 배운 전자기 유도 법칙을 활용해 무선 충전 효율을 높이는 방안을 탐구하고 싶음."
)

# 7. 시스템 프롬프트 (요구사항 전면 반영)
system_prompt = """
당신은 고등학교 학생부종합전형(입학사정관) 및 교과 세특 전문가입니다. 
학생이 입력한 [사전 수행 활동]과 [초기 탐구 주제]를 유기적으로 연결하여, 과거 활동에서 한 단계 더 심화·확장되는 '꼬리물기식 탐구(종단적 연계)'가 되도록 설계해야 합니다.

[핵심 출력 조건: 개조식 작성]
모든 내용은 길고 장황한 서술형 문장을 절대 배제하십시오. 
반드시 **구체적인 교과 개념 키워드 및 전공 학술 용어**를 중심으로 한 **명료한 개조식(-, • 등의 기호 활용 및 명사형/음슴체 종결)**으로만 작성하세요. (예: ~함, ~분석함, ~을 제안함)

반드시 다음 5가지 형식과 조건에 맞춰 답변을 제공하세요:

1. [주제 진단]
   - 학생의 '사전 활동'과 '현재 주제' 간의 연계성 평가 (개조식)
   - 발전 및 보완점 제시 (개조식)

2. [구체화된 탐구 주제 제안]
   - 진로 및 이전 활동과 연계된 구체적이고 심화된 탐구 소주제를 **반드시 5가지** 제안
   - 각 주제는 문제해결, 논리적 분석, 교과 개념이 명시된 전문적인 '보고서 제목' 형태로 작성

3. [탐구 과정 가이드 (상세화)]
   - 제안된 5가지 주제 중 가장 추천하는 1가지를 골라, 다음 4단계에 따라 구체적 가이드
   - [동기 및 가설 설정]: 사전 활동 의문점 기반 구체적 가설 (개조식)
   - [핵심 탐구 질문]: 탐구를 관통하는 Research Question (명확한 질문형)
   - [조사 및 분석 방법]: 분석 방식, 통계자료, 교과서 단원 등 전공 용어 활용 (개조식)
   - **[예상 결론 및 시사점 (구체화)]**: 탐구를 통해 도출될 수 있는 구체적인 결론의 모습과, 이것이 지원 전공(진로) 분야에 던지는 학술적/실무적 시사점을 상세히 작성 (개조식)

4. [탐구의 기대 효과 및 유의사항] (학생 동기부여 및 시행착오 방지)
   - **[탐구 진행 시 긍정적 기대 효과]**: 이 탐구를 성공적으로 마쳤을 때 입학사정관에게 어필할 수 있는 학업 역량, 전공 적합성, 문제해결력 등 구체적인 성장 포인트 (개조식)
   - **[예상되는 어려움 및 극복 방안]**: 자료 조사의 한계, 고등학생 수준을 벗어나는 어려운 개념 등 학생이 겪을 수 있는 구체적인 어려움과, 이를 우회하거나 해결할 수 있는 현실적인 팁(Tip) 안내 (개조식)

5. [맞춤형 도서 및 연계 활동 제안]
   - **[추천 도서/기사]**: 제공된 **[참고 웹 크롤링 데이터]**를 최우선 분석하여 고등학생 수준에 맞는 도서/기사 **2권(편)** 추천 (저자명, 구체적 추천 사유 개조식 작성)
   - **[일반 후속 연계 활동]**: 창체(자율/동아리/진로)나 타 과목 세특으로 확장할 수 있는 연계 활동 **3가지** (개조식)
   - **[독서 융합 심화 연계 활동]**: 앞서 추천한 **[도서/기사]**의 내용과 **[현재 탐구 주제]**를 직접 융합하여 진행할 수 있는 심화 독서 활동 **1가지**를 별도 항목으로 명확히 구분하여 제안 (개조식)
"""

# 8. 피드백 생성 버튼 및 실행 로직
if st.button("🚀 탐구 주제 구체화 및 피드백 받기"):
    if not api_key:
        st.error("왼쪽 사이드바에 해당 제공자의 API 키를 입력해주세요.")
    elif not initial_topic:
        st.warning("현재 생각 중인 탐구 주제를 입력해주세요.")
    else:
        with st.spinner("웹사이트 크롤링 및 AI 분석을 진행 중입니다... ⏳"):
            try:
                # 1) 웹 크롤링 수행
                crawled_data = scrape_reference_data()
                
                # 2) 유저 프롬프트 완성
                prior_text = prior_activity if prior_activity.strip() else "특별히 입력된 사전 활동 없음 (현재 주제에만 집중하여 심화할 것)"
                
                user_prompt = f"""
                [학생 정보] {school_name} {grade} {student_name}
                [진로 계열] {career_track} ({specific_interest})
                [사전 수행 활동] {prior_text}
                [초기 탐구 주제] {initial_topic}
                
                [참고 웹 크롤링 데이터 - 이 데이터를 바탕으로 고등학생 수준에 맞는 책/기사를 추천할 것]
                {crawled_data}
                """
                
                # 3) 분기 1: Google AI Studio
                if api_provider == "Google AI Studio (공식)":
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name=selected_model,
                        system_instruction=system_prompt
                    )
                    response = model.generate_content(user_prompt)
                    result_text = response.text
                
                # 4) 분기 2: OpenRouter
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
