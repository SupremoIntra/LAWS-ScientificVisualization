import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# SETUP STILE MATPLOTLIB (TUFTE PRINCIPLES)
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')

# La griglia in background (alpha=0.2) funge da "Sfondo" (Gestalt), 
# permettendo ai dati ("Figura") di emergere senza distrazioni ottiche.
plt.rcParams.update({
    'axes.grid': True,
    'grid.alpha': 0.2,
    'grid.linestyle': '--',
    'axes.spines.top': False,   # Rimozione chart junk: i bordi non aggiungono informazioni
    'axes.spines.right': False, 
    'axes.edgecolor': '#cccccc',
    'text.color': '#333333',
    'axes.labelcolor': '#333333',
    'xtick.color': '#333333',
    'ytick.color': '#333333'
})

# ==========================================
# CARICAMENTO DATI E PARSING ROBUSTO
# ==========================================
file_path = 'DroneWarsData.csv'

col_names = [
    'strike_id', 'country', 'date_str', 'president', 'location', 'coords_raw', 
    'latitude', 'longitude', 'total_deaths_min', 'total_deaths_max', 
    'civilian_deaths_min', 'civilian_deaths_max', 'children_deaths', 'injured_min', 'injured_max'
]

# Leggiamo il file considerando il separatore ';' e ignorando colonne finali fantasma
df = pd.read_csv(file_path, sep=';', header=None, names=col_names, usecols=range(15), dtype=str)

# ==========================================
# CONTROLLI DI QUALITÀ E PREPROCESSING
# ==========================================
initial_rows = len(df)

df['country'] = df['country'].str.strip()

# b) Conversione numerica robusta (Risoluzione Errore)
numeric_cols = ['latitude', 'longitude', 'total_deaths_min', 'total_deaths_max', 'civilian_deaths_min', 'civilian_deaths_max']
for col in numeric_cols:
    # 1. Uniformiamo i separatori decimali
    df[col] = df[col].astype(str).str.replace(',', '.')
    # 2. Convertiamo in float. Se incontra testo (es. 'Latitude'), restituisce NaN
    df[col] = pd.to_numeric(df[col], errors='coerce')

# c) Gestione Incertezza e Stima
df['total_deaths'] = df['total_deaths_max']
df['civilian_deaths'] = df['civilian_deaths_max']

# d) Rimozione duplicati e nulli critici
df = df.drop_duplicates(subset=['strike_id'])
duplicates_removed = initial_rows - len(df)

# I NaN generati dal `to_numeric` sulle righe di testo intruso vengono rimossi qui
df = df.dropna(subset=['date_str', 'latitude', 'longitude', 'total_deaths'])
nulls_removed = (initial_rows - duplicates_removed) - len(df)

df['civilians_uncertain'] = df['civilian_deaths'].isna()
df['civilian_deaths'] = df['civilian_deaths'].fillna(0)

# e) Parsing temporale (Connessione Gestaltica)
df['date'] = pd.to_datetime(df['date_str'], format='%d-%m-%Y', errors='coerce')
df = df.dropna(subset=['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# f) Coerenza logica
df['civilians_forced'] = df['civilian_deaths'] > df['total_deaths']
df.loc[df['civilians_forced'], 'civilian_deaths'] = df.loc[df['civilians_forced'], 'total_deaths']

# ==========================================
# REPORT TESTUALE
# ==========================================
print(f"--- REPORT PREPROCESSING DRONE WARS ---")
print(f"Righe iniziali: {initial_rows}")
print(f"Righe valide post-pulizia: {len(df)}")
print(f"Duplicati rimossi: {duplicates_removed}")
print(f"Righe anomale/nulle rimosse: {nulls_removed}")
print(f"\nPeriodo di osservazione: {df['date'].min().strftime('%d-%m-%Y')} a {df['date'].max().strftime('%d-%m-%Y')}")
print(f"\nMetriche (Stima Massima Documentata):")
print(f"- Vittime Totali -> Max: {df['total_deaths'].max():.0f}, Media: {df['total_deaths'].mean():.1f}")
print(f"- Vittime Civili -> Max: {df['civilian_deaths'].max():.0f}, Media: {df['civilian_deaths'].mean():.1f}")
print(f"\nTop 3 Nazioni colpite:\n{df['country'].value_counts().head(3).to_string()}")
print(f"---------------------------------------")