import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_lottie import st_lottie
import requests

st.set_page_config(layout="wide")


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


file_url = "https://assets4.lottiefiles.com/temp/lf20_aKAfIn.json"
lottie_book = load_lottieurl(file_url)
st_lottie(lottie_book, speed=1, height=200, key="initial")

st.title("Goodreads App")

books_df = pd.read_csv("goodreads_history.csv")

booksreads_file = st.file_uploader("Sube tu archivo csv")

if booksreads_file is None:
    books_df = pd.read_csv("goodreads_history.csv")
    st.write("Analizando los datos históricos de Tyler")
else:
    books_df = pd.read_csv(booksreads_file)
    st.write("Analizando tus datos históricos de Goodreads")

    """
    Después de observar los datos y pensar en que información sería util obtener de los datos históricos, 
    he aquí algunas preguntas interesantes:
        1. ¿Cuantos libros lee al año?
        2. ¿Cuanto tiempo se tarda en terminar un libro que ha empezado?
        3. ¿Cuanto duran los libros que se han leído?
        4. ¿Que edad tienen los libros leídos?
        5. ¿Cómo califica los libros en comparación con otros usuarios de Goodreads?
    
    La tarea está en tomar estas preguntas y AVERIGUAR como modificar los datos para visualizarlos.
    """


# Pregunta 1. ¿Cuantos libros lee al año?
# Para este escenario tomaré la columna "Date Read" que viene a ser la fecha cuando terminé de leer el libro
# Extraeré solo el "AÑO" de la columna "Date Read" dandole el formato correcto de fecha.

books_df["Year Finished"] = pd.to_datetime(books_df["Date Read"]).dt.year

books_per_year = books_df.groupby("Year Finished")["Book Id"].count().reset_index()
books_per_year.columns = ["Year Finished", "Count"]

fig_books_per_year = px.bar(
    books_per_year, x="Year Finished", y="Count", title="Libros leídos por año"
)

# st.plotly_chart(fig_books_per_year)


# Pregunta 2. ¿Cuanto tiempo se tarda en terminar un libro que ha empezado?
# Para está pregunta asumiré que el usuario "termina" de leer su libro según la fecha de "Date Read"
# La forma de abordarlo es simple. Podría cambiar el formato a fecha de las columnas originales, o bien solo cambiarlo al momento de la resta (usaré esta opción).

books_df["days_to_finish"] = (
    pd.to_datetime(books_df["Date Read"]) - pd.to_datetime(books_df["Date Added"])
).dt.days

fig_days_to_finish = px.histogram(books_df, x="days_to_finish")
# st.plotly_chart(fig_days_to_finish)

# El gráfico anterior da como resultado una muestra errónea, ya que aparecen días en negativo (-500) y libros que están siendo leídos.
# Esto ocurre porque el dataset no fue limpiado. Se aplicará un filtro para que solo se muestren valores positivo y que hayan sido leidos (Exclusive Shelf == read)
books_finished_filtered = books_df[
    (books_df["Exclusive Shelf"] == "read") & (books_df["days_to_finish"] >= 0)
]

fig_books_finished_filtered = px.histogram(
    books_finished_filtered,
    x="days_to_finish",
    title="Tiempo transcurrido entre Date Added y Date Finished",
)
# st.plotly_chart(fig_books_finished_filtered)


# Pregunta 3. ¿Cuanto duran los libros que se han leído?
# Supongo que la duración del libro está determinada por el "Number of Page". Probemos rápidamente que sale.
fig_book_duration = px.histogram(
    books_df, x="Number of Pages", title="Duración en base al Number of Pages"
)
# st.plotly_chart(fig_book_duration)


# Pregunta 4. ¿Que edad tienen los libros leídos?
# Voy utilizar la columna "Original Publication Year"
# Voy a agruparlos por esa columna y mostrarlos rapidamente en un grafico para ver que patrones.

