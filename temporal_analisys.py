import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# ==========================================
# SETUP STILE MATPLOTLIB (TUFTE PRINCIPLES)
# ==========================================
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'axes.grid': True,
    'grid.alpha': 0.2,
    'grid.linestyle': '--',
    'axes.spines.top': False,
    'axes.spines.right': False, 
    'axes.edgecolor': '#cccccc',
    'text.color': '#333333',
    'axes.labelcolor': '#333333',
    'xtick.color': '#333333',
    'ytick.color': '#333333'
})

# ==========================================
# CARICAMENTO DATI PULITI
# ==========================================
try:
    # parse_dates è fondamentale per mantenere la coerenza dell'asse temporale X
    df = pd.read_csv('cleaned_drone_data.csv', parse_dates=['date'])
except FileNotFoundError:
    print("ERRORE: Esegui prima preprocessing.py per generare 'cleaned_drone_data.csv'")
    exit()

# ==========================================
# AGGREGAZIONE TEMPORALE
# ==========================================
# Raggruppiamo i dati per mese (Month End 'ME') per registrare gli zeri nei mesi senza attacchi.
df_monthly = df.resample('ME', on='date')[['total_deaths', 'civilian_deaths']].sum().reset_index()

# Media mobile a 3 mesi (rolling window).
# PERCHÉ (Gestalt - Legge della Buona Continuazione): Attenuando il rumore ad alta frequenza, 
# la linea guida l'occhio a percepire il trend di fondo come una figura continua.
df_monthly['total_ma'] = df_monthly['total_deaths'].rolling(window=3, min_periods=1).mean()
df_monthly['civ_ma'] = df_monthly['civilian_deaths'].rolling(window=3, min_periods=1).mean()

# ==========================================
# VISUALIZZAZIONE TEMPORALE (TUFTE & WARE)
# ==========================================
fig, ax = plt.subplots(figsize=(12, 6))

# Contesto (Principio di Figura/Sfondo):
# Vittime totali tracciate sottili e desaturate per retrocedere sullo sfondo.
ax.plot(df_monthly['date'], df_monthly['total_ma'], 
        color='#7f7f7f', linewidth=1.2, zorder=1)

# Focus (Attenzione Pre-Attentiva - Colin Ware):
# Colore rosso mattone saturo e marcatori distanziati per guidare la percezione.
ax.plot(df_monthly['date'], df_monthly['civ_ma'], 
        color='#b2182b', linewidth=2.5, marker='o', markevery=6, markersize=5, zorder=2)

# ==========================================
# ETICHETTATURA E DATA-INK RATIO
# ==========================================
# Etichettatura Diretta (Gestalt - Legge della Prossimità):
# Posizionamento inline invece di una legenda esterna per ridurre il carico cognitivo.
last_date = df_monthly['date'].iloc[-1]
last_total = df_monthly['total_ma'].iloc[-1]
last_civ = df_monthly['civ_ma'].iloc[-1]

ax.text(last_date, last_total, ' Vittime Totali', color='#7f7f7f', fontsize=11, va='center')
ax.text(last_date, last_civ, ' Vittime Civili', color='#b2182b', fontsize=11, fontweight='bold', va='center')

# Annotazione del picco critico
peak_idx = df_monthly['civ_ma'].idxmax()
peak_date = df_monthly.loc[peak_idx, 'date']
peak_val = df_monthly.loc[peak_idx, 'civ_ma']

ax.annotate(f"Picco Civili ({peak_val:.0f})", 
            xy=(peak_date, peak_val), 
            xytext=(0, 15), textcoords='offset points',
            ha='center', color='#b2182b', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#b2182b', lw=1.5))

# Lie Factor = 1 (Graphical Integrity):
# L'asse Y DEVE partire da 0 per evitare distorsioni delle variazioni relative.
ax.set_ylim(bottom=0)

# Formattazione minimale asse X
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.set_ylabel("Media mobile mensile (vittime)", fontsize=11)

sns.despine(ax=ax, top=True, right=True, left=False, bottom=False)

plt.tight_layout()
plt.show()