# Importamos las librerías necesarias. 
from fastapi import FastAPI
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI(
    title="Proyecto Individual N° 1 ",
    description= "Machine Learning Operations (MLOps)"

)

# Importamos el dataset que contiene los datos para ser consumidos en las consultas de la API.
df = pd.read_csv("Datasets/dataset_ETL.csv")
df["release_date"] = pd.to_datetime(df["release_date"], format="%Y-%m-%d")
df["month_release"] = df["release_date"].dt.strftime("%B")
df["day_of_week_release"] = df["release_date"].dt.strftime("%A")

@app.get("/")
def index():
    return {"mensage":"Bienvenido!"}


@app.get("/peliculas_mes/{mes}")
def peliculas_mes(mes: str):
    '''
    Esta función recibe como argumento el mes en español y la función retorna la cantidad de películas que se estrenaron ese mes
    (nombre del mes en español, en str, ejemplo "marzo") históricamente.

    '''
    meses = {
        "enero": "January",
        "febrero": "February",
        "marzo": "March",
        "abril": "April",
        "mayo": "May",
        "junio": "June",
        "julio": "July",
        "agosto": "August",
        "septiembre": "September",
        "octubre": "October",
        "noviembre": "November",
        "diciembre": "December"
    }
    mes_ingles = meses.get(mes.lower())
    df_mes = df[df["month_release"] == mes_ingles]
    cantidad = len(df_mes)
    return {"mes": mes, "cantidad": cantidad}


@app.get('/peliculas_dia/{dia}')
def peliculas_dia(dia: str):
    '''
    Esta función recibe como argumento el día de la semana y la función retorna la cantidad de películas que se estrenaron
    ese día (nombre del día en español, en str, ejemplo "lunes") históricamente.

    '''
    dias_semana = {
        "lunes": "Monday",
        "martes": "Tuesday",
        "miercoles": "Wednesday",
        "jueves": "Thursday",
        "viernes": "Friday",
        "sabado": "Saturday",
        "domingo": "Sunday"
    }
    dia_ing = dias_semana[dia.lower()]
    
    df_dia = df[df["day_of_week_release"] == dia_ing]
    cantidad = len(df_dia)
    return {"dia": dia, "cantidad": cantidad}



@app.get('/franquicia/{franquicia}')
def franquicia(franquicia: str):
    '''
    Esta función recibe como argumento la franquicia y retorna la cantidad de películas, la ganancia total
    y la ganancia promedio para dicha franquicia.

    '''
    df["belongs_to_collection"] = df["belongs_to_collection"].fillna("")
    df_franquicia = df[df["belongs_to_collection"].str.contains(franquicia, na=False)]
    cantidad = df_franquicia.shape[0]
    ganancia_total = df_franquicia["revenue"].sum()
    ganancia_promedio = df_franquicia["revenue"].mean()
    return {"franquicia": franquicia, "cantidad": cantidad, "ganancia_total": round(ganancia_total, 2), "ganancia_promedio": round(ganancia_promedio, 2)}


@app.get('/peliculas_pais/{pais}')
def peliculas_pais(pais: str):
    '''
    Esta función recibe como argumento el nombre del país y retorna la cantidad de películas producidas en el mismo.

    '''
    cantidad = len(df[df["production_countries"] == pais])
    return {"pais": pais, "cantidad": cantidad}



@app.get('/productoras/{productora}')
def productoras(productora: str):
    '''
    Esta función recibe como argumento el nombre de la productora y retorna la ganancia total y la cantidad de películas que produjeron.

    '''
    df_productora = df[df["production_companies"] == productora]
    ganancia_total = df_productora["revenue"].sum()
    cantidad = len(df_productora)
    return {"productora": productora, "ganancia_total": ganancia_total, "cantidad": cantidad}


@app.get('/retorno/{pelicula}')
def retorno(pelicula: str):
    '''
    Esta función recibe como argumento el nombre de la película y retorna la inversión, la ganancia, el retorno y el año en el que se lanzó.

    '''
    pelicula_df = df.loc[df["title"] == pelicula]
    inversion = pelicula_df["budget"].values[0]
    ganancia = pelicula_df["revenue"].values[0]
    retorno = pelicula_df["retorno"].values[0]
    anio = int(pelicula_df["release_date"].dt.year.values[0])
    return {"pelicula": pelicula, "inversion": inversion, "ganacia": ganancia, "retorno": retorno, "anio": anio}



# Importamos el dataset que contiene los datos que serán consumidos en las consultas de la API.
df_m = pd.read_csv("Datasets/data_modelo.csv", sep=",")
df_m = df_m.sample(n=4000, random_state=42)
punt_matrix = df_m.pivot_table(index="title", values="vote_average")
simil_matrix = cosine_similarity(punt_matrix.fillna(0))

@app.get("/recomendacion/{titulo}")
def recomendacion(titulo: str):
 
    movie_index = punt_matrix.index.get_loc(titulo)

    movie_scores = list(enumerate(simil_matrix[movie_index]))

    movie_scores = sorted(movie_scores, key=lambda x: x[1], reverse=True)

    top_movies = [punt_matrix.index[i] for i, score in movie_scores[1:6]]

    return top_movies
