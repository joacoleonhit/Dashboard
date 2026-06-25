from flask import Flask, render_template, request
import requests
import pandas as pd

app = Flask(__name__)

def obtener_datos(pais, indicador):
    url = f"https://api.worldbank.org/v2/country/{pais}/indicator/{indicador}?format=json"

    respuesta = requests.get(url)
    datos = respuesta.json()

    registros = datos[1]
    df = pd.DataFrame(registros)
    df = df[['date', 'value']]
    df = df.dropna()
    df = df.rename(columns={'date': 'anio', 'value': 'valor'})
    df['anio'] = df['anio'].astype(int)
    df = df.sort_values('anio')

    return df

df_poblacion = obtener_datos("ARG", "SP.POP.TOTL")

def calcular_kpis(pais):
    df_poblacion = obtener_datos(pais, "SP.POP.TOTL")
    df_pib = obtener_datos(pais, "NY.GDP.MKTP.CD")
    df_vida = obtener_datos(pais, "SP.DYN.LE00.IN")

    poblacion_actual = df_poblacion['valor'].iloc[-1]
    pib_actual = df_pib['valor'].iloc[-1]
    esperanza_vida_actual = df_vida['valor'].iloc[-1]

    crecimiento = (
        (df_poblacion.iloc[-1]["valor"] -
         df_poblacion.iloc[-2]["valor"])
         / df_poblacion.iloc[-2]["valor"]
    ) * 100

    return {
        pais: pais,
        "poblacion_actual": poblacion_actual,
        "pib_actual": pib_actual,
        "esperanza_vida_actual": esperanza_vida_actual,
        "crecimiento": crecimiento
    }


@app.route("/")
def index():
    pais = request.args.get("pais", "ARG")

    indicador = request.args.get("indicador", "SP.POP.TOTL")


    paises = {
        "ARG": "Argentina",
        "BRA": "Brasil",
        "CHL": "Chile",
        "URY": "Uruguay",
        "USA": "Estados Unidos",
        "ESP": "España"
    }


    indicadores = {
        "SP.POP.TOTL": "Población total",
        "NY.GDP.MKTP.CD": "Producto Interno Bruto (PIB)",
        "SP.DYN.LE00.IN": "Esperanza de vida al nacer"
    }


    df_poblacion = obtener_datos(pais, indicador)

    df_grafico = obtener_datos(pais, indicador)

    kpis = calcular_kpis(pais)

    datos = df_poblacion.tail(10).values.tolist()

    anios = df_grafico["anio"].tolist()
    poblaciones = df_grafico["valor"].tolist()

    comparar = request.args.get("comparar")
    pais_comparacion = request.args.get("pais_comparacion", "BRA")

    kpis_comparacion = None
    poblaciones_comparacion = None
    

    if comparar == "1":
            kpis_comparacion = calcular_kpis(pais_comparacion)

            df_comparacion = obtener_datos(pais_comparacion, indicador)

            poblaciones_comparacion = df_comparacion["valor"].tolist()


    return render_template(
        "index.html",
        datos=datos,
        pais=pais,
        paises=paises,
        indicador=indicador,
        indicadores=indicadores,
        kpis=kpis,
        anios=anios,
        poblaciones=poblaciones,
        comparar=comparar,
        pais_comparacion=pais_comparacion,
        kpis_comparacion=kpis_comparacion,
        poblaciones_comparacion=poblaciones_comparacion
    )

if __name__ == "__main__":
    app.run(debug=True)