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

model = st.radio('Какова модель осуществления заказов', ['MTS (Пополнению переходящего запаса)', 'MTO (Заказ вручную)'], index=0)

if model == 'MTS (Пополнению переходящего запаса)':
  optimum_inventory_level = 
if model == 'MTO (Заказ вручную)':
  optimum_inventory_level = 0
lead_time_
