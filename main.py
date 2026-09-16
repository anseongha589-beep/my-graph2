
import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.markdown(
    """
    1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한
    **216편의 영화 데이터**를 이용해 영화의 분포와 관계를 살펴봅니다.
    """
)


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/"
    "kobis_movies.csv"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 개봉일 처리
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 장르 처리
    # 여러 장르가 | 로 연결되어 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("알 수 없음")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        ).fillna(0)

    # 영화명 빈 값 처리
    df["movieNm"] = (
        df["movieNm"]
        .fillna("영화명 없음")
        .astype(str)
    )

    return df


# --------------------------------------------------
# 데이터 불러오기 오류 처리
# --------------------------------------------------
try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.error(f"오류 내용: {e}")
    st.stop()


# ==================================================
# 데이터 정보
# ==================================================
st.markdown("---")

st.subheader("📊 데이터 정보")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "전체 영화 수",
        f"{len(df):,}편"
    )

with col2:
    st.metric(
        "장르 수",
        f"{df['genre'].nunique():,}개"
    )

with col3:
    min_date = df["openDt"].min()
    max_date = df["openDt"].max()

    if pd.notna(min_date) and pd.notna(max_date):
        date_text = (
            f"{min_date.strftime('%Y-%m-%d')} ~ "
            f"{max_date.strftime('%Y-%m-%d')}"
        )
    else:
        date_text = "날짜 정보 없음"

    st.metric(
        "데이터 기간",
        date_text
    )


# ==================================================
# 그래프 1. 장르별 영화 편수
# ==================================================
st.markdown("---")
st.header("1️⃣ 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = [
    "장르",
    "영화 편수"
]


fig_genre = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수"
)

fig_genre.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}<extra></extra>"
    )
)

fig_genre.update_layout(
    height=600,
    legend_title_text="장르"
)

st.plotly_chart(
    fig_genre,
    use_container_width=True
)


# --------------------------------------------------
# 그래프 1 알 수 있는 것
# --------------------------------------------------
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "____________________________________________________________"
)


# --------------------------------------------------
# 그래프 1 데이터 표
# --------------------------------------------------
with st.expander("📋 장르별 영화 편수 자세히 보기"):

    display_genre = genre_counts.copy()

    display_genre["비율"] = (
        display_genre["영화 편수"]
        / len(df)
        * 100
    ).round(1).astype(str) + "%"

    display_genre = display_genre[
        ["장르", "영화 편수", "비율"]
    ]

    st.dataframe(
        display_genre,
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# 그래프 2. 장르별 영화 트리맵
# ==================================================
st.markdown("---")
st.header("2️⃣ 장르 안에 영화가 들어 있는 트리맵")

st.markdown(
    """
    **각 장르 안에 해당 장르의 영화들이 들어 있습니다.**
    영화 칸의 크기는 **총 관객수**를 나타냅니다.
    """
)


# 트리맵용 데이터 준비
treemap_df = df[
    [
        "genre",
        "movieNm",
        "total_audi"
    ]
].copy()


# 총 관객수가 0인 데이터는 트리맵에서 의미가 없으므로
# 아주 작은 값으로 처리해 모든 영화를 표시
treemap_df["treemap_audi"] = treemap_df["total_audi"].clip(lower=1)


fig_treemap = px.treemap(
    treemap_df,
    path=[
        px.Constant("전체"),
        "genre",
        "movieNm"
    ],
    values="treemap_audi",
    custom_data=[
        "movieNm",
        "total_audi",
        "genre"
    ],
    title="장르별 영화 총 관객수 트리맵"
)


# 마우스를 올렸을 때 표시되는 내용
fig_treemap.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "장르: %{customdata[2]}<br>"
        "총 관객: %{customdata[1]:,}명"
        "<extra></extra>"
    )
)


fig_treemap.update_layout(
    height=750,
    margin=dict(
        t=60,
        l=10,
        r=10,
        b=10
    )
)


st.plotly_chart(
    fig_treemap,
    use_container_width=True
)


# --------------------------------------------------
# 그래프 2 알 수 있는 것
# --------------------------------------------------
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "____________________________________________________________"
)


# --------------------------------------------------
# 그래프 2 설명
# --------------------------------------------------
with st.expander("🔎 트리맵 보는 방법"):

    st.markdown(
        """
        - **큰 영역**은 장르를 나타냅니다.
        - **장르 안의 작은 칸**은 각각의 영화를 나타냅니다.
        - **영화 칸이 클수록 총 관객수가 많습니다.**
        - 영화 칸에 **마우스를 올리면 영화명과 총 관객수**를 확인할 수 있습니다.
        """
    )


# ==================================================
# 원본 데이터
# ==================================================
st.markdown("---")

with st.expander("📁 원본 데이터 보기"):
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

