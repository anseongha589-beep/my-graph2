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


# --------------------------------------------------
# 트리맵용 데이터 준비
# --------------------------------------------------
treemap_df = df[
    [
        "genre",
        "movieNm",
        "total_audi"
    ]
].copy()


treemap_df["treemap_audi"] = (
    treemap_df["total_audi"].clip(lower=1)
)


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
# 그래프 3. 총 관객수 분포
# ==================================================
st.markdown("---")
st.header("3️⃣ 총 관객의 분포 (히스토그램)")


hist_df = df[
    ["movieNm", "total_audi"]
].copy()

hist_df = hist_df[
    hist_df["total_audi"] >= 0
].copy()


if len(hist_df) > 0:

    # --------------------------------------------------
    # 100만 명 미만 영화 수
    # --------------------------------------------------
    under_1m_count = int(
        (hist_df["total_audi"] < 1_000_000).sum()
    )


    # --------------------------------------------------
    # 가장 많은 관객을 기록한 영화
    # --------------------------------------------------
    max_movie_row = hist_df.loc[
        hist_df["total_audi"].idxmax()
    ]

    max_movie_name = max_movie_row["movieNm"]
    max_movie_audi = int(max_movie_row["total_audi"])


    # --------------------------------------------------
    # 히스토그램
    # --------------------------------------------------
    fig_hist = px.histogram(
        hist_df,
        x="total_audi",
        nbins=15,
        title="영화별 총 관객수 분포",
        labels={
            "total_audi": "총 관객 수",
            "count": "영화 편수"
        }
    )


    fig_hist.update_traces(
        hovertemplate=(
            "총 관객 수: %{x}<br>"
            "영화 편수: %{y}편"
            "<extra></extra>"
        )
    )


    fig_hist.update_layout(
        height=600,
        xaxis_title="총 관객 수",
        yaxis_title="영화 편수",
        bargap=0.05
    )


    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )


    # --------------------------------------------------
    # 그래프 설명
    # --------------------------------------------------
    st.markdown(
        f"""
        **{len(hist_df):,}편 가운데 {under_1m_count:,}편이
        100만 명 미만입니다. 가장 많이 본 영화는
        {max_movie_name}({max_movie_audi:,}명)입니다.**
        """
    )


    st.markdown(
        "💡 **이 그래프로 알 수 있는 것:** "
        "____________________________________________________________"
    )


else:
    st.warning(
        "총 관객수 데이터가 없어 히스토그램을 만들 수 없습니다."
    )


# ==================================================
# 그래프 4. 개봉일 스크린수와 총 관객수의 관계
# ==================================================
st.markdown("---")
st.header("4️⃣ 개봉일 스크린수와 총 관객수의 관계")

st.markdown(
    """
    영화의 **개봉일 스크린수(first_scrn)**와
    **총 관객수(total_audi)** 사이의 관계를 산점도로 확인합니다.

    점 하나가 영화 한 편을 나타내며, **장르별로 색을 다르게 표시**합니다.
    점에 마우스를 올리면 **영화명과 관련 데이터**를 확인할 수 있습니다.
    """
)


# --------------------------------------------------
# 산점도용 데이터
# --------------------------------------------------
scatter_df = df[
    [
        "movieNm",
        "genre",
        "first_scrn",
        "total_audi"
    ]
].copy()


scatter_df = scatter_df[
    (scatter_df["first_scrn"] > 0) &
    (scatter_df["total_audi"] > 0)
].copy()


# --------------------------------------------------
# 산점도
# --------------------------------------------------
if len(scatter_df) > 0:

    fig_scatter = px.scatter(
        scatter_df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        hover_name="movieNm",
        hover_data={
            "first_scrn": ":,",
            "total_audi": ":,",
            "genre": True
        },
        labels={
            "first_scrn": "개봉일 스크린수",
            "total_audi": "총 관객수",
            "genre": "장르"
        },
        title="개봉일 스크린수와 총 관객수의 관계"
    )


    fig_scatter.update_traces(
        marker=dict(
            size=10,
            opacity=0.75
        )
    )


    fig_scatter.update_layout(
        height=700,
        xaxis_title="개봉일 스크린수",
        yaxis_title="총 관객수",
        legend_title_text="장르"
    )


    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )


    # --------------------------------------------------
    # 그래프 4 알 수 있는 것
    # --------------------------------------------------
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "개봉일 스크린수와 총 관객수 사이에 어떤 관계가 있는지 "
        "확인할 수 있습니다."
    )


else:
    st.warning(
        "개봉일 스크린수와 총 관객수 데이터가 없어 산점도를 만들 수 없습니다."
    )


# ==================================================
# 그래프 5. 장르별 총 관객수 상자 그림
# ==================================================
st.markdown("---")
st.header("5️⃣ 장르별 총 관객수 상자 그림")

st.markdown(
    """
    **영화가 10편 이상인 장르만** 골라 장르별 총 관객수의 분포를
    상자 그림(박스플롯)으로 비교합니다.

    상자 밖으로 튀어나온 점은 **이상치**입니다.
    이상치에 마우스를 올리면 **영화명과 총 관객수**를 확인할 수 있습니다.
    """
)


# --------------------------------------------------
# 장르별 영화 수
# --------------------------------------------------
genre_movie_counts = (
    df["genre"]
    .value_counts()
)


# 영화가 10편 이상인 장르만 선택
valid_genres = genre_movie_counts[
    genre_movie_counts >= 10
].index.tolist()


# --------------------------------------------------
# 박스플롯 데이터
# --------------------------------------------------
box_df = df[
    df["genre"].isin(valid_genres)
].copy()


# 총 관객수가 0인 데이터 제외
box_df = box_df[
    box_df["total_audi"] > 0
].copy()


if len(box_df) > 0:

    # --------------------------------------------------
    # 장르 순서
    # --------------------------------------------------
    box_df["genre"] = pd.Categorical(
        box_df["genre"],
        categories=valid_genres,
        ordered=True
    )


    # --------------------------------------------------
    # 박스플롯
    # --------------------------------------------------
    fig_box = px.box(
        box_df,
        x="genre",
        y="total_audi",
        points="outliers",
        custom_data=[
            "movieNm",
            "genre",
            "total_audi"
        ],
        category_orders={
            "genre": valid_genres
        },
        labels={
            "genre": "장르",
            "total_audi": "총 관객수"
        },
        title="영화 10편 이상인 장르의 총 관객수 분포"
    )


    # --------------------------------------------------
    # 마우스 오버
    # --------------------------------------------------
    fig_box.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "장르: %{customdata[1]}<br>"
            "총 관객수: %{customdata[2]:,}명"
            "<extra></extra>"
        ),
        marker=dict(
            size=7
        ),
        line=dict(
            width=2
        )
    )


    # --------------------------------------------------
    # 일반적인 선형 세로축
    # --------------------------------------------------
    fig_box.update_yaxes(
        type="linear",
        title_text="총 관객수",
        tickformat=",.0f"
    )


    fig_box.update_layout(
        height=650,
        xaxis_title="장르",
        yaxis_title="총 관객수",
        showlegend=False,
        boxmode="group",
        margin=dict(
            l=70,
            r=30,
            t=70,
            b=70
        )
    )


    st.plotly_chart(
        fig_box,
        use_container_width=True
    )


    # --------------------------------------------------
    # 포함된 장르
    # --------------------------------------------------
    valid_genres_text = ", ".join(valid_genres)

    st.markdown(
        f"""
        **영화가 10편 이상인 장르:** {valid_genres_text}
        """
    )


    # --------------------------------------------------
    # 그래프 5 알 수 있는 것
    # --------------------------------------------------
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "영화가 10편 이상인 장르들의 총 관객수 분포와 "
        "상자 밖으로 튀어나온 이상치 영화를 확인할 수 있습니다."
    )


else:
    st.warning(
        "영화가 10편 이상인 장르의 데이터가 없습니다."
    )


# ==================================================
# 그래프 6. 첫 주 관객수를 크기로 나타낸 버블 그래프
# ==================================================
st.markdown("---")
st.header("6️⃣ 첫 주 관객수까지 나타낸 버블 그래프")

st.markdown(
    """
    4번 산점도에 **첫 주 관객수(first_week_audi)**를 추가했습니다.

    - 가로축 → **개봉일 스크린수**
    - 세로축 → **총 관객수**
    - 점 색 → **장르**
    - 점 크기 → **첫 주 관객수**

    따라서 **버블이 클수록 첫 주 관객수가 많은 영화**입니다.
    """
)


# --------------------------------------------------
# 버블 그래프용 데이터
# --------------------------------------------------
bubble_df = df[
    [
        "movieNm",
        "genre",
        "first_scrn",
        "first_week_audi",
        "total_audi"
    ]
].copy()


# 필요한 값이 있는 영화만 사용
bubble_df = bubble_df[
    (bubble_df["first_scrn"] > 0) &
    (bubble_df["total_audi"] > 0) &
    (bubble_df["first_week_audi"] > 0)
].copy()


# --------------------------------------------------
# 버블 그래프
# --------------------------------------------------
if len(bubble_df) > 0:

    fig_bubble = px.scatter(
        bubble_df,
        x="first_scrn",
        y="total_audi",
        color="genre",
        size="first_week_audi",
        size_max=45,
        hover_name="movieNm",
        hover_data={
            "first_scrn": ":,",
            "first_week_audi": ":,",
            "total_audi": ":,",
            "genre": True
        },
        labels={
            "first_scrn": "개봉일 스크린수",
            "total_audi": "총 관객수",
            "first_week_audi": "첫 주 관객수",
            "genre": "장르"
        },
        title="개봉일 스크린수 × 총 관객수 × 첫 주 관객수"
    )


    # --------------------------------------------------
    # 버블 모양
    # --------------------------------------------------
    fig_bubble.update_traces(
        marker=dict(
            opacity=0.65,
            line=dict(
                width=1
            )
        ),
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "장르: %{customdata[3]}<br>"
            "개봉일 스크린수: %{x:,}개<br>"
            "첫 주 관객수: %{customdata[1]:,}명<br>"
            "총 관객수: %{y:,}명"
            "<extra></extra>"
        )
    )


    # --------------------------------------------------
    # 그래프 크기 및 축
    # --------------------------------------------------
    fig_bubble.update_layout(
        height=750,
        xaxis_title="개봉일 스크린수",
        yaxis_title="총 관객수",
        legend_title_text="장르"
    )


    st.plotly_chart(
        fig_bubble,
        use_container_width=True
    )


    # --------------------------------------------------
    # 버블 그래프 설명
    # --------------------------------------------------
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "개봉일 스크린수와 총 관객수의 관계뿐만 아니라 "
        "첫 주 관객수가 많은 영화가 어떤 영화인지 함께 확인할 수 있습니다."
    )


else:
    st.warning(
        "개봉일 스크린수, 첫 주 관객수, 총 관객수 데이터가 없어 "
        "버블 그래프를 만들 수 없습니다."
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
