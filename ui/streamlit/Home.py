import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from neo4j_driver import run_query
import math

from ui_utils import render_header_svg

st.set_page_config(
    page_title="Offshore Leaks",
    page_icon="images/logo-mark-fullcolor-RGB-transBG.svg",
    layout="wide",
)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
    </style>
    <div style='text-align: center; font-size: 2.5rem; font-weight: 600; font-family: "Roboto"; color: #018BFF; line-height:1; '>ICIJ Offshore Leaks</div>
""", unsafe_allow_html=True)
render_header_svg("images/bottom-header.svg", 200)


# @st.cache_data
def get_data() -> pd.DataFrame:
    return run_query("""
      MATCH (n:Officer) return COUNT(n.name) as count""")

mgr_count = get_data()

placeholder = st.empty()

with placeholder.container():
        companies_count = run_query("""MATCH (n:Entity) return COUNT(n.name) as count""")
        intermediaries_count = run_query("""MATCH (n:Intermediary) return COUNT(n.name) as count""")

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(
            label="Officers",
            value=mgr_count['count'][0]
        )     
        kpi2.metric(
            label="Companies",
            value=companies_count['count'][0]
        )
        kpi3.metric(
            label="Intermediaries",
            value=intermediaries_count['count'][0]
        )

        assets_col = st.columns(1)
        st.markdown("### Popular Intermediaries")
        df_assets = run_query("""
            MATCH (i:Intermediary) RETURN i.name AS intermediary, 
            SIZE([(i)-[]-(e:Entity) | e]) AS entity_connections 
            ORDER BY entity_connections DESC LIMIT 10""")
        size_max_default = 7
        scaling_factor = 5
        fig_assets = px.scatter(df_assets, x="intermediary", y="entity_connections",
                    size="entity_connections", color="intermediary",
                        hover_name="intermediary", log_y=False, 
                        size_max=size_max_default*scaling_factor)
        st.plotly_chart(fig_assets, use_container_width=True)

        # create two columns for charts
        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### Officers with most Companies")
            df = run_query("""
              MATCH p=(m:Officer)-[]-(:Intermediary)-[]->(c:Entity) 
                RETURN m.name as officer, 
                COUNT(m.name) as connections
                ORDER BY connections DESC limit 10""")
            fig = px.scatter(df, x="officer", y="connections",
                      size="connections", color="officer",
                            hover_name="officer", log_y=False, 
                            size_max=size_max_default*scaling_factor)
            st.plotly_chart(fig, use_container_width=True)
            
        with fig_col2:
            st.markdown("### Popular Locations of Officers")
            df = run_query("""
              MATCH (m:Officer) 
                WHERE m.countries IS NOT NULL
                RETURN toUpper(m.countries) as country, 
                count(*) as count
                ORDER BY count DESC limit 10""")
            fig2 = px.scatter(df, x="country", y="count",
                      size="count", color="country",
                            hover_name="country", log_y=False, 
                            size_max=size_max_default*scaling_factor)
            st.plotly_chart(fig2, use_container_width=True)
        