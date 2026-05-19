#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from pathlib import Path

# -----------------------------------
# STREAMLIT PAGE CONFIG
# -----------------------------------

st.set_page_config(
    page_title="News Scraper Dashboard",
    page_icon="📰",
    layout="wide"
)

st.title("📰 Financial & Political News Dashboard")
st.markdown("Real-time news scraping from multiple news sources.")

# -----------------------------------
# CSV FILE
# -----------------------------------

CSV_PATH = "HistNews.csv"

# Create CSV if it does not exist
if not Path(CSV_PATH).exists():
    df_init = pd.DataFrame(columns=["source", "title", "link"])
    df_init.to_csv(CSV_PATH, index=False)

# -----------------------------------
# GENERIC REQUEST FUNCTION
# -----------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def get_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")

        return None

    except Exception as e:
        st.warning(f"Error loading {url}: {e}")
        return None


# -----------------------------------
# SCRAP FUNCTIONS
# -----------------------------------

def scrap_eleconomista():
    url = "https://www.eleconomista.com.mx/"
    soup = get_soup(url)

    if soup is None:
        return pd.DataFrame()

    html_str = str(soup)

    pattern = r'<h2 class="c-article__title"><a href="([^"]+)"[^>]*>([^<>]+)</a></h2><p'
    matches = re.findall(pattern, html_str)

    rows = []

    for match in matches:
        link = match[0]
        title = match[1].strip()

        if link.startswith("/"):
            link = "https://www.eleconomista.com.mx" + link

        rows.append({
            "source": "El Economista",
            "title": title,
            "link": link
        })

    return pd.DataFrame(rows)


def scrap_eleconomista_emp():
    url = "https://www.eleconomista.com.mx/empresas"
    soup = get_soup(url)

    if soup is None:
        return pd.DataFrame()

    html_str = str(soup)

    pattern = r'<h2 class="c-article__title">\s*<a href="([^"]+)".*?>(.*?)</a>\s*</h2>'
    matches = re.findall(pattern, html_str)

    rows = []

    for match in matches:
        link = match[0]
        title = re.sub(r"<.*?>", "", match[1]).strip()

        if link.startswith("/"):
            link = "https://www.eleconomista.com.mx" + link

        rows.append({
            "source": "El Economista Empresas",
            "title": title,
            "link": link
        })

    return pd.DataFrame(rows)


def scrap_eleconomista_eco():
    url = "https://www.eleconomista.com.mx/economia"
    soup = get_soup(url)

    if soup is None:
        return pd.DataFrame()

    html_str = str(soup)

    pattern = r'<h2 class="c-article__title">\s*<a href="([^"]+)".*?>(.*?)</a>\s*</h2>'
    matches = re.findall(pattern, html_str)

    rows = []

    for match in matches:
        link = match[0]
        title = re.sub(r"<.*?>", "", match[1]).strip()

        if link.startswith("/"):
            link = "https://www.eleconomista.com.mx" + link

        rows.append({
            "source": "El Economista Economía",
            "title": title,
            "link": link
        })

    return pd.DataFrame(rows)


def scrap_expansion():
    url = "https://expansion.mx/"
    soup = get_soup(url)

    if soup is None:
        return pd.DataFrame()

    html_str = str(soup)

    pattern = r'href="([^"]+)"[^>]*>([^<]+)</a>\s*</h3>'
    matches = re.findall(pattern, html_str)

    rows = []

    for match in matches:
        link = match[0]
        title = match[1].strip()

        if not link.startswith("http"):
            link = "https://expansion.mx" + link

        rows.append({
            "source": "Expansion",
            "title": title,
            "link": link
        })

    return pd.DataFrame(rows)


def scrap_elfinanciero():
    url = "https://www.elfinanciero.com.mx/"
    soup = get_soup(url)

    if soup is None:
        return pd.DataFrame()

    html_str = str(soup)

    pattern = r'href="([^"]+)"[^>]*>([^<]+)</a></h2>'
    matches = re.findall(pattern, html_str)

    rows = []

    for match in matches:
        link = match[0]
        title = match[1].strip()

        if link.startswith("/"):
            link = "https://www.elfinanciero.com.mx" + link

        rows.append({
            "source": "El Financiero",
            "title": title,
            "link": link
        })

    return pd.DataFrame(rows)


