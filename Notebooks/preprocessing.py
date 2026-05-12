import pandas as pd
import numpy as np


df = pd.read_csv('../data/tbij_drones_data.csv')

# --- 1. GESTIONE DUPLICATI E VALORI MANCANTI ---

# Eventuali doppi conteggi altererebbero l'accuratezza quantitativa e aumenterebbero il Lie Factor, falsando in modo ingannevole le proporzioni reali degli attacchi e delle vittime.
initial_rows = df.shape
df = df.drop_duplicates()
print(f"Pulizia duplicati: rimosse {initial_rows - df.shape} righe per scongiurare bias statistici sulle distribuzioni.")

# L'assenza di valori nei campi fondamentali rende impossibile tracciare grafici longitudinali continui; mantenere record incompleti genererebbe fastidiosi buchi visivi o errori fatali nel calcolo delle medie mobili.
missing_cols = ['date', 'lat', 'lon', 'civilian_casualties', 'total_strikes']
missing_count = df[missing_cols].isnull().sum().sum()
df = df.dropna(subset=missing_cols)
print(f"Pulizia valori mancanti: eliminate {missing_count} celle per garantire la solidità strutturale del data storytelling e la pulizia dei plot.")


# --- 2. GESTIONE E ORDINAMENTO DELLE DATE ---

# Per sfruttare appieno i principi della Gestalt, in particolare quello della connessione nei line plots temporali, è imperativo che l'asse del tempo sia una variabile "datetime" trattata in modo lineare e rigorosamente sequenziale.
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# Date malformate che non possono essere convertite spezzerebbero il continuum della serie storica, introducendo rumore (noise) non interpretabile dall'osservatore.
invalid_dates = df['date'].isnull().sum()
if invalid_dates > 0:
    print(f"Rimossi {invalid_dates} record con date non formattabili per mantenere inalterata la coerenza dell'evoluzione temporale.")
    df = df.dropna(subset=['date'])

# L'ordinamento è la condizione sine qua non affinché le linee nel grafico riflettano lo scorrere reale del tempo da sinistra verso destra.
df = df.sort_values(by='date')


# --- 3. CONTROLLO VALIDITÀ COORDINATE GEOGRAFICHE ---

# Affinché i marker spaziali su librerie come Folium o Geopandas mantengano la corretta posizione sul piano 2D (considerato l'attributo pre-attentivo più potente), i dati geospaziali devono rientrare rigorosamente entro i limiti fisici terrestri standard.
outliers_geo = df[~((df['lat'] >= -90) & (df['lat'] <= 90) & (df['lon'] >= -180) & (df['lon'] <= 180))]

if not outliers_geo.empty:
    print(f"Attenzione: esclusi {outliers_geo.shape} record con coordinate geografiche fuori scala. L'inclusione di questi outlier corromperebbe irreparabilmente le mappe spaziali interattive.")
    df = df.drop(outliers_geo.index)


# --- 4. CREAZIONE COLONNA YEAR_MONTH ---

# Una granularità esclusivamente giornaliera renderebbe la varianza troppo alta, generando il cosiddetto 'visual clutter' (spaghetti chart) e abbassando drasticamente il Data/Ink Ratio teorizzato da Tufte. Raggruppare per mese smussa il rumore ma mantiene intatti i trend rilevanti, ideali per la percezione della storia.
df['year_month'] = df['date'].dt.to_period('M')


# --- 5. REPORT DESCRITTIVO TESTUALE FINALE ---

# Un riepilogo testuale a valle del preprocessing serve allo sviluppatore per certificare mentalmente che il campione abbia sufficiente massa critica e integrità prima di procedere con il rendering visivo e la convalida della tesi sulle LAWS e il Diritto Umanitario.
print("\n" + "="*50)
print("📸 FOTOGRAFIA DEL DATASET PULITO E PRONTO PER LA VISUALIZZAZIONE")
print("="*50)
print(f"Dimensioni del dataset validato (Righe, Colonne): {df.shape}")
print(f"Teatri di conflitto (Paesi) isolabili negli Small Multiples: {df['country'].nunique()}")

print("\nStatistiche descrittive delle metriche chiave di targeting:")
# L'arrotondamento a due decimali riduce il carico cognitivo dell'osservatore, evitando che un'eccessiva precisione numerica (inutile in questa fase) rallenti la working memory.
print(df[['total_strikes', 'civilian_casualties']].describe().round(2))
print("="*50)