import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random

st.subheader('Разработчик: Павел Молотивский')

with st.sidebar:
    st.title('Введите данные для моделирования элемента цепочки поставок (конкретного SKU)')
    st.subheader("Параметры для расчета уровня запаса")
    current_stock = st.number_input("Укажите фактический остаток в месте хранения в штуках", value=20)
    order_in_process = st.number_input("Установите ранее сделанные, но не выполненные заказы на поставку в место хранения", value=200)
    stock_level = current_stock + order_in_process

    st.subheader("Параметры для расчета точки заказа:")
    sales_3m = st.number_input("Укажите объем продаж данного SKU за последние три месяца, шт", value=10000)
    days_3m = st.number_input("Укажите количество дней в последних трех месяцах", value=90)
    lead_time_for_replenishment = 1
    st.subheader(f"Регулярность поставок: {lead_time_for_replenishment} день")

    st.title('Параметры для расчета страхового запаса:')
    demand_variation = st.slider("Каков ваш коэффициент вариабельности спроса в процентах", 0.0, 100.0, 18.0, 0.5)
    leadtime_variation = st.slider("Каков ваш коэффициент вариабельности срока поставки (от заказа до поставки) в процентах", 0, 100, 8, 2)
    safety_multiplicator = st.slider("На сколько изменить страховой запас для избежания дефицита: ", 0.00, 8.00, 1.00, 0.01)

st.title('Приложение по моделированию принятия решения элементом цепочки поставок при ежедневных поставках')
st.metric("Уровень запаса", f"{stock_level} штук")
st.info('Уровень запаса - это фактический запас в точке хранения плюс уже заказанный, но еще не поставленный товар')

average_day_sales = sales_3m / days_3m
st.metric("Среднедневные продажи за последние три месяца", f"{np.around(average_day_sales, decimals=2)} шт в день")

safety_stock_days = lead_time_for_replenishment * ((1 + demand_variation / 100) * (1 + leadtime_variation / 100) - 1) * safety_multiplicator
safety_stock_pieces = safety_stock_days * average_day_sales
optimum_inventory_level_days = lead_time_for_replenishment + safety_stock_days
reorder_level = optimum_inventory_level_days * average_day_sales

col1, col2 = st.columns(2)
col1.metric("Оптимальный уровень запаса (в днях)", f"{np.around(optimum_inventory_level_days, decimals=2)} дней")
col2.metric("Оптимальный уровень запаса (в штуках)", f"{np.around(reorder_level, decimals=2)} штук")

col1, col2 = st.columns(2)
col1.metric("Страховой запас (в днях)", f"{np.around(safety_stock_days, decimals=2)} дней")
col2.metric("Страховой запас (в штуках)", f"{np.around(safety_stock_pieces, decimals=2)} штук")
st.info('Страховой запас - это надбавка к необходимому для хранения запасу с целью застраховать от дефицита из-за задержек поставки и всплесков спроса')

st.metric("Уровень (точка) заказа", f"{np.around(reorder_level, decimals=2)} штук")
st.info('Точка заказа - это объем запаса, при котором необходимо сделать заказ, чтобы времени хватило до исчерпания запаса к моменту пополнения с учетом рисков задержек поставки и изменений спроса')

# Генерация случайных данных
demand_random_generator = [random.normalvariate(average_day_sales, (demand_variation / 100) * average_day_sales) for _ in range(30)]
leadtime_random_generator = [random.normalvariate(lead_time_for_replenishment, (leadtime_variation / 100) * lead_time_for_replenishment) for _ in range(30)]

st.subheader("Расчет необходимого заказа")
needed_order = reorder_level - stock_level
if needed_order < 0:
    st.error(f'Заказывать не нужно. До заказа нужно израсходовать {np.around(-needed_order, decimals=0)} шт')
else:
    st.metric("Необходимый заказ:", f"{np.around(needed_order, decimals=2)} шт")

# Построение графика
df = pd.DataFrame({'День': range(1, 31), 'Спрос': demand_random_generator, 'Время поставки': leadtime_random_generator})
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['День'], y=df['Спрос'], mode='lines+markers', name='Спрос'))
fig.add_trace(go.Scatter(x=df['День'], y=[df['Спрос'].mean()] * 30, mode='lines', name='Средний спрос'))
st.plotly_chart(fig, use_container_width=True)
