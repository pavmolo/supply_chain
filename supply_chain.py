import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import random

st.subheader('Разработчик: Павел Молотивский')

with st.sidebar:
  st.title('Введите данные для моделирования элемента цепочки поставок (конкретного SKU)')
  st.subheader("Параметры для расчета уровня запаса")
  current_stock = st.number_input("Укажите фактический остаток в месте хранения в штуках", value=20)

  order_in_process = st.number_input("Установите ранее сделанные, но не выполенные заказы на поставку в место хранения", value=200)

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
#st.subheader(f"Уровень запаса: {stock_level} штук")
st.metric("Уровень запаса", f"{stock_level} штук")
st.info('Уровень запаса - это фактический запас в точке хранения плюс уже заказанный, но еще не поставленный товар')


average_day_sales = sales_3m / days_3m
average_day_sales_rounded = np.around(average_day_sales, decimals=2, out=None)

#st.subheader(f"Среднедневные продажи за последние три месяца: {average_day_sales} руб. в день")
st.metric("Среднедневные продажи за последние три месяца", f"{average_day_sales_rounded} шт в день")

safety_stock_days = lead_time_for_replenishment * ((1 + demand_variation / 100) * (1 + leadtime_variation / 100) - 1) * safety_multiplicator
safety_stock_pieces = safety_stock_days * average_day_sales
optimum_inventory_level_days = lead_time_for_replenishment + safety_stock_days
reorder_level = optimum_inventory_level_days * average_day_sales



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
  st.error(f'Заказывать не нужно. До заказа нужно израсходовать {np.around(-neded_order, decimals=0, out=None)} шт')
else:
  st.metric("Необходимый заказ:", f"{np.around(neded_order, decimals=2, out=None)} шт")



#st.area_chart(x=range(30), y=demand_random_generator, width=0, height=0, use_container_width=True)


df = pd.DataFrame(demand_random_generator, columns=['demand'], index=range(30))
df['lead_time'] = leadtime_random_generator
df['consumption'] = df['lead_time'] * df['demand']
df['after'] = df.index * 100 + 1
df['before'] = df.index * 100 + 99
df['orders'] = 0
df['order_in_process'] = 0
df['fact_stock_after'] = 0
df['fact_stock_before'] = 0
df['reorder_level'] = np.around(reorder_level, decimals=0, out=None)
df['safety_stock'] =  np.around(safety_stock_pieces, decimals=0, out=None)
df['order_in_process'][0] = order_in_process
df['orders'][0] = reorder_level - current_stock
df['fact_stock_after'][0] = current_stock + df['order_in_process'][0]
df['fact_stock_before'][0] = df['fact_stock_after'][0] - df['consumption'][0]
df = df[['demand', 'lead_time', 'after', 'before','safety_stock', 'reorder_level', 'orders', 'order_in_process', 
       'fact_stock_after', 'consumption', 'fact_stock_before']]

with st.expander("Сгенерированы случайные величины спроса и сроков поставки на основании показателей вариабельности, введенных вами. Нажмите сюда, чтобы посмотреть их"):
  
  st.subheader('Сгенерированный случайный спрос на основании введенных данных')
  fig_2 = go.Figure()
  fig_2.add_trace(go.Scatter(x=df.index , y=df['demand'], name='Случайная величина спроса'))
  fig_2.add_trace(go.Scatter(x=df.index, y=[df['demand'].mean()] * df['demand'].count(), name='Средняя величина спроса'))
  fig_2.update_yaxes(range=[0, df['demand'].max() * 1.05])
  st.plotly_chart(fig_2, use_container_width=True, sharing="streamlit")
  
  st.subheader('Сгенерированный случайный срок от заказа до поставки на основании введенных данных')
  fig_3 = go.Figure()
  fig_3.add_trace(go.Scatter(x=df.index , y=df['lead_time'], name='Случайная величина спроса'))
  fig_3.add_trace(go.Scatter(x=df.index, y=[df['lead_time'].mean()] * df['lead_time'].count(), name='Средняя величина спроса'))
  fig_3.update_yaxes(range=[0, df['lead_time'].max() * 1.05])
  st.plotly_chart(fig_3, use_container_width=True, sharing="streamlit")

for i in range(1, 30):
  df['order_in_process'][i] = df['orders'][i-1]
  df['fact_stock_after'][i] = df['fact_stock_before'][i-1] + df['order_in_process'][i]
  df['fact_stock_before'][i] = df['fact_stock_after'][i] - df['consumption'][i]
  if df['fact_stock_before'][i] < 0:
    df['fact_stock_before'][i] = 0
  df['orders'][i] = reorder_level - df['fact_stock_before'][i-1]
  if df['orders'][i] < 0:
    df['orders'][i] = 0

before = df[['before', 'fact_stock_before']]
before.columns = ['step', 'fact_stock']
after = df[['after', 'fact_stock_after']]
after.columns = ['step', 'fact_stock']
fact_stock = pd.concat([after, before])
fact_stock = fact_stock.sort_values('step', axis=0, ascending=True)
fact_stock['Точка заказа'] = reorder_level
fact_stock['Страховой запас'] = safety_stock_pieces

st.subheader("Моделирование 30 дней")
st.info(f"Страхового запаса не хватило (возник дефицит) в {(df['fact_stock_before'] == 0).sum()} случаях из {len(df)}")
fig_4 = go.Figure()
fig_4.add_trace(go.Scatter(x=fact_stock['step'], y=fact_stock['fact_stock'], fill='tozeroy', name='Объема запаса в точке хранения'))
fig_4.add_trace(go.Scatter(x=fact_stock['step'], y=fact_stock['Страховой запас'], name='Страховой запас'))
fig_4.add_trace(go.Scatter(x=fact_stock['step'], y=fact_stock['Точка заказа'], name='Точка заказа'))
fig_4.update_layout(width=1000)
st.plotly_chart(fig_4, use_container_width=False, sharing="streamlit")
with st.expander("Справка по интерпретации графика 'Пилы'"):
  st.markdown('''<img src="https://i.ibb.co/HGwb7jb/order-level-illustration.png">''', unsafe_allow_html=True)

mean_stock = fact_stock['fact_stock'].mean()
st.metric("Средний уровень запаса при моделировании", f"{np.around(mean_stock, decimals=2, out=None)} штук")
st.metric("Рассчетный уровень запаса", f"{np.around(safety_stock_pieces + ((reorder_level - safety_stock_pieces) / 2), decimals=2, out=None)} штук")