def scrap_cnbc():
    url = "https://www.cnbc.com/business/"
    soup = get_soup(url)

    if soup is None:
        return pd.DataFrame()

    html_str = str(soup)

    pattern = r'<a[^>]*class="Card-title"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
    matches = re.findall(pattern, html_str)

    rows = []

    for match in matches:
        link = match[0]
        title = match[1].strip()

        if link.startswith("/"):
            link = "https://www.cnbc.com" + link

        rows.append({
            "source": "CNBC",
            "title": title,
            "link": link
        })

    return pd.DataFrame(rows)


def scrap_yahoo():
    url = "https://finance.yahoo.com/"
    soup = get_soup(url)

    if soup is None:
        return pd.DataFrame()

    html_str = str(soup)

    pattern = r'href="(https://[^"]+)"[^>]*?><h3[^>]*>(.*?)</h3>'
    matches = re.findall(pattern, html_str)

    rows = []

    for match in matches:
        rows.append({
            "source": "Yahoo Finance",
            "title": match[1].strip(),
            "link": match[0]
        })

    return pd.DataFrame(rows)


# -----------------------------------
# RUN ALL SCRAPERS
# -----------------------------------

@st.cache_data(ttl=1800)
def run_scrap():

    dfs = [
        scrap_eleconomista(),
        scrap_eleconomista_emp(),
        scrap_eleconomista_eco(),
        scrap_expansion(),
        scrap_elfinanciero(),
        scrap_cnbc(),
        scrap_yahoo()
    ]

    df_news = pd.concat(dfs, ignore_index=True)

    # Clean duplicates
    df_news = df_news.drop_duplicates(subset=["title"])

    return df_news


# -----------------------------------
# HISTORICAL NEWS FUNCTION
# -----------------------------------

def hist_news(csv_path, df_news):

    try:
        df_hist = pd.read_csv(csv_path)

    except:
        df_hist = pd.DataFrame(columns=["source", "title", "link"])

    df_hist["Category"] = "Historical"
    df_news["Category"] = "Current"

    df_all = pd.concat([df_hist, df_news], ignore_index=True)

    df_unique = df_all.drop_duplicates(subset="title", keep=False)

    df_filtered = df_unique[df_unique["Category"] == "Current"]

    df_updated = pd.concat([df_hist, df_filtered], ignore_index=True)

    df_updated.to_csv(csv_path, index=False)

    return df_updated


# -----------------------------------
# BUTTON
# -----------------------------------

if st.button("🔄 Refresh News"):

    with st.spinner("Scraping news sources..."):

        df_news = run_scrap()

        df_all_news = hist_news(CSV_PATH, df_news)

        df_current = df_all_news[
            df_all_news["Category"] == "Current"
        ].copy()

        st.success(f"Loaded {len(df_current)} current news articles.")

        # -----------------------------------
        # FILTERS
        # -----------------------------------

        sources = sorted(df_current["source"].unique())

        selected_sources = st.multiselect(
            "Filter by Source",
            options=sources,
            default=sources
        )

        keyword = st.text_input("Search keyword")

        filtered_df = df_current[
            df_current["source"].isin(selected_sources)
        ]

        if keyword:
            filtered_df = filtered_df[
                filtered_df["title"].str.contains(
                    keyword,
                    case=False,
                    na=False
                )
            ]

        # -----------------------------------
        # DISPLAY NEWS
        # -----------------------------------

        st.subheader("📰 Latest News")

        for _, row in filtered_df.iterrows():

            st.markdown(
                f"""
                ### [{row['title']}]({row['link']})
                **Source:** {row['source']}
                ---
                """
            )

        # -----------------------------------
        # DOWNLOAD CSV
        # -----------------------------------

        csv = filtered_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="news.csv",
            mime="text/csv"
        )

else:
    st.info("Click 'Refresh News' to load latest articles.")

