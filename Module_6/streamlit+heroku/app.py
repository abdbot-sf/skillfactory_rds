#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import lightfm as lf
import nmslib
import pickle
import scipy.sparse as sparse


# Пропишем вспомогательные функции: 

# In[2]:


def nearest_books_nms(itemid, index, n=10):
    """Функция для поиска ближайших соседей, возвращает построенный индекс"""
    nn = index.knnQuery(item_embeddings[itemid], k=n)
    return nn


# Первая функция использует наш построенный index для поиска книг. Думайте об этой функции как о реализации K-NN (k-ближайших соседей). 
# 
# Функция get_names просто возвращает список книг,  а точнее их названия, в виде [(Название книги, Имя Автора),...]:

# In[3]:


def get_names(index):
    """
    input - idx of books
    Функция для возвращения имени книг
    return - list of names
    """
    names = []
    for idx in index:
        names.append(items[items['itemid'] == idx]['title'].values[0])
    return names


# Чтение файлов никогда не было таким увлекательным!

# In[4]:


def read_files(folder_name='data'):
    """
    Читаем файл с данными
    """
    items = pd.read_csv('products.csv')
    items['itemid'] = items['itemid'].astype(str)
    items['title'] = items['title'].str.extract(r'(\S+\s\S+\s\S+)')
    items.dropna(subset=['title'], inplace=True)
    return items


# In[5]:


def product_description(option):
    """
    Функция для создания составляющих описания товара
    """
    choice = products[products['itemid'] == option]
    price = choice['price'].iloc[0]
    title = choice['title'].iloc[0]
    desc = choice['description'].iloc[0]

    return choice, price, title, desc


# Давайте загрузим векторные представления книг, которые мы сохранили в предыдущем модуле.

# In[6]:


def load_embeddings():
    """
    Функция для загрузки векторных представлений
    """
    with open('item_embeddings_lfm_comp.pickle', 'rb') as f:
        item_embeddings = pickle.load(f)

    # Тут мы используем nmslib, чтобы создать наш быстрый knn
    nms_idx = nmslib.init(method='hnsw', space='cosinesimil')
    nms_idx.addDataPointBatch(item_embeddings)
    nms_idx.createIndex(print_progress=True)
    return item_embeddings,nms_idx


# А теперь выполним весь код, который мы написали.

# In[7]:


st.title('Попробуем вам что-нибудь порекомендовать')

# Загружаем данные
products = read_files()
item_embeddings, nms_idx = load_embeddings()

# вводим title
product = st.text_input('Наберите интересующий продукт на английском языке:', '')
product = product.lower()
# находим подходящий товар
try:
    output = products[products['title'].str.lower().str.contains(product)]
    # выбираем товар из списка
    option = st.selectbox('Выберите интересующий вас продукт из списка:', output['title'].values)
    options = output[output['title'].values == option].itemid.iloc[0]
    st.header(f'Информация о продукте:')

     
    choice, price, title, desc = product_description(options)
    st.markdown(f'**{цена}**')
    st.markdown(f'*{наименование}*')
    st.markdown(desc)

    # выводим рекомендации к товару
    st.header('Также рекомендуем: ')

    # Ищем рекомендации
    output = products[products['title'] == option]
    val_index = output[output['title'].values == option]['itemid'].iloc[0]
    index = nearest_items_nms(val_index, nms_idx, 5)

    # Выводим инфо о рекомендуемых товарах:
    for idx in index[0][1:]:
        try:
            choice, price, title, desc = product_description(str(idx))
            st.markdown(f'*{наименование}*')
            st.markdown(f'**{цена}**')
            st.markdown('-----')
        except:
            st.text('')
except:
    st.header(f'Указанный вами продукт не найден')


# In[ ]:




