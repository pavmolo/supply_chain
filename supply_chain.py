import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random


with st.sidebar:
  st.title('Введите данные для моделирования элемента цепочки поставок (конкретного SKU)')
  st.subheader("Параметры для расчета уровня запаса")
  current_stock = st.number_input("Укажите фактический остаток в месте хранения в штуках", value=0)

  order_in_process = st.number_input("Установите ранее сделанные, но не выполенные заказы на поставку в место хранения", value=0)

  stock_level = current_stock + order_in_process
  st.subheader("Параметры для расчета точки заказа:")
  sales_3m = st.number_input("Укажите объем продаж данного SKU за последние три месяца, шт", value=0)
  days_3m = st.number_input("Укажите количество дней в последних трех месяцах", value=90)
  lead_time_for_replenishment = st.slider("Укажите время в днях от момента заказа до момента поставки (оставьте 1 при ежедневных поставках)", 0.00, 20.00, 1.00, 0.01)
  st.title('Параметры для расчета страхового запаса:')
  demand_variation = st.slider("Каков ваш коэффициент вариабельности спроса в процентах", 0, 100, 0, 2)
  leadtime_variation = st.slider("Каков ваш коэффициент вариабельности срока поставки (от заказа до поставки) в процентах", 0, 100, 0, 2)

st.title('Результат моделирования')
#st.subheader(f"Уровень запаса: {stock_level} штук")
st.metric("Уровень запаса", f"{stock_level} штук")
st.info('Уровень запаса - это фактический запас в точке хранения плюс уже заказанный, но еще не поставленный товар')


average_day_sales = sales_3m / days_3m
average_day_sales_rounded = np.around(average_day_sales, decimals=2, out=None)

#st.subheader(f"Среднедневные продажи за последние три месяца: {average_day_sales} руб. в день")
st.metric("Среднедневные продажи за последние три месяца", f"{average_day_sales_rounded} шт в день")


optimum_inventory_level_days = lead_time_for_replenishment * (1 + demand_variation / 100) * ( 1 + leadtime_variation / 100)
reorder_level = optimum_inventory_level_days * average_day_sales
safety_stock_days = optimum_inventory_level_days - lead_time_for_replenishment
safety_stock_pieces = safety_stock_days * average_day_sales

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
col2.metric("Страховой запас (в штуках)", f"{np.around(safety_stock_pieces, decimals=2, out=None)} штук")
st.info('Страховой запас - это надбавка к необходимому для хранения запасу с целью застраховать от дефицита из-ща двух причин: задержек поставки и всплексков спроса')


st.metric("Уровень (точка) заказа", f"{np.around(reorder_level, decimals=2, out=None)} штук")
st.info('Точка заказа - это объем запаса, при котором необходимо сделать заказ, чтобы времени хватило до исчерпания запаса к моменту попонения с учетом рисков задержек поставки и изменений спроса')

demand_random_generator = [random.normalvariate(average_day_sales, sigma_demand) for x in range(30)]
#st.subheader(f"Колебания спроса: {demand_random_generator} дней")
leadtime_random_generator = [random.normalvariate(lead_time_for_replenishment, sigma_leadtime) for x in range(30)]

st.subheader("Расчет необходимого заказа")
neded_order = reorder_level - stock_level
if neded_order < 0:
  st.error(f'Заказывать не нужно. До заказа нужно израсходовать {-neded_order} шт')
else:
  st.metric("Необходимый заказ:", f"{np.around(neded_order, decimals=2, out=None)} шт")

with st.expander("Сгенерированы случайные величины спроса и сроков поставки на основании показателей вариабельности, введенных вами. Нажмите сюда, чтобы посмотреть их"):
  fig = px.line(y=demand_random_generator, title='Сгенерированный случайный спрос на основании введенных данных')
  st.plotly_chart(fig, use_container_width=True, sharing="streamlit")
  fig = px.line(y=leadtime_random_generator, title='Сгенерированный случайный срок от заказа до поставки на основании введенных данных')
  st.plotly_chart(fig, use_container_width=True, sharing="streamlit")
  st.markdown('''<img src="https://i.ibb.co/HGwb7jb/order-level-illustration.png">''', unsafe_allow_html=True)

#st.area_chart(x=range(30), y=demand_random_generator, width=0, height=0, use_container_width=True)

df = pd.DataFrame(demand_random_generator, columns=['demand'], index=range(30))
df['lead_time'] = leadtime_random_generator
df['consumption'] = df['lead_time'] * df['demand']
orders = []
stocks = []
stock_plus_order = []
current_stock_dinamic = current_stock
order_in_process_dinamic = order_in_process
neded_order_dinamic = neded_order
numbers_minus = []
stock_fact_minus = []
numbers_plus = []
stock_fact_plus = []
for i in range(30):
  # Определяем фактический запас прямо перед пополнением
  number_x_minus = i * 100 - 1
  numbers_minus.append(number_x_minus)
  stock_fact_dinamic_minus = current_stock_dinamic - df['consumption'][i]
  stock_fact_minus.append(stock_fact_dinamic_minus)
  
  # Определяем фактический запас сразу после пополнения
  number_x_plus = i * 100 + 1
  numbers_plus.append(number_x_plus)
  stock_fact_dinamic_plus = stock_fact_dinamic_minus + neded_order_dinamic
  stock_fact_plus.append(stock_fact_dinamic_plus)
  
  # Делаем заказ
  neded_order_dinamic = reorder_level - stock_fact_dinamic_plus - order_in_process_dinamic
  if neded_order_dinamic < 0:
    neded_order_dinamic = 0
  orders.append(neded_order_dinamic)
  stocks.append(stock_fact_dinamic_minus)
  current_stock_dinamic = stock_fact_dinamic_plus
  
    
df['orders'] = orders
df['stocks'] = stocks
df['safety_stocks'] = safety_stock_pieces
df['reorder_level'] = reorder_level

df_minus = pd.DataFrame(stock_fact_plus, index = number_x_minus, column = 'fact_stock')
st.table(data=df_minus)

st.subheader("Имитационное моделирование объема запаса / дефицита")
quant_deficit = (df['stocks'] < 0).sum()
st.info(f"Страхового запаса не хватило в {quant_deficit} днях из {df['stocks'].count()}")

#st.area_chart(df['stocks'])

fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['stocks'], fill='tozeroy', name='Запас перед поставкой'))
fig.add_trace(go.Scatter(x=df.index, y=df['stock_level_before_replenishment'], fill='tozeroy', name='Уровень запаса перед пополнением'))
fig.add_trace(go.Scatter(x=df.index, y=df['safety_stocks'], name='Страховой запас'))
fig.add_trace(go.Scatter(x=df.index, y=df['reorder_level'], name='Точка заказа'))
fig.update_layout(width=800)
st.plotly_chart(fig, use_container_width=False, sharing="streamlit")


st.table(data=df)

