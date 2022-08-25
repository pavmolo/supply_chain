import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.subheader("Заполните поля ниже:")
current_stock = st.number_input(f"Установите текущий уровень запаса в штуках", value=0)
