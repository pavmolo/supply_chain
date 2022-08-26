import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.subheader("Заполните поля ниже:")
current_stock = st.number_input("Установите текущий уровень запаса в штуках", value=0)

order_in_process = st.number_input("Установите ранее сделанные, но не выполенные заказы", value=0)

stock_level = current_stock + order_in_process


st.subheader(f"Уровень заказа: {stock_level} штук")

sales_3m = st.number_input("Укажите продажи за последние три месяца, руб.", value=0)

days_3m = st.number_input("Укажите количество дней в последних трех месяцах", value=90)

average_day_sales = sales_3m / days_3m

st.subheader(f"Среднедневные продажи за последние три месяца: {average_day_sales} руб. в день")

lead_time_for_replenishment = st.number_input("Укажите время в днях от момента заказа до момента поставки", value=0)
demand_variation = st.slider("Какова ваш коэффициент вариабельности спроса в процентах", 0, 100, 0, 2)
leadtime_variation = st.slider("Какова ваш коэффициент вариабельности срока поставки (от заказа до поставки) в процентах", 0, 100, 0, 2)
optimum_inventory_level_days = lead_time_for_replenishment * (1 + ((demand_variation / 100) * (leadtime_variation / 100)))
optimum_inventory_level_pieces = optimum_inventory_level_days * average_day_sales
safety_stock_days = optimum_inventory_level_days - lead_time_for_replenishment
safety_stock_pieces = safety_stock_days * average_day_sales

sigma_demand = (demand_variation / 100) * average_day_sales
sigma_leadtime = (leadtime_variation / 100) * lead_time_for_replenishment

st.subheader(f"Оптимальный уровень запаса (в днях): {optimum_inventory_level_days} дней")
st.subheader(f"Оптимальный уровень запаса (в штуках): {optimum_inventory_level_pieces} штук")
st.subheader(f"Страховой запас (в днях): {safety_stock_days} дней")
st.subheader(f"Страховой запас (в штуках): {safety_stock_pieces} штук")


demand_random_generator = random.normalvariate(average_day_sales, sigma_demand) for x in range(30)]
st.subheader(f"Колебания спроса: {demand_random_generator} дней")
