import yfinance as yf

import pandas as pd
import numpy as np
import streamlit as st
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import time

# # # # # #

# Sidebar elements
ticker = st.sidebar.text_input(label = 'Enter a stock ticker', max_chars = 5, value='AAPL')
ticker = ticker.upper()

N = st.sidebar.slider(label = 'Select day range for which to retrieve data', min_value=30,
                      max_value=180, value=30, step=30)

date_N_days_ago = datetime.now() - timedelta(days=N)
start = date_N_days_ago.strftime('%Y-%m-%d')
today = date.today().strftime('%Y-%m-%d')

# # ---

# Main body
st.title("Stock Price Moves Monitor $")
st.write("When do the biggest price moves happen?")
st.write("Regular hours? Extended hours?")
st.write("How often do those moves happen?")
st.write("**Enter your favorite ticker (left) and find out!**")

# # ---

def stock_data(ticker):

    stock_df = yf.download(f'{ticker}', start=start, end=today)[['Open', 'Close']]

    # Modify stock_df: add columns
    stock_df['Close_shifted'] = stock_df.Close.shift()

    stock_df['RegHrs_Δ'] = stock_df.loc[:, 'Close'] - stock_df.loc[:, 'Open']
    stock_df['ExHrs_Δ'] = stock_df.loc[:, 'Open'] - stock_df.loc[:, 'Close_shifted']

    stock_df['RegHrs_Δ_pct'] = ((stock_df['RegHrs_Δ']/stock_df['Open']) * 100)
    stock_df['ExHrs_Δ_pct'] = ((stock_df['ExHrs_Δ']/stock_df['Close_shifted']) * 100)

    return stock_df

stock_df = stock_data(ticker)

# # ---

# Sidebar elements
begin_price = stock_df.iloc[0]['Close']
end_price = stock_df.iloc[-1]['Close']
diff = end_price - begin_price
st.sidebar.metric(label = f'Closing price {N} days ago', value = f'${begin_price:.2f}')
st.sidebar.metric(label = f'Closing price on last trading day', value = f'${end_price:.2f}')
st.sidebar.metric(label = f'Change from {N} days ago', value = f'${diff:.2f}')
# ---

# Main body
st.subheader(f'**{ticker}** price movement insights - past {N} days.')

# ---

reg_pos = 0
reg_neg = 0

for x in (stock_df['RegHrs_Δ_pct']):
    if x > 0:
        reg_pos += 1
    elif x < 0:
        reg_neg += 1
    else:
        pass

reg_labels = [f'Days {ticker} closed ⬆', f'Days {ticker} closed ⬇']
reg_values = [reg_pos, reg_neg]

col1, col2 = st.columns((1,1))

ex_pos = 0
ex_neg = 0

for x in (stock_df['ExHrs_Δ_pct']):
    if x > 0:
        ex_pos += 1
    elif x < 0:
        ex_neg += 1
    else:
        pass

ex_labels = [f'Days {ticker} opened ⬆︎', f'Days {ticker} opened ⬇︎']
ex_values = [ex_pos, ex_neg]

pie_colors = ['#0984e3', '#4b6584']
with col1:
    # Use `hole` to create a donut-like pie chart
    fig_reg = go.Figure(data=[go.Pie(labels=reg_labels,
                                     values=reg_values,
                                     marker_colors = pie_colors,
                                     hole=.4)])
    fig_reg.update_layout(legend_xanchor="center")
    fig_reg.update_traces(textinfo='value', textfont_size=20)
    fig_reg.add_annotation(x= 0.5, y = 0.5,
                    text = f"{ticker}",
                    font = dict(size=20,family='Verdana',
                                color='black'),
                    showarrow = False)
    st.plotly_chart(fig_reg, use_container_width=True)

with col2:
    fig_neg = go.Figure(data=[go.Pie(labels=ex_labels,
                                     values=ex_values,
                                     marker_colors = pie_colors,
                                     hole=.4)])
    fig_neg.update_layout(legend_xanchor="center")
    fig_neg.update_traces(textinfo='value', textfont_size=20)
    fig_neg.add_annotation(x= 0.5, y = 0.5,
                           text = f"{ticker}",
                           font = dict(size=20,family='Verdana',
                                       color='black'),
                           showarrow = False)
    st.plotly_chart(fig_neg, use_container_width=True)

# # #
RegHrsΔ_pct_mean_pos = ((stock_df[stock_df['RegHrs_Δ_pct'] > 0])['RegHrs_Δ_pct']).mean().round(2)
RegHrsΔ_pct_mean_neg = ((stock_df[stock_df['RegHrs_Δ_pct'] < 0])['RegHrs_Δ_pct']).mean().round(2)
ExHrsΔ_pct_mean_pos = ((stock_df[stock_df['ExHrs_Δ_pct'] > 0])['ExHrs_Δ_pct']).mean().round(2)
ExHrsΔ_pct_mean_neg = ((stock_df[stock_df['ExHrs_Δ_pct'] < 0])['ExHrs_Δ_pct']).mean().round(2)

st.subheader(f"Histograms showing % changes in {ticker} price - regular vs extended hours")
st.write("➡︎ Extended hours data represent the net change from **previous trading day's close to "
         "next trading day's open** (after-hours plus pre-market sessions)")

x0 = stock_df['RegHrs_Δ_pct']
x1 = stock_df['ExHrs_Δ_pct']
x0x1 = stock_df.loc[:, ('RegHrs_Δ_pct', 'ExHrs_Δ_pct')]

def twohist_fn():
    with col3:
        fig_x0 = go.Figure(data=[go.Histogram(x=x0, marker_color='#4b6584',
                                              opacity=0.65)])
        fig_x0.update_layout(bargap=0.1,
                          yaxis=dict(
                              title='frequency (days)',
                              titlefont_size=16,
                              tickfont_size=14,),
                          xaxis=dict(
                              title='% change in price',
                              titlefont_size=16,
                              tickfont_size=14,),
                             title=dict(text=f"Regular Hrs (skew = {x0.skew():.2f})"),
                             font=dict(size=15)
                          )

        st.plotly_chart(fig_x0, use_container_width=True)

    with col4:
        fig_x1 = go.Figure(data=[go.Histogram(x=x1,
                                              marker_color='#2d98da',
                                              opacity=0.65)])

        fig_x1.update_layout(bargap=0.1,
                      yaxis=dict(
                          title='frequency (days)',
                          titlefont_size=16,
                          tickfont_size=14,),
                      xaxis=dict(
                          title='% change in price',
                          titlefont_size=16,
                          tickfont_size=14,),
                             title=dict(text=f"Extended Hrs (skew = {x1.skew():.2f})"),
                             font=dict(size=15)
                      )

        st.plotly_chart(fig_x1, use_container_width=True)

def dist_fn():
    dist_data = [x0, x1]

    dist_labels = ['Reg Hours', 'Ex Hours']
    dist_colors = ['#4b6584', '#2d98da']

    # Create distplot
    dist_fig = ff.create_distplot(dist_data,
                                  dist_labels,
                                  colors=dist_colors,
                                  bin_size=.25, show_rug=False,
                             show_curve=False)

    dist_fig.update_layout(title_text='Ex & Reg Hrs Data Overlap',
                           bargap=0,
                           yaxis=dict(
                               title='frequency (proportional)',
                               titlefont_size=16,
                               tickfont_size=14,),
                           xaxis=dict(
                               title='% change in price',
                               titlefont_size=16,
                               tickfont_size=14,),
                           )
    st.plotly_chart(dist_fig)

with st.container():
    hist_type = st.selectbox(label = 'Display Regular Hrs and Extended Hrs data on the same plot?',
                             options =
                             ('Separate Reg Hrs and Ex Hrs (2 plots)', 'Overlap Reg Hrs and Ex Hrs (1 plot)'))

with st.container():

    col3, col4 = st.columns((1, 1))

    if hist_type == 'Separate Reg Hrs and Ex Hrs (2 plots)':
        twohist_fn()

    if hist_type == 'Overlap Reg Hrs and Ex Hrs (1 plot)':
        dist_fn()

# multi-level columns
items = pd.MultiIndex.from_tuples([('% change', 'Reg Hours'),('% change', 'Ex Hours')])

# creating a DataFrame
dataFrame = pd.DataFrame([[x0.min(), x1.min()],
                          [x0.mean(),x1.mean()],
                          [ x0.max(), x1.max()]],
                          index=['min', 'mean', 'max'],
                         columns=items)
dataFrame = dataFrame.style.format(precision=2).highlight_max(color='#ffbe76').highlight_min(
    color='#95afc0')

with st.container():

    st.subheader(f"Spread and central tendency (past {N} days)")
    # st.write("Min, mean, max, interquartile range and median")

    col5, col6 = st.columns((0.6, 1))

    with col5:

        st.header("")
        st.header("")
        st.header("")
        st.header("")
        st.header("")

        st.write("Range & mean")
        st.dataframe(dataFrame)

    with col6:

        fig_box = px.box(x0x1, points=False,
                         labels={'value': '% change in price', 'variable': ''},
                         title="Hover cursor over plot to see range, IQR, median"
                         )
        st.plotly_chart(fig_box, use_container_width=True)

# # #
Δ_data = {'mean_Δ': [RegHrsΔ_pct_mean_pos,
                     ExHrsΔ_pct_mean_pos,
                     RegHrsΔ_pct_mean_neg,
                     ExHrsΔ_pct_mean_neg]}

Δ_df = pd.DataFrame(Δ_data,
                    index = ['RegHrs_Δ_up', 'ExHrs_Δ_up', 'RegHrs_Δ_dn', 'ExHrs_Δ_dn'])

Δ_df['color'] = ['#03A9F4' if i > 0 else '#f39c12' for i in Δ_df.mean_Δ]

with st.container():

    st.subheader(f"Mean price changes - Regular Hrs vs Extended Hrs")
    st.write("Here, **up** sessions and **down** sessions are aggregated separately, and discrete means (averages) are calculated.")
    st.write("This clarifies whether the average price movement up or down was greater  "
             "during regular "
             "trading hours or extended hours.")
    st.write("Pattern: 'RegHrs_Δ_up' denotes the mean of all regular-hours sessions **that ended "
             "higher** in the study period.")

    def bar_graph():

        # Use textposition='auto' for direct text
        fig = go.Figure(data=[go.Bar(
            x=Δ_df.index, y=Δ_df['mean_Δ'],
            text=Δ_df['mean_Δ'],
            marker_color= Δ_df['color'],
            textposition='auto')])
        fig.update_layout(
                          yaxis=dict(
                              title='% change in price',
                              titlefont_size=16,
                              tickfont_size=14,),
                          )
        st.plotly_chart(fig)

    bar_graph()




