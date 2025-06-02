import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# === CONFIGURACIÓN ===
archivo_csv = 'data_2025-04-30_11-53-13.csv'  # Cambia esto por el nombre de tu archivo
salida_csv = 'analisis_tostado.csv'

# === CARGA DE DATOS ===
df = pd.read_csv(archivo_csv, skiprows=1, dayfirst=True)

# Crear columna de Timestamp combinando Fecha y Hora
df['Timestamp'] = pd.to_datetime(
    df['Fecha'].astype(str) + ' ' + df['Hora'].astype(str),
    dayfirst=True,
    errors='coerce'
)

# Eliminar filas sin fecha válida y fijar índice
df = df.dropna(subset=['Timestamp'])
df = df.set_index('Timestamp').sort_index()

# Filtrar la etapa de "Tostado"
rost = df[df['Etapa'].str.contains('Tostado', case=False)].copy()

# === MÉTRICAS BÁSICAS ===
stats = rost[['Temperatura_1','Temperatura_2','RoR']].agg(['min','mean','max','std']).T

# Pico máximo de RoR
t_peak = rost['RoR'].idxmax()
max_ror = rost.loc[t_peak, 'RoR']

# Cruces simultáneos >150°C
cross150 = rost[(rost['Temperatura_1'] > 150) & (rost['Temperatura_2'] > 150)].index

# Duración total de la etapa
dur_total = rost.index[-1] - rost.index[0]

# Correlación entre sondas
corr = rost['Temperatura_1'].corr(rost['Temperatura_2'])

# Tiempos a temperaturas clave
def time_to_temp(col, T):
    sel = rost[rost[col] >= T]
    return sel.index[0] if not sel.empty else pd.NaT

t_150 = time_to_temp('Temperatura_1', 150)
t_170 = time_to_temp('Temperatura_1', 170)
t_180 = time_to_temp('Temperatura_1', 180)
t_200 = time_to_temp('Temperatura_1', 200)

# Fases
fase_secado = t_150 - rost.index[0] if pd.notna(t_150) else pd.NaT
fase_maillard = (t_170 - t_150) if pd.notna(t_150) and pd.notna(t_170) else pd.NaT

# Development Time y %
dev_time = rost.index[-1] - t_peak
dev_pct = dev_time / dur_total * 100

# RoR suavizado
rost['RoR_roll'] = rost['RoR'].rolling(window=6, center=True).mean()

# Detección de cracks
crack_thresh = 12
mask = rost['RoR_roll'] > crack_thresh
groups = (mask != mask.shift()).cumsum()
cracks = rost['RoR_roll'][mask].groupby(groups).apply(lambda x: x.index[0])
first_crack = cracks.iloc[0] if len(cracks) > 0 else pd.NaT
second_crack = cracks.iloc[1] if len(cracks) > 1 else pd.NaT

# Área bajo RoR
area_ror = np.trapezoid(rost['RoR'], x=rost.index.astype(np.int64) / 1e9)

# Máxima diferencia entre sondas
rost['DeltaT'] = (rost['Temperatura_1'] - rost['Temperatura_2']).abs()
t_max_delta = rost['DeltaT'].idxmax()
max_delta = rost['DeltaT'].max()
uniform_pct = (rost['DeltaT'] < 2).mean() * 100

# Pendientes medias
dt_seconds = rost.index.to_series().diff().dt.total_seconds().median()
rost['dT1'] = rost['Temperatura_1'].diff() / dt_seconds * 60
rost['dT2'] = rost['Temperatura_2'].diff() / dt_seconds * 60
mean_slope1 = rost['dT1'].mean()
mean_slope2 = rost['dT2'].mean()

# Cross-correlation lag
t1 = rost['Temperatura_1'] - rost['Temperatura_1'].mean()
t2 = rost['Temperatura_2'] - rost['Temperatura_2'].mean()
corrs = np.correlate(t1, t2, mode='full')
lag_samples = corrs.argmax() - (len(rost) - 1)
lag_seconds = lag_samples * dt_seconds

# === RESUMEN FINAL ===
resumen = {
    'Duración total (s)':       [dur_total.total_seconds()],
    'Pico RoR (°C/min)':        [max_ror],
    'Tiempo pico RoR':          [t_peak],
    'Correlación T1 vs T2':     [corr],
    'Área bajo RoR':            [area_ror],
    'Uniformidad ΔT<2°C (%)':   [uniform_pct],
    'Max ΔT (°C)':              [max_delta],
    'Tiempo ΔT máximo':         [t_max_delta],
    'Slope media T1':           [mean_slope1],
    'Slope media T2':           [mean_slope2],
    't a 150°C':                [t_150],
    't a 170°C':                [t_170],
    't a 180°C':                [t_180],
    't a 200°C':                [t_200],
    'Fase secado (s)':          [fase_secado.total_seconds() if pd.notna(fase_secado) else np.nan],
    'Fase Maillard (s)':        [fase_maillard.total_seconds() if pd.notna(fase_maillard) else np.nan],
    'Dev Time (s)':             [dev_time.total_seconds()],
    'Dev %':                    [dev_pct],
    'First crack':              [first_crack],
    'Second crack':             [second_crack],
    'Lag entre sondas (s)':     [lag_seconds],
    'Cruces >150°C':            [len(cross150)]
}

res_df = pd.DataFrame(resumen).T.rename(columns={0: 'Valor'})

# Redondear valores numéricos a 2 decimales
res_df['Valor'] = res_df['Valor'].apply(
    lambda x: round(x, 2) if isinstance(x, (int, float, np.float64)) else x
)

# Redondear estadísticas básicas
stats_rounded = stats.round(2)

# Unir y guardar en un solo archivo
combined = pd.concat([stats_rounded, res_df], axis=0)
combined = combined.round(2)
combined.to_csv(salida_csv, encoding='utf-8-sig', index=True)

print(f"Análisis completo guardado en: {salida_csv}")

# === GRAFICAR ===
fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()

ax1.plot(rost.index, rost['Temperatura_1'], label='Temp1', color='tab:blue')
ax1.plot(rost.index, rost['Temperatura_2'], label='Temp2', color='tab:green')
ax1.set_ylabel('Temperatura (°C)')
ax1.legend(loc='upper left')

ax2.plot(rost.index, rost['RoR'], label='RoR', color='tab:red', alpha=0.6)
ax2.set_ylabel('RoR (°C/min)')
ax2.legend(loc='upper right')

plt.title('Perfil de Tostado: Temperaturas y RoR')
plt.tight_layout()
plt.show()
