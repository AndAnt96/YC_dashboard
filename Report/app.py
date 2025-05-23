from ipyleaflet import Marker, DivIcon, Map, basemaps, leaflet, Popup
from shiny import App, reactive, ui,render
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import shiny.experimental as x
import plotly.express as px
import plotly.graph_objects as go
from plotly_streaming import render_plotly_streaming
from pathlib import Path
import faicons
import folium
import geopandas as gpd
from shapely import wkt 
from shapely.geometry import mapping
import pydeck as pdk


category_colors = {
    "Serverless": 0,
    "Containers": 1,
    "Cloud Operations": 2,
    "Security & Identity": 3,
    "Dev Tools": 4,
    "Machine Learning & GenAI": 5,
    "Data": 6,

    "Networking & Content Delivery": 7,
    "Front-End Web & Mobile": 8,
    "Storage": 9,
    "Game Tech": 10,
}

industry_columns = ['건설업','광업.제조업',
                    '도소매ㆍ음식숙박업',
                    '사업ㆍ개인ㆍ공공서비스업',
                    '전기ㆍ운수ㆍ통신ㆍ금융업',
                    '전산업',
                    '총합']

house_column = ['1만 명당 주택 수',
                '주택 합계',
                '단독주택-일반',
                '단독주택-다가구',
                '아파트',
                '연립주택',
                '다세대주택',
                '1만 명당 노후주택 수']

hospital_column = ['병원', 
                   '정신병원', 
                   '종합병원', 
                   '치과병원', 
                   '한방병원', 
                   '병원 합계', 
                   '1천 명당 병원 수']

years_column =[2022, 2023, 2024]

culture_column = ['영화관수',
                    '공원수',
                    '공연장',
                    '과학관',
                    '문화산업진흥시설',
                    '지방문화원',
                    '문화예술진흥시설',
                    '전시시설',
                    '공공도서관',
                    '사회복지시설',
                    '총 시설수',
                    '1만 명당 시설 수']

def read_data():
    df = pd.read_csv(
        Path(__file__).parent / "data/df_yc.csv", delimiter=","
    )
    return df

def read_outflow_total():
    df_outflow_total = pd.read_csv(
        Path(__file__).parent / "data/1_out_trend.csv", delimiter=","
    )
    return df_outflow_total

def read_outflow_2022():
    df_outflow_2022 = pd.read_csv(
        Path(__file__).parent / "data/2_out_cnt_2022.csv", delimiter=","
    )
    return df_outflow_2022


def read_outflow_2023():
    df_outflow_2023 = pd.read_csv(
        Path(__file__).parent / "data/2_out_cnt_2023.csv", delimiter=","
    )
    return df_outflow_2023

def read_outflow_2024():
    df_outflow_2024 = pd.read_csv(
        Path(__file__).parent / "data/2_out_cnt_2024.csv", delimiter=","
    )
    return df_outflow_2024


def get_color_theme(theme, list_categories=None):

    if theme == "Custom":
        list_colors = [
            "#F6AA54",
            "#2A5D78",
            "#9FDEF1",
            "#B9E52F",
            "#E436BB",
            "#6197E2",
            "#863CFF",
            "#30CB71",
            "#ED90C7",
            "#DE3B00",
            "#25F1AA",
            "#C2C4E3",
            "#33AEB1",
            "#8B5011",
            "#A8577B",
        ]
    elif theme == "RdBu":
        list_colors = px.colors.sequential.RdBu.copy()
        del list_colors[5]  # Remove color position 5
    elif theme == "GnBu":
        list_colors = px.colors.sequential.GnBu
    elif theme == "RdPu":
        list_colors = px.colors.sequential.RdPu
    elif theme == "Oranges":
        list_colors = px.colors.sequential.Oranges
    elif theme == "Blues":
        list_colors = px.colors.sequential.Blues
    elif theme == "Reds":
        list_colors = px.colors.sequential.Reds
    elif theme == "Hot":
        list_colors = px.colors.sequential.Hot
    elif theme == "Jet":
        list_colors = px.colors.sequential.Jet
    elif theme == "Rainbow":
        list_colors = px.colors.sequential.Rainbow

    if list_categories is not None:
        final_list_colors = [
            list_colors[category_colors[category] % len(list_colors)]
            for category in list_categories
        ]
    else:
        final_list_colors = list_colors

    return final_list_colors


def get_color_template(mode):
    if mode == "light":
        return "plotly_white"
    else:
        return "plotly_dark"


def get_background_color_plotly(mode):
    if mode == "light":
        return "white"
    else:
        return "rgb(29, 32, 33)"


def get_map_theme(mode):
    print(mode)
    if mode == "light":
        return basemaps.CartoDB.Positron
    else:
        return basemaps.CartoDB.DarkMatter


