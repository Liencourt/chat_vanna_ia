import streamlit as st
from googletrans import Translator
from vanna.remote import VannaDefault

@st.cache_resource(ttl=3600)
def setup_vanna():
    vn = VannaDefault(api_key=st.secrets.get("VANNA_API_KEY"), model='chat-ndp2')
    vn.connect_to_postgres(host="localhost", port=5432,user="postgres",dbname="dwccd",
                           password=st.secrets.get("DB_PASSWORD"))
    return vn

@st.cache_data(show_spinner="Gerando perguntas de exemplo ...")
def generate_questions_cached():
    vn = setup_vanna()
    return vn.generate_questions()


@st.cache_data(show_spinner="Gerando SQL Query ...")
def generate_sql_cached(question: str):
    vn = setup_vanna()
    return vn.generate_sql(question=question, allow_llm_to_see_data=True)

@st.cache_data(show_spinner="Verificando se o SQL é Válido ...")
def is_sql_valid_cached(sql: str):
    vn = setup_vanna()
    return vn.is_sql_valid(sql=sql)

@st.cache_data(show_spinner="Rodando SQL query ...")
def run_sql_cached(sql: str):
    vn = setup_vanna()
    return vn.run_sql(sql=sql)

@st.cache_data(show_spinner="Verificando se podemos gerar um gráfico ...")
def should_generate_chart_cached(question, sql, df):
    vn = setup_vanna()
    return vn.should_generate_chart(df=df)

@st.cache_data(show_spinner="Gerando o codigo do plotly ...")
def generate_plotly_code_cached(question, sql, df):
    vn = setup_vanna()
    code = vn.generate_plotly_code(question=question, sql=sql, df=df)
    return code


@st.cache_data(show_spinner="Rodando o codigo Plotly ...")
def generate_plot_cached(code, df):
    vn = setup_vanna()
    return vn.get_plotly_figure(plotly_code=code, df=df)


@st.cache_data(show_spinner="Gerando Questões Sugeridas ...")
def generate_followup_cached(question, sql, df):
    vn = setup_vanna()

    return vn.generate_followup_questions(question=question, sql=sql, df=df)

@st.cache_data(show_spinner="Gerando Resumo ...")
def generate_summary_cached(question, df):
    vn = setup_vanna()
    summary = vn.generate_summary(question=question, df=df)
    translator = Translator()
    translated_summary = translator.translate(summary, src='en', dest='pt').text
    return translated_summary