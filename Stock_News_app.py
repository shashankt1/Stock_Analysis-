#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = dash.Dash(__name__)

def get_stock_news(page_number):
    headlines = []
    linkz = []
    resp = requests.get(f"https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms?page={page_number}")
    soup = BeautifulSoup(resp.content, features='xml')
    k = soup.findAll('title')
    lnk = soup.findAll('link')

    for txt in k:
        headlines.append(txt.get_text())

    for links in lnk:
        linkz.append(links.get_text())

    linkz = linkz[2:len(linkz)]
    headlines = headlines[2:len(headlines)]

    return list(zip(headlines, linkz))

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)['compound']
    return sentiment_score

app.layout = html.Div([
    html.H1("Stock News Headlines"),
    html.Ul(
        id='news-list',
        children=[
            html.Li(
                f"{headline} - {link}",
                id=f'item-{i}',
                style={'color': 'green' if analyze_sentiment(headline) >= 0 else 'red'}
            )
            for i, (headline, link) in enumerate(get_stock_news(1))  # Start with page 1
        ]
    ),
    html.Button('Previous Page', id='prev-page-button', n_clicks=0, style={'margin-top': '10px'}),
    html.Button('Next Page', id='next-page-button', n_clicks=0, style={'margin-top': '10px'}),
    html.Div(id='dummy-output', style={'display': 'none'}),
    dcc.Store(id='page-number-store', data=1)
])

@app.callback(
    [Output('dummy-output', 'children'),
     Output('page-number-store', 'data')],
    [Input('next-page-button', 'n_clicks'),
     Input('prev-page-button', 'n_clicks')],
    [State('page-number-store', 'data')]
)
def update_news_list(next_clicks, prev_clicks, current_page):
    # Determine which button was clicked
    ctx = dash.callback_context
    triggered_id = ctx.triggered_id

    if triggered_id == 'next-page-button.n_clicks':
        page_number = current_page + 1
    elif triggered_id == 'prev-page-button.n_clicks':
        page_number = max(1, current_page - 1)
    else:
        page_number = current_page

    news_list = [
        html.Li(
            f"{headline} - {link}",
            id=f'item-{i}',
            style={'color': 'green' if analyze_sentiment(headline) >= 0 else 'red'}
        )
        for i, (headline, link) in enumerate(get_stock_news(page_number))
    ]
    return news_list, page_number

@app.callback(
    Output('news-list', 'children'),
    [Input('dummy-output', 'children')]
)
def update_news_display(news_list):
    return news_list

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)


# In[3]:


import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta

app = dash.Dash(__name__)

def get_stock_news(page_number, start_date=None, end_date=None):
    # Fetch news based on date range
    date_filter = f"&sd={start_date.strftime('%Y%m%d')}" if start_date else ""
    date_filter += f"&ed={end_date.strftime('%Y%m%d')}" if end_date else ""

    headlines = []
    linkz = []
    resp = requests.get(f"https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms?page={page_number}{date_filter}")
    soup = BeautifulSoup(resp.content, features='xml')
    k = soup.findAll('title')
    lnk = soup.findAll('link')

    for txt in k:
        headlines.append(txt.get_text())

    for links in lnk:
        linkz.append(links.get_text())

    linkz = linkz[2:len(linkz)]
    headlines = headlines[2:len(headlines)]

    return list(zip(headlines, linkz))

# Real-time updates using Interval component
app.layout = html.Div([
    html.H1("Stock News Headlines"),
    dcc.Input(id='search-bar', type='text', placeholder='Search News'),
    dcc.Dropdown(
        id='sort-dropdown',
        options=[
            {'label': 'Date', 'value': 'date'},
            {'label': 'Sentiment Score', 'value': 'sentiment'}
        ],
        value='date',
        style={'width': '200px'}
    ),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=(datetime.now() - timedelta(days=7)).date(),
        end_date=datetime.now().date(),
        display_format='YYYY-MM-DD'
    ),
    html.Ul(
        id='news-list',
        children=[
            html.Li(
                f"{headline} - {link}",
                id=f'item-{i}',
                style={'color': 'green' if analyze_sentiment(headline) >= 0 else 'red'}
            )
            for i, (headline, link) in enumerate(get_stock_news(1))
        ]
    ),
    html.Button('Previous Page', id='prev-page-button', n_clicks=0, style={'margin-top': '10px'}),
    html.Button('Next Page', id='next-page-button', n_clicks=0, style={'margin-top': '10px'}),
    html.Div(id='dummy-output', style={'display': 'none'}),
    dcc.Store(id='page-number-store', data=1),
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # Update every 1 minute (in milliseconds)
        n_intervals=0
    )
])