books_per_publication_date = (
    books_df.groupby("Original Publication Year")["Book Id"].count().reset_index()
)
books_per_publication_date.columns = ["Year Published", "Count"]

fig_publication_date = px.bar(
    books_per_publication_date,
    x="Year Published",
    y="Count",
    title="Año de publicación del libro",
)
fig_publication_date.update_xaxes(range=[1850, 2021])
# st.plotly_chart(fig_publication_date)
st.write(
    "Este gráfico está con zoom en el periodo 1850 a 2021, pero es interactivo por lo cual puedes quitar el zoom y ver el conjunto completo de datos."
)

# Pregunta 5. ¿Cómo califica los libros en comparación con otros usuarios de Goodreads?
# Para esto utilizaré las columnas "My Rating" y "Average Rating" (rating de otros usuarios)
# 1. Filtraré los libros leidos según la valoración (valoraciones distintas a cero, es decir, leídos y valorados)
# 2. Crear un histograma de la valoracion media (Average Rating) por libro para el primer gráfico
# 3. Crear un histograma para las valoraciones propias (My Rating)

books_rated = books_df[books_df["My Rating"] != 0]

fig_books_rated = px.histogram(books_rated, x="My Rating")
# st.plotly_chart(fig_books_rated)

fig_average_book_rating = px.histogram(books_rated, x="Average Rating")
# st.plotly_chart(fig_average_book_rating)

# Vamos a calcular si el rating mio es mayor o menor que la media de los usuarios
import numpy as np

avg_difference = (
    np.mean(books_rated["My Rating"]) - np.mean(books_rated["Average Rating"])
).round(2)
if avg_difference < 0:
    sign = "bajo"
else:
    sign = "alto"


st.write(
    f"Tu rating a los libros es {sign} en comparación con la media del publico por {abs(avg_difference)} puntos"
)


### Mejora Iterativa
#   1. Embellecimiento de la app mediante una animación
#   2. Organización mediante columnas y anchura
#   3. COnstrucción narrativa mediante texto y estadísticas adicionales


books_finished = books_df[books_df["Exclusive Shelf"] == "read"]
u_books = len(books_finished["Book Id"].unique())
u_authors = len(books_finished["Author"].unique())
mode_author = books_finished["Author"].mode()[0]
st.write(
    f"Parece que has terminado {u_books} libros con un total de {u_authors} autores únicos. Tu autor más leído es {mode_author}!"
)
st.write(
    f"Los resultados de la app se pueden encontrar más abajo, se ha analizado todo desde como se distribuyen tus lecturas hasta cómo puntúas los libros. Dale una mirada, y recuerda que todos los gráficos son interactivos!"
)


# Añadiendo columnas

row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)
row3_col1, row3_col2 = st.columns(2)

with row1_col1:
    mode_year_finished = int(books_df["Year Finished"].mode()[0])
    st.plotly_chart(fig_books_per_year)
    st.write(
        f"Terminas la mayoría de tus libros el año {mode_year_finished}. Buen trabajo!"
    )
with row1_col2:
    st.plotly_chart(fig_books_finished_filtered)
    mean_days_to_finish = int(books_finished_filtered["days_to_finish"].mean())
    st.write(
        f"Te tomó un promedio de {mean_days_to_finish} días desde que agregaste el libro a tu cuenta hasta que lo terminaste. Esta no es una métrica perfecta, ya que pudiste agregar el libro a la lista de futuras lecturas!"
    )
with row2_col1:
    st.plotly_chart(fig_book_duration)
    avg_pages = int(books_df["Number of Pages"].mean())
    st.write(
        f"Tus libros tienen en promedio {avg_pages} paginas, Revisa su distribución arriba!"
    )
with row2_col2:
    st.plotly_chart(fig_publication_date)
with row3_col1:
    st.plotly_chart(fig_books_rated)
with row3_col2:
    st.plotly_chart(fig_average_book_rating)
