import time
import streamlit as st
import pandas as pd
from io import BytesIO
from modulos.vanna_calls import (
    generate_questions_cached,
    generate_sql_cached,
    run_sql_cached,
    generate_plotly_code_cached,
    generate_plot_cached,
    generate_followup_cached,
    should_generate_chart_cached,
    is_sql_valid_cached,
    generate_summary_cached
)
def to_excel_(df: pd.DataFrame):
    in_memory_fp = BytesIO()
    df.to_excel(in_memory_fp)
    # Write the file out to disk to demonstrate that it worked.
    in_memory_fp.seek(0, 0)
    return in_memory_fp.read()
avatar_url = "img/chat-bot.webp"

st.set_page_config(layout="wide",page_title="Chat NDP",page_icon=avatar_url)

st.sidebar.title("Configurações")
st.sidebar.checkbox("Mostrar SQL", value=True, key="show_sql")
st.sidebar.checkbox("Mostrar Tabela", value=True, key="show_table")
st.sidebar.checkbox("Mostrar codigo Plotly", value=True, key="show_plotly_code")
st.sidebar.checkbox("Mostrar Gráficos", value=True, key="show_chart")
st.sidebar.checkbox("Mostrar Resumo", value=True, key="show_summary")
st.sidebar.checkbox("Mostrar Questões sugeridas", value=True, key="show_followup")
st.sidebar.button("Nova Pergunta", on_click=lambda: set_question(None), use_container_width=True)

#st.title("Chat NDP")
# st.sidebar.write(st.session_state)


def set_question(question):
    st.session_state["my_question"] = question


assistant_message_suggested = st.chat_message(
    "assistant", avatar=avatar_url
)
if assistant_message_suggested.button("Clique aqui para questões sugeridas"):
    st.session_state["my_question"] = None
    questions = generate_questions_cached()
    for i, question in enumerate(questions):
        time.sleep(0.05)
        button = st.button(
            question,
            on_click=set_question,
            args=(question,),
        )

my_question = st.session_state.get("my_question", default=None)

if my_question is None:
    my_question = st.chat_input(
        "Pergunte - me sobre seus dados",
    )


if my_question:
    st.session_state["my_question"] = my_question
    user_message = st.chat_message("user")
    user_message.write(f"{my_question}")

    sql = generate_sql_cached(question=my_question)

    if sql:
        if is_sql_valid_cached(sql=sql):
            if st.session_state.get("show_sql", True):
                assistant_message_sql = st.chat_message(
                    "assistant", avatar=avatar_url
                )
                assistant_message_sql.code(sql, language="sql", line_numbers=True)
        else:
            assistant_message = st.chat_message(
                "assistant", avatar=avatar_url
            )
            assistant_message.write(sql)
            assistant_message = st.chat_message(
                "assistant", avatar=avatar_url
            )
            assistant_message.error("O comando acima não será executado pois não se trata de uma consulta")
            st.stop()

        df = run_sql_cached(sql=sql)

        if df is not None:
            st.session_state["df"] = df

        if st.session_state.get("df") is not None:
            if st.session_state.get("show_table", True):
                df = st.session_state.get("df")
                assistant_message_table = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                df_download = pd.DataFrame(df)
                df_downloads = to_excel_(df_download)
                st.download_button('Download Excel', df_downloads,file_name='dados.xlsx',key='df_downloads')
                if len(df) > 10:
                    assistant_message_table.text("Primeiras 10 linhas")
                    assistant_message_table.dataframe(df.head(10),use_container_width=True,hide_index=True)

                else:
                    assistant_message_table.dataframe(df,use_container_width=True)


            if should_generate_chart_cached(question=my_question, sql=sql, df=df):

                code = generate_plotly_code_cached(question=my_question, sql=sql, df=df)

                if st.session_state.get("show_plotly_code", False):
                    assistant_message_plotly_code = st.chat_message(
                        "assistant",
                        avatar=avatar_url,
                    )
                    assistant_message_plotly_code.code(
                        code, language="python", line_numbers=True
                    )

                if code is not None and code != "":
                    if st.session_state.get("show_chart", True):
                        assistant_message_chart = st.chat_message(
                            "assistant",
                            avatar=avatar_url,
                        )
                        fig = generate_plot_cached(code=code, df=df)
                        if fig is not None:
                            assistant_message_chart.plotly_chart(fig)
                        else:
                            assistant_message_chart.warning("Não foi possivel gerar o gráfico")

            if st.session_state.get("show_summary", True):
                assistant_message_summary = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                summary = generate_summary_cached(question=my_question, df=df)
                if summary is not None:
                    assistant_message_summary.text(summary)

            if st.session_state.get("show_followup", True):
                assistant_message_followup = st.chat_message(
                    "assistant",
                    avatar=avatar_url,
                )
                followup_questions = generate_followup_cached(
                    question=my_question, sql=sql, df=df
                )
                st.session_state["df"] = None

                if len(followup_questions) > 0:
                    assistant_message_followup.text(
                        "Aqui tem algumas preguntas sugeridas"
                    )
                    #imprime as primeiras 5 questões
                    for question in followup_questions[:5]:
                        assistant_message_followup.button(question, on_click=set_question, args=(question,))

    else:
        assistant_message_error = st.chat_message(
            "assistant", avatar=avatar_url
        )
        assistant_message_error.error("Não foi possivel gerar SQL para essa questão")