@app.callback(
    [Output('dummy-output', 'children'),
     Output('page-number-store', 'data')],
    [Input('interval-component', 'n_intervals'),
     Input('next-page-button', 'n_clicks'),
     Input('prev-page-button', 'n_clicks')],
    [State('page-number-store', 'data')]
)
def update_news_list(n_intervals, next_clicks, prev_clicks, current_page):
    ctx = dash.callback_context
    triggered_id = ctx.triggered_id

    if triggered_id == 'next-page-button.n_clicks':
        page_number = current_page + 1
    elif triggered_id == 'prev-page-button.n_clicks':
        page_number = max(1, current_page - 1)
    else:
        page_number = current_page

    news_list = [
        html.Li(
            f"{headline} - {link}",
            id=f'item-{i}',
            style={'color': 'green' if analyze_sentiment(headline) >= 0 else 'red'}
        )
        for i, (headline, link) in enumerate(get_stock_news(page_number))
    ]
    return news_list, page_number

# New callback for search, sorting, and date range filter
@app.callback(
    Output('news-list', 'children'),
    [Input('dummy-output', 'children'),
     Input('search-bar', 'value'),
     Input('sort-dropdown', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_news_display(news_list, search_query, sort_option, start_date, end_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
    end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

    # Filter news based on search query
    filtered_news = [(headline, link) for headline, link in get_stock_news(1, start_date, end_date)
                     if search_query and search_query.lower() in headline.lower()]

    # Sort news based on selected option
    if sort_option == 'date':
        sorted_news = sorted(filtered_news, key=lambda x: x[0], reverse=True)
    elif sort_option == 'sentiment':
        sorted_news = sorted(filtered_news, key=lambda x: analyze_sentiment(x[0]), reverse=True)
    else:
        sorted_news = filtered_news

    updated_news_list = [
        html.Li(
            f"{headline} - {link}",
            id=f'item-{i}',
            style={'color': 'green' if analyze_sentiment(headline) >= 0 else 'red'}
        )
        for i, (headline, link) in enumerate(sorted_news)
    ]
    return updated_news_list

if __name__ == '__main__':
    app.run_server(debug=True, port=8051)


# In[6]:


import streamlit as st
import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta

def get_stock_news(page_number, start_date=None, end_date=None):
    # Fetch news based on date range
    date_filter = f"&sd={start_date.strftime('%Y%m%d')}" if start_date else ""
    date_filter += f"&ed={end_date.strftime('%Y%m%d')}" if end_date else ""

    headlines = []
    linkz = []
    resp = requests.get(f"https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms?page={page_number}{date_filter}")
    soup = BeautifulSoup(resp.content, features='xml')
    k = soup.findAll('title')
    lnk = soup.findAll('link')

    for txt in k:
        headlines.append(txt.get_text())

    for links in lnk:
        linkz.append(links.get_text())

    linkz = linkz[2:len(linkz)]
    headlines = headlines[2:len(headlines)]

    return list(zip(headlines, linkz))

def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)['compound']
    return sentiment_score

def main():
    st.title("Stock News Headlines")

    # Sidebar components
    search_query = st.sidebar.text_input("Search News", "")
    start_date = st.sidebar.date_input("Start Date", (datetime.now() - timedelta(days=7)).date())
    end_date = st.sidebar.date_input("End Date", datetime.now().date())

    # Fetch news based on user input
    news_list = get_stock_news(1, start_date, end_date)

    # Filter news based on search query
    filtered_news = [(headline, link) for headline, link in news_list
                     if search_query and search_query.lower() in headline.lower()]

    # Display news list
    for i, (headline, link) in enumerate(filtered_news):
        st.write(f"{headline} - {link}")
        st.markdown("---")

if __name__ == '__main__':
    main()


# In[ ]:




