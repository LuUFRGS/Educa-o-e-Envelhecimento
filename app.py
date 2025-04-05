# app.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Filtro de Artigos - Revista Envelhecer", layout="wide")
st.title("🔍 Robô de Filtro - Revista Envelhecer")

# Palavras-chave
palavras_chave = [
    "gerontecnologia",
    "tecnologia para o envelhecimento",
    "mulheres",
    "feminização da velhice",
    "estudos de gênero",
    "envelhecimento"
]

st.markdown("🔑 **Palavras-chave utilizadas:** " + ", ".join(palavras_chave))

@st.cache_data
def buscar_artigos():
    base_url = "https://seer.ufrgs.br/RevEnvelhecer/issue/archive"
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, "html.parser")

    links_edicoes = [a['href'] for a in soup.select("div.obj_issue_summary a.title")]

    resultados = []

    for link in links_edicoes:
        r_edicao = requests.get(link)
        soup_edicao = BeautifulSoup(r_edicao.text, "html.parser")
        artigos = soup_edicao.select("div.obj_article_summary")

        for artigo in artigos:
            titulo = artigo.select_one("div.title").get_text(strip=True)
            autores = artigo.select_one("div.authors").get_text(strip=True)
            link_artigo = artigo.select_one("a")["href"]

            # Tenta pegar o resumo diretamente da página do artigo
            r_artigo = requests.get(link_artigo)
            soup_artigo = BeautifulSoup(r_artigo.text, "html.parser")
            resumo = soup_artigo.select_one("section.article-abstract")
            resumo_texto = resumo.get_text(strip=True) if resumo else ""

            texto = f"{titulo} {resumo_texto}".lower()

            if any(p.lower() in texto for p in palavras_chave):
                resultados.append({
                    "Título": titulo,
                    "Autores": autores,
                    "Resumo": resumo_texto,
                    "Link": link_artigo
                })
    return resultados

if st.button("🔎 Buscar artigos relacionados"):
    with st.spinner("Rastreando a Revista Envelhecer..."):
        dados = buscar_artigos()

        if dados:
            df = pd.DataFrame(dados)
            st.success(f"Encontramos {len(df)} artigo(s) relevante(s)!")
            st.dataframe(df, use_container_width=True)

            # Download como Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Artigos Filtrados')
                writer.save()
            st.download_button(
                label="📥 Baixar resultados em Excel",
                data=output.getvalue(),
                file_name="artigos_relevantes.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhum artigo com as palavras-chave foi encontrado.")