# 지도에서 원형 아이콘을 형성하는 함수 
def create_custom_icon(count):

    size_circle = 45 + (count / 10)

    # Define the HTML code for the icon
    html_code = f"""
    <div style=".leaflet-div-icon.background:transparent !important;
        position:relative; width: {size_circle}px; height: {size_circle}px;">
        <svg width="{size_circle}" height="{size_circle}" viewBox="0 0 42 42"
            class="donut" aria-labelledby="donut-title donut-desc" role="img">
            <circle class="donut-hole" cx="21" cy="21" r="15.91549430918954"
                fill="white" role="presentation"></circle>
            <circle class="donut-ring" cx="21" cy="21" r="15.91549430918954"
                fill="transparent" stroke="color(display-p3 0.9451 0.6196 0.2196)"
                stroke-width="3" role="presentation"></circle>
            <text x="50%" y="60%" text-anchor="middle" font-size="13"
                font-weight="bold" fill="#000">{count}</text>
        </svg>
    </div>
    """

    # Create a custom DivIcon
    return DivIcon(
        icon_size=(50, 50), icon_anchor=(25, 25), html=html_code, class_name="dummy"
    )


# 지도 마커를 선택했을 때 popup에 나올 내용의 함수 
def create_custom_popup(country, total, dark_mode, color_theme):

    # Group by 'region' and count occurrences of each region
    df = read_data()
    category_counts = (
        df[df.country == country].groupby("category").size().reset_index(name="count")
    )

    # Create a pie chart using plotly.graph_objects
    data = [
        go.Pie(
            labels=category_counts["category"],
            values=category_counts["count"],
            hole=0.3,
            textinfo="percent+label",
            marker=dict(
                colors=get_color_theme(color_theme, category_counts["category"])
            ),
        )
    ]

    # Set title and template
    layout = go.Layout(
        title=f"{total} Community Builders in {country}",
        template=get_color_template(dark_mode),
        paper_bgcolor=get_background_color_plotly(dark_mode),
        title_x=0.5,
        titlefont=dict(size=20),
        showlegend=False,
    )

    figure = go.Figure(data=data, layout=layout)
    figure.update_traces(
        textposition="outside", textinfo="percent+label", textfont=dict(size=15)
    )
    figure.layout.width = 600
    figure.layout.height = 400

    popup = Popup(child=go.FigureWidget(figure), max_width=600, max_height=400)

    return popup


app_ui = ui.page_fillable(
    ui.page_navbar(
        ui.nav_panel(
            "이탈 현황",
            ui.row(
                ui.layout_columns(
                    ui.input_select(
                            id="years",
                            label="연도 선택",
                            choices=years_column,
                            selected="2024"
                    ), col_widths=(2,)
                ),
            ),                    
            ui.row(
                ui.layout_columns(
                    ui.output_ui('outflow_value_box1'),
                    ui.output_ui('outflow_value_box2'),
                    ui.output_ui('outflow_value_box3'),
                    col_widths=(4, 4, 4),
                ),
            ),
            ui.row(
                ui.layout_columns(
                    x.ui.card(
                                ui.output_ui("arclayer"),
                                class_='card_bar'
                              ),
                    x.ui.card(output_widget("get_top10_table"), class_="card_bar",fill=True),          
                    x.ui.card(output_widget("pieplot_0"),class_='card_bar'),
                    col_widths=(4,2,6),
                ),
            ),
        ),
        ui.nav_panel(
            "인프라 상세 비교",
            ui.row(
                ui.tags.div(
                ui.tags.h5("필터 선택", class_="filter-title")
                ),
                ui.layout_columns(
                    ui.input_select(
                        id="industry",
                        label="산업군 선택",
                        choices=industry_columns,
                        selected="총합"
                        ),
                        col_widths=(2,)
                    ),
                ui.layout_columns(
                    x.ui.card(output_widget("pieplot_1"), class_="card_bar"),
                    x.ui.card(output_widget("diff_df"), class_="card_bar",fill=True),
                    ui.navset_card_tab(  
                        ui.nav_panel("교육",output_widget("treemap_0")),
                        ui.nav_panel("문화복지",
                                     ui.input_select(
                                            id="culture",
                                            label="문화복지 요인 선택",
                                            choices=culture_column,
                                            selected="총 시설수"
                                    ), 
                                    output_widget("barplot_1")),
                        ui.nav_panel("의료",
                                    ui.input_select(
                                            id="hospital",
                                            label="의료 요인 선택",
                                            choices=hospital_column,
                                            selected="병원 합계"
                                    ),
                                    output_widget('barplot_2'),
                                            
                        ),
                        id="tab",  
                    ),col_widths=(4,2,6), class_="custom-row-spacing",
                ),
            ),        
            ui.navset_card_tab(  
                ui.nav_panel("주택",
                            ui.input_select(
                                    id="house",
                                    label="주택 요인 선택",
                                    choices=house_column,
                                    selected="주택 합계"
                            ),
                            output_widget('barplot_0'),
                ),
                ui.nav_panel("주택 노후화 비율",
                            output_widget('barplot_3'),
                ),
            ),
        ),

        ui.nav_panel(
            '결론',
            ui.tags.div(
                ui.markdown("""
                        
## 직업 분야
                            
- 제조업을 많이 차지하고 있는 구미시와 차별점을 두기 위해 첨단 산업을 육성하여 영천시에 인구 유입을 할 수 있도록 해야한다.
- 구미시에서 통근하는 주민들을 위해 대중 교통 증설할 필요가 존재한다.

## 교육 - 문화 분야

- 이미 타지역보다 인구대비 인프라가 많기 때문에 해당 분야보다 다른 분야에 대한 투자가 필요하다.

## 주택 및 주거 분야

- 만명 당 주택 수가 타지역보다 높지만, 아파트의 세대수가 타지역보다 적다.
- 노후화된 단독주택이 타지역보다 많기 때문에 해당 부분에 대한 보수 및 재개발 유도을 통해 주거 환경 개선이 필요하다.

"""),class_="markdown-conclusion"
            ),
        ),
        title=ui.img(src="images/대시보드-배너-003.jpg",style="max-width:500px;width:80;background-color: #202534;"
                     ),
        id="page",
        sidebar=ui.sidebar(
            ui.input_select(
                id="color_theme",
                label="Color theme",
                choices=[
                    "Custom",
                    "RdBu",
                    "GnBu",
                    "RdPu",
                    "Oranges",
                    "Blues",
                    "Reds",
                    "Hot",
                    "Jet",
                    "Rainbow",
                ],
                selected="Custom",
            ),
            ui.input_dark_mode(id="dark_mode", mode="light"),
            open="closed",
        ),
        footer=ui.h6(
            "Made by 영천의 문단속 © 2025",
            style="color: white !important; text-align: center;",
        ),
        window_title="Yeongcheon population outflow Dashboard",
    ),
    ui.tags.style(
        """
        .leaflet-popup-content {
            width: 600px !important;
        }
        .navbar {
            background-color: #272c3d !important; 
        }
        
        .nav-link {
        font-size: 30px !important;
        font-weight: bold;
        color: white !important;
        }

        .navbar.navbar-expand-md {
            background-color: #272c3d !important;
        }

        .navbar-nav .nav-link {
            font-size: 30px !important;
            font-weight: bold;
            color: white !important;
        }

        .nav-tabs {
        background-color: #272c3d !important;
        border-bottom: 2px solid #444 !important;
        
        }

        .nav-tabs .nav-link {
        color: white !important;
        font-size: 16px;
        }

        .nav-tabs .nav-link.active {
        background-color: #272c3d !important;
        border-width: 5px !important; 
        color: white !important;            
        border-color: #444 #444 #444 !important;
        }

        .tab-content {
        background-color: #272c3d !important;
        padding: 1rem;
        border-radius: 10px;
        }

        .markdown-conclusion {
        color: white;
        font-size: 35px;
        line-height: 1.6;
        }

        .dataframe thead {
            background-color: #272c3d !important;
            color: white !important;
        }

        .dataframe tbody {
            background-color: #272c3d !important;
            color: white !important;
        }
        .custom-row-spacing {
        margin-top: 0px;
        margin-bottom: 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        }

        .leaflet-div-icon {
            background: transparent !important;
            border: transparent !important;
        }
        .collapse-toggle {
            color: #FD9902 !important;
        }
        .main {
            background-image: url("images/background.jpg");
            height: 100%;
            background-position: center;
            background-repeat: no-repeat;
            background-size: cover;
        }

        .card-body {
        background-color: #272c3d !important;
        color: white !important;
        }
        .card_bar {
        background-color: #272c3d !important;
        color: purple;
        
        }

        .card_bar .dataframe thead {
        background-color: #272c3d !important;  
        color: white !important;             
        font-weight: bold;
        }

        .card_bar .dataframe tbody {
            background-color: #272c3d !important;  
            color: white !important;
        }

        .card_bar .dataframe td, 
        .card_bar .dataframe th {
            border: none !important;
            padding: 6px 12px;
        }

        .value-box {
        background-color: #272c3d !important;
        color: white !important;
        border-radius: 12px;
        }

        .value-box .value-box-title {
            color: #F72585 !important;
            font-size: 30px;
        }

        .value-box .value-box-value {
            color: white !important;
            font-size: 30px;
            font-weight: bold;
        }

        .value-box .value-box-showcase {
            background-color: transparent !important;
        }
        
        }
        div#map_full.html-fill-container {
            height: -webkit-fill-available !important;
            min-height: 850px !important;
            max-height: 2000px !important;
        }
        div#main_panel.html-fill-container {
            height: -webkit-fill-available !important;
        }

        .card-header {
        background-color: #272c3d !important;  
        color: #F72585 !important;              
        font-size: 100px;                      
        font-weight: bold;
        padding: 50px;
        border-radius: 30px;                 
        }

        select#industry {
        background-color: #828898 !important;
        color: white !important;
        border: 1px solid white !important;
        padding: 6px;
        font-size: 25px;
        border-radius: 6px;
        }

        label[for="industry"] {
        font-size: 30px;         
        color: #F72585;          
        font-weight: bold;     
        margin-bottom: 6px;
        display: block;
        }
        
        select#house {
        background-color: #828898 !important;
        color: white !important;
        border: 1px solid white !important;
        padding: 6px;
        font-size: 25px;
        border-radius: 6px;
        }

        label[for="house"] {
        font-size: 30px;         
        color: #F72585;          
        font-weight: bold;     
        margin-bottom: 6px;
        display: block;
        }
        
        select#hospital {
        background-color: #828898 !important;
        color: white !important;
        border: 1px solid white !important;
        padding: 6px;
        font-size: 25px;
        border-radius: 6px;
        }

        label[for="hospital"] {
        font-size: 30px;         
        color: #F72585;          
        font-weight: bold;     
        margin-bottom: 6px;
        display: block;
        }
        
        select#years {
        background-color: #828898 !important;
        color: white !important;
        border: 1px solid white !important;
        padding: 6px;
        font-size: 25px;
        border-radius: 6px;
        }

        label[for="years"] {
        font-size: 30px;         
        color: #F72585;          
        font-weight: bold;     
        margin-bottom: 6px;
        display: block;
        }
        
        select#culture {
        background-color: #828898 !important;
        color: white !important;
        border: 1px solid white !important;
        padding: 6px;
        font-size: 25px;
        border-radius: 6px;
        }

        label[for="culture"] {
        font-size: 30px;         
        color: #F72585;          
        font-weight: bold;     
        margin-bottom: 6px;
        display: block;
        }



        """
    ),
    icon="images/favicon.ico"
)

def server(input, output, session):

    df = read_data()
    df_reason = pd.read_csv(
        Path(__file__).parent / "data/3_out_reason.csv", delimiter=","
    )

    df_outflow = pd.read_csv(
        Path(__file__).parent / "data/df_outflow.csv", delimiter=","
    )

    df_job = pd.read_csv(
        Path(__file__).parent / "data/df_job.csv", delimiter=","
        )

    df_plot = pd.read_csv(
        Path(__file__).parent / "data/df_plot.csv", delimiter=","
        )

    df_sorted = pd.read_csv(
        Path(__file__).parent/'data/df_sorted.csv', delimiter=",")

    df_education1 = pd.read_csv(
        Path(__file__).parent/'data/df_education1.csv', delimiter=",")    
    
    df_long = pd.read_csv(
        Path(__file__).parent/'data/df_long.csv', delimiter=",")    

    curture_0 = pd.read_csv(
        Path(__file__).parent/'data/curture_0.csv', delimiter=",")    

    df_hos = pd.read_csv(
        Path(__file__).parent/'data/df_hos.csv', delimiter=",")    
    
    df_병합 = pd.read_csv(
        Path(__file__).parent/'data/df_병합_주택노후화.csv', delimiter=",")    


    @reactive.Calc
    @output
    @render_plotly_streaming()
    
    def pieplot_0():
        selected_years = int(input.years()),
        df_filtered = df_reason[df_reason['year'] == selected_years]

        arc_layer_inspired_palette = [
            "#F72585",  # 강렬한 핑크 레드
            "#B5179E",  # 딥 퍼플 핑크
            "#7209B7",  # 진한 퍼플
            "#560BAD",  # 다크 바이올렛
            "#480CA8",  # 다크 퍼플
            "#3A0CA3",  # 퍼플 블루
            "#3F37C9",  # 딥 인디고
            "#4361EE",  # 블루 퍼플
            "#4895EF",  # 밝은 블루 퍼플
        ]

        fig0 = px.pie(
            df_filtered,
            names="reason",
            values="reason_count",
            hole=0.3,
            labels={"reason": "사유", "reason_count": "사유 빈도 수"},
            template="plotly_dark",
            color_discrete_sequence=arc_layer_inspired_palette,
        )

        fig0.update_traces(
            textinfo="label+percent",
            textfont=dict(size=25, color="white"),
            marker=dict(
                line=dict(color="rgba(255,255,255,0.7)", width=2.5)
            ),
            hoverinfo="label+percent+value"
        )

        fig0.update_layout(
            title={
                'text': "<b>이탈 사유</b><br><span style='font-size:14px'>",
                'x': 0.4,
                'xanchor': 'center',
                'font': dict(color="white", size=30),
            },
            paper_bgcolor="#272c3d",
            plot_bgcolor="#272c3d",
            legend=dict(
                font=dict(color="white", size=28),
                bgcolor="rgba(0,0,0,0)"
            ),
            margin=dict(t=80, b=20, l=20, r=20),
            showlegend=True
        )

        return fig0
    
    @reactive.Calc
    @output
    @render_plotly_streaming()
    
    def pieplot_1():
        arc_layer_inspired_palette = [
            "#F72585",  # 강렬한 핑크 레드
            "#B5179E",  # 딥 퍼플 핑크
            "#7209B7",  # 진한 퍼플
            "#560BAD",  # 다크 바이올렛
            "#480CA8",  # 다크 퍼플
            "#3A0CA3",  # 퍼플 블루
            "#3F37C9",  # 딥 인디고
            "#4361EE",  # 블루 퍼플
            "#4895EF",  # 밝은 블루 퍼플
        ]


        selected_industry = input.industry()
        pull_vals = [0.15 if "영천" in r else 0 for r in df_plot["지역별"]]

        fig = px.pie(
                df_plot,
                names="지역명",
                values=selected_industry,
                hole=0.3,
                template="plotly_dark",
                color_discrete_sequence=arc_layer_inspired_palette
            )

        fig.update_traces(
                pull=pull_vals,
                textinfo="label+percent",
                textfont=dict(size=25, color="white"),
                textposition='auto',
                marker=dict(
                    line=dict(color="rgba(255,255,255,0.7)", width=2.5)
                ),
                hoverinfo="label+percent+value"
            )

        fig.update_layout(
                height=900,
                width=900,
                title={
                    'text': f"<b>지역별 {selected_industry} 종사자 분포</b><br><span style='font-size:14px'>",
                    'x': 0.45,
                    'xanchor': 'center',
                    'font': dict(color="white", size=28),
                },
                # annotations=[dict(
                #     text= f"<b>{selected_industry}</b>",
                #     x=0.5, y=0.5,
                #     font_size=16,
                #     font_color="#F72585",
                #     showarrow=False
                # )],
                paper_bgcolor="#272c3d",  # 더 어두운 백그라운드 (밤하늘 느낌)
                plot_bgcolor="#272c3d",
                legend=dict(
                    font=dict(color="white", size=12),
                    bgcolor="rgba(0,0,0,0)"
                ),
                margin=dict(t=80, b=20, l=20, r=20),
                showlegend=False
            )

        return fig

    @reactive.Calc
    @output
    @render.ui()
    def arclayer():
        selected_year = int(input.years())
        df_filtered = df_outflow[df_outflow['year'] == selected_year]
        arc_layer3 = pdk.Layer(
            "ArcLayer",
            data=df_filtered,
            get_width="in_cut",
            get_source_position=["src_lat", "src_lnd"],
            get_target_position=["w_lat", "w_lnd"],
            get_tilt=10,
            get_source_color='[202,223,239]',
            get_target_color='[198,0,124]',
            pickable=True,
            auto_highlight=True,
            )
        view_state = pdk.ViewState(
            latitude=36.5,
            longitude=127.8,
            bearing=0,
            pitch=30,
            zoom=6
            )
        TOOLTIP_TEXT = {"html": "{in_cnt} household <br /> output : {SRC_SIGUNGU_NM} <br /> input : {SIGUNGU_NM}"}
        r1 = pdk.Deck(arc_layer3, initial_view_state=view_state, tooltip=TOOLTIP_TEXT)
        return ui.tags.iframe(
            srcDoc=r1.to_html(as_string=True, notebook_display=False),
            style="width:100%; height:800px; border:none;")

    @reactive.Calc
    @output
    @render_plotly_streaming()
    def barplot_0():
            selected_house = input.house()
            arc_layer_inspired_palette = [
                    "#F72585",  # 강렬한 핑크 레드
                    "#B5179E",  # 딥 퍼플 핑크
                    "#7209B7",  # 진한 퍼플
                    "#560BAD",  # 다크 바이올렛
                    "#480CA8",  # 다크 퍼플
                    "#3A0CA3",  # 퍼플 블루
                    "#4361EE"  # 블루 퍼플
                    ]
            df_sorted['formatted_text'] = df_sorted[selected_house].apply(lambda x: f"{x:,}")    
            fig3 = px.bar(
                df_sorted,
                x="행정구역",
                y=selected_house,
                color="행정구역",
                text='formatted_text',
                labels={
                    "행정구역": "지역구분",
                    selected_house: selected_house,
                },
                template="plotly_dark",
                color_discrete_sequence=arc_layer_inspired_palette,
            )
    
            fig3.update_traces(
                textfont=dict(color="white", size=25),
                marker_line_width=1.5,
                marker_line_color="rgba(255,255,255,0.6)"
            )
    
            fig3.update_layout(
                height=1000,
                xaxis={'categoryorder': 'array', 'categoryarray': df_sorted['행정구역'].tolist(),
                       'tickfont':dict(size=25, color="white")},
                xaxis_title=dict(font=dict(size=30,color='white')),
                
                yaxis=dict(title=dict(font=dict(size=30, color="white")),
                tickfont=dict(size=25, color="white")),
                yaxis_title=dict(font=dict(size=30, color='white')),
                plot_bgcolor="#272c3d",
                paper_bgcolor="#272c3d",
                font=dict(color="white"),
                title=dict(
                    text = f"<b>{selected_house}</b>",
                    x=0.5,
                    xanchor='center',
                    font=dict(color="white", size=30)
                ),
                margin=dict(t=80, b=60, l=40, r=20),
                legend=dict(
                    font=dict(color="white", size=12),
                    bgcolor="rgba(0,0,0,0)"
                ),showlegend=False
            )
    
            return fig3
    
    @reactive.Calc
    @output
    @render_plotly_streaming()
    def barplot_1():
        selected_culture = input.culture()
        arc_layer_inspired_palette = [
            "#F72585",  # 강렬한 핑크 레드
            "#B5179E",  # 딥 퍼플 핑크
            "#7209B7",  # 진한 퍼플
            "#560BAD",  # 다크 바이올렛
            "#480CA8",  # 다크 퍼플
            "#3A0CA3",  # 퍼플 블루
            "#4361EE",  # 블루 퍼플
        ]
    
        fig3 = px.bar(
            curture_0,
            x="region",
            y=selected_culture,
            color="region",
            text=selected_culture,
            labels={
                "region": "지역구분",
                selected_culture: selected_culture,
            },
            template="plotly_dark",
            color_discrete_sequence=arc_layer_inspired_palette,
        )
    
        fig3.update_traces(
            textfont=dict(color="white", size=25),
            marker_line_width=1.5,
            marker_line_color="rgba(255,255,255,0.6)"
        )
    
        fig3.update_layout(
            xaxis={'categoryorder': 'array', 'categoryarray': curture_0['region'].tolist(),
                   'tickfont':dict(size=25, color="white")},
            
            xaxis_title=dict(font=dict(size=30,color='white')),
            
            yaxis=dict(title=dict(font=dict(size=30, color="white")),
            tickfont=dict(size=25, color="white")
            ),
            
            yaxis_title=dict(font=dict(size=30, color='white')),
            
            plot_bgcolor="#272c3d",
            paper_bgcolor="#272c3d",
            font=dict(color="white"),
            title=dict(
                text=f"<b>문화ㆍ복지 요인</b><br><span style='font-size:25px'>{selected_culture}</span>",
                x=0.5,
                xanchor='center',
                font=dict(color="white", size=35)
            ),
            margin=dict(t=80, b=60, l=40, r=20),
            legend=dict(
                font=dict(color="white", size=20),
                bgcolor="rgba(0,0,0,0)"
            ),showlegend=False
        )
    
        return fig3
    
    @reactive.Calc
    @output
    @render_plotly_streaming()
    def barplot_2():
        selected_hospital = input.hospital()
        arc_layer_inspired_palette = [
            "#F72585",  # 강렬한 핑크 레드
            "#B5179E",  # 딥 퍼플 핑크
            "#7209B7",  # 진한 퍼플
            "#560BAD",  # 다크 바이올렛
            "#480CA8",  # 다크 퍼플
            "#3A0CA3",  # 퍼플 블루
            "#4361EE",  # 블루 퍼플
        ]

        fig3 = px.bar(
            df_hos,
            x="region",
            y=selected_hospital,
            color="region",
            text=selected_hospital,
            labels={
                "region": "지역구분",
                selected_hospital : selected_hospital ,
            },
            template="plotly_dark",
            color_discrete_sequence=arc_layer_inspired_palette,
        )

        fig3.update_traces(
            textfont=dict(color="white", size=25),
            marker_line_width=1.5,
            marker_line_color="rgba(255,255,255,0.6)"
        )

        fig3.update_layout(
            xaxis={'categoryorder': 'array', 'categoryarray': df_hos['region'].tolist(),
                   'tickfont':dict(size=25, color="white")},
            
            xaxis_title=dict(font=dict(size=30,color='white')),
            
            yaxis=dict(title=dict(font=dict(size=30, color="white")),
            tickfont=dict(size=25, color="white")
            ),
            
            yaxis_title=dict(font=dict(size=30, color='white')),
            
            plot_bgcolor="#272c3d",
            paper_bgcolor="#272c3d",
            font=dict(color="white"),
            title=dict(text=f"<b>의료 요인</b><br><span style='font-size:25px'>{selected_hospital}</span>",
                x=0.5,
                xanchor='center',
                font=dict(color="white", size=35)
            ),
            margin=dict(t=80, b=60, l=40, r=20),
            legend=dict(
                font=dict(color="white", size=12),
                bgcolor="rgba(0,0,0,0)"
            ),showlegend=False
        )

        return fig3
    
    @reactive.Calc
    @output
    @render_plotly_streaming()
    def barplot_3():
        색상팔레트 = ["#F72585", "#B5179E", "#7209B7", "#560BAD"]

        fig = px.bar(
            df_병합,
            x="행정구역",
            y="비율",
            color="주택유형",
            text="표시텍스트",
            labels={
                "행정구역": "행정구역",
                "비율": "비율 (%)",
                "주택유형": "주택 유형"
            },
            template="plotly_dark",
            color_discrete_sequence=색상팔레트
        )

        # 텍스트와 막대 스타일 설정
        fig.update_traces(
            textfont=dict(color="white", size=25),
            marker_line_width=1.2,
            marker_line_color="rgba(255,255,255,0.5)"
        )

        # 레이아웃 설정
        fig.update_layout(
            xaxis={'tickfont':dict(size=25, color="white")},
            xaxis_title=dict(font=dict(size=30,color='white')),
            yaxis=dict(title=dict(font=dict(size=30, color="white")),
            tickfont=dict(size=25, color="white")
            ),
            
            yaxis_title=dict(font=dict(size=30, color='white')),
            height=1000,
            barmode="stack",
            plot_bgcolor="#272c3d",
            paper_bgcolor="#272c3d",
            font=dict(color="white"),
            title=dict(
                text="<b>30년 이상 노후 주택 비율 및 가구 수</b>",
                x=0.5,
                xanchor='center',
                font=dict(color="white", size=35)
            ),
            margin=dict(t=80, b=60, l=40, r=20),
            legend=dict(
                title="",
                font=dict(color="white", size=35),
                bgcolor="rgba(0,0,0,0)"
            )
        )

        return fig

    
    @reactive.Calc
    @output
    @render_plotly_streaming()
    def treemap_0():
        region_total = df_education1.groupby('region')['count'].sum().to_dict()
        total_schools = df_education1['count'].sum()

        labels = []
        parents = []
        values = []
        hover_texts = []
        colors = []

        # Arc Layer 스타일 색상
        arc_layer_colors = [
            "#F72585", "#B5179E", "#7209B7", "#560BAD",
            "#480CA8", "#3A0CA3", "#3F37C9", "#4361EE", "#4895EF"
        ]

        color_map = {}

        # 지역 노드 추가
        for i, (region, group) in enumerate(df_long.groupby('region')):
            region_sum = group['count'].sum()
            proportion_total = region_sum / total_schools

            labels.append(region)
            parents.append("")
            values.append(region_sum)
            hover_texts.append(
                f"<b>{region}</b><br>학교 수: {region_sum}개<br>전체 학교 비중: {proportion_total:.2%}"
            )
            color_map[region] = arc_layer_colors[i % len(arc_layer_colors)]
            colors.append(color_map[region])

            # 학교 수준 자식 노드 추가
            for _, row in group.iterrows():
                school_count = row['count']
                proportion_region = school_count / region_sum

                labels.append(row['school_level'])
                parents.append(region)
                values.append(school_count)
                hover_texts.append(
                    f"{region} - {row['school_level']}<br>학교 수: {school_count}개<br>지역 내 비중: {proportion_region:.2%}"
                )
                colors.append(color_map[region])
        
        fig = go.Figure(go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            hovertext=hover_texts,
            hoverinfo="text",
            marker=dict(colors=colors, line=dict(width=1.5, color='white')),
            branchvalues="total",
            textinfo='label+value+percent parent',
            textfont=dict(color='white',size=25)
        ))

        fig.update_layout(
            title={
                'text': "<b>교육 요인</b><br><span style='font-size:25px'>학교 수준별 학교 수</span>",
                'x': 0.5,
                'xanchor': 'center',
                'font': dict(color="white", size=35),
            },
            paper_bgcolor="#272c3d",
            plot_bgcolor="#272c3d",
            font=dict(color="white",size=20),
            margin=dict(t=100, b=0, l=0, r=0),
            height=800
        )

        return fig

    
    @render.data_frame  
    def yc_df():
        selected_industry = input.industry()
        df_yc = df_job[df_job['지역별'] == '경상북도 영천시'][['지역별', selected_industry]]
        return render.DataTable(df_yc) 
    
    @output
    @render_plotly_streaming()
    def diff_df():
        selected_industry = input.industry()
        df = df_job[['지역별', selected_industry, selected_industry + '_차이_비율']]
        target_row = df[df["지역별"] == "경상북도 영천시"]
        other_rows = df[df["지역별"] != "경상북도 영천시"]
        df_new = pd.concat([target_row, other_rows], ignore_index=True)

        value_col = df_new[selected_industry].apply(lambda x: f"{x:,}")

        colors = [
            "white" if region == "경상북도 영천시" else
            ("red" if "▲" in val else "blue")
            for region, val in zip(df_new["지역별"], df_new[selected_industry + '_차이_비율'])
            ]
        fig = go.Figure(
            data=[go.Table(
                header=dict(
                    values=["지역별", selected_industry, "차이 비율"],
                    fill_color='#1e1e2f',
                    font=dict(
                        color='white', size=25),
                    align='left'
                ),
                cells=dict(
                    values=[df_new["지역별"], value_col, df_new[selected_industry + '_차이_비율']],
                    fill_color='#272c3d',
                    font=dict(
                        color=['white',
                               'white',
                               colors
                                     ], size=25),
                    align='left',
                    height=30
                )
            )]
        )

        fig.update_layout(
            height=1000,
            width=400,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='#272c3d'
        )

        return fig 
    
    @output
    @render_plotly_streaming()
    def get_top10_table():
        selected_year = int(input.years())
        df_filtered = df_outflow[df_outflow['year'] == selected_year]

        # in_cnt 기준 정렬 후 상위 10개 추출
        df_top10 = df_filtered[['SIGUNGU_NM', 'in_cnt']].sort_values(
            'in_cnt', ascending=False).head(25).reset_index(drop=True)

        # 천 단위 콤마 포맷 적용
        df_top10['in_cnt'] = df_top10['in_cnt'].apply(lambda x: f"{x:,}")

        # Plotly Table 생성
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=["<b>이탈 top 25 </b>", "<b>이탈 세대수</b>"],
                fill_color="#1e1e2f",
                align='center',
                font=dict(color='white', size=25)
            ),
            cells=dict(
                values=[df_top10['SIGUNGU_NM'], df_top10['in_cnt']],
                fill_color="#272c3d",
                align='left',
                font=dict(color='white', size=25),
                height=40
            )
        )])

        fig.update_layout(
            paper_bgcolor="#272c3d",
            margin=dict(t=20, b=20, l=20, r=20)
        )

        return fig

    @render.ui
    def outflow_value_box1():
        selected_year = int(input.years())
    # 예시: 2024년도만 필터링해서 합산
        df = read_outflow_total()
        selected_year = selected_year  # → 나중엔 input에서 받아올 수도 있음
        value = df[df['    Year'] == selected_year]['count'].sum()
        

        return ui.value_box(
                title="영천시 이탈 세대수",
                showcase=faicons.icon_svg(
                    "people-group", width="50px", fill="#F72585 !important"
                ),
                value=f"{value:,} 세대",  # 천 단위 쉼표 표시
                class_="value-box"
            )
    
    @render.ui
    def outflow_value_box2():
        selected_year = int(input.years())
    # 예시: 2024년도만 필터링해서 합산
        df = read_outflow_total()
        selected_year = selected_year  # → 나중엔 input에서 받아올 수도 있음
        value = df[df['    Year'] == selected_year]['out_rate'].values[0]
        

        return ui.value_box(
                title="전년 대비 이탈 증감률",
                showcase=faicons.icon_svg(
                    "people-group", width="50px", fill="#F72585 !important"
                ),
                value=f"{value}%",  # 천 단위 쉼표 표시
                class_="value-box"
            )

    @render.ui
    def outflow_value_box3():
        selected_year = int(input.years())
    
        df = read_outflow_total()
        selected_year = selected_year  
        value = len(df_outflow[df_outflow['year'] == selected_year]['SIGUNGU_NM'].unique())
        
        return ui.value_box(
                title="이탈 지역(시군구) 수",
                showcase=faicons.icon_svg(
                    "people-group", width="50px", fill="#F72585 !important"
                ),
                value=f"{value}",
                class_="value-box"
            )

static_dir = Path(__file__).parent / "static"
app = App(app_ui, server, static_assets=static_dir)