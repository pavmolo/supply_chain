import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random


st.subheader("Рачет уровня запаса")
current_stock = st.number_input("Установите текущий уровень запаса в штуках", value=0)

order_in_process = st.number_input("Установите ранее сделанные, но не выполенные заказы", value=0)

stock_level = current_stock + order_in_process


#st.subheader(f"Уровень запаса: {stock_level} штук")
st.metric("Уровень запаса", f"{stock_level} штук")
st.info('Уровень запаса - это фактический запас в точке хранения плюс уже заказанный, но еще не поставленный товар')

st.subheader("Рачет точки заказа")
sales_3m = st.number_input("Укажите продажи за последние три месяца, руб.", value=0)

days_3m = st.number_input("Укажите количество дней в последних трех месяцах", value=90)

average_day_sales = sales_3m / days_3m
average_day_sales_rounded = np.around(average_day_sales, decimals=2, out=None)

#st.subheader(f"Среднедневные продажи за последние три месяца: {average_day_sales} руб. в день")
st.metric("Среднедневные продажи за последние три месяца", f"{average_day_sales_rounded} руб. в день")

lead_time_for_replenishment = st.number_input("Укажите время в днях от момента заказа до момента поставки", value=0.00, step=0.01)
demand_variation = st.slider("Какова ваш коэффициент вариабельности спроса в процентах", 0, 100, 0, 2)
leadtime_variation = st.slider("Какова ваш коэффициент вариабельности срока поставки (от заказа до поставки) в процентах", 0, 100, 0, 2)
optimum_inventory_level_days = lead_time_for_replenishment * (1 + ((demand_variation / 100) * (leadtime_variation / 100)))
optimum_inventory_level_pieces = optimum_inventory_level_days * average_day_sales
safety_stock_days = optimum_inventory_level_days - lead_time_for_replenishment
reorder_level = safety_stock_days * average_day_sales

sigma_demand = (demand_variation / 100) * average_day_sales
sigma_leadtime = (leadtime_variation / 100) * lead_time_for_replenishment

#st.subheader(f"Оптимальный уровень запаса (в днях): {optimum_inventory_level_days} дней")
#st.subheader(f"Оптимальный уровень запаса (в штуках): {optimum_inventory_level_pieces} штук")
#st.subheader(f"Страховой запас (в днях): {safety_stock_days} дней")
#st.subheader(f"Страховой запас (в штуках): {safety_stock_pieces} штук")

col1, col2 = st.columns(2)
col1.metric("Оптимальный уровень запаса (в днях)", f"{np.around(optimum_inventory_level_days, decimals=2, out=None)} дней")
col2.metric("Оптимальный уровень запаса (в штуках)", f"{np.around(reorder_level, decimals=2, out=None)} штук")

col1, col2 = st.columns(2)
col1.metric("Страховой запас (в днях)", f"{np.around(safety_stock_days, decimals=2, out=None)} дней")
col2.metric("Страховой запас (в штуках)", f"{np.around(reorder_level, decimals=2, out=None)} штук")
st.caption('Страховой запас - это надбавка к необходимому для хранения запасу с целью застраховать от дефицита из-ща двух причин: задержек поставки и всплексков спроса')


st.metric("Уровень (точка) заказа", f"{np.around(reorder_level, decimals=2, out=None)} штук")
st.caption('Точка заказа - это объем запаса, при котором необходимо сделать заказ, чтобы времени хватило до исчерпания запаса к моменту попонения с учетом рисков задержек поставки и изменений спроса')

demand_random_generator = [random.normalvariate(average_day_sales, sigma_demand) for x in range(30)]
#st.subheader(f"Колебания спроса: {demand_random_generator} дней")
leadtime_random_generator = [random.normalvariate(lead_time_for_replenishment, sigma_leadtime) for x in range(30)]

st.subheader("Расчет необходимого заказа")
neded_order = reorder_level - stock_level
if neded_order < 0:
  st.error(f'Заказывать не нужно. До заказа нужно израсходовать{-neded_order}')
else:
  st.metric("Необходимый заказ", f"{neded_order} шт")


fig = px.line(y=demand_random_generator, title='Сгенерированный случайный спрос на основании введенных данных')
st.plotly_chart(fig, use_container_width=True, sharing="streamlit")
fig = px.line(y=leadtime_random_generator, title='Сгенерированный случайный срок от заказа до поставки на основании введенных данных')
st.plotly_chart(fig, use_container_width=True, sharing="streamlit")

st.markdown('''<img src="https://i.ibb.co/HGwb7jb/order-level-illustration.png">''', unsafe_allow_html=True)

#st.area_chart(x=range(30), y=demand_random_generator, width=0, height=0, use_container_width=True)
