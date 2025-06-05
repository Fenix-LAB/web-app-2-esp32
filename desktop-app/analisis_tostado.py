import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import sys

# Estilo de las gráficas
plt.style.use('default')
plt.rcParams['figure.figsize'] = [12, 8]
plt.rcParams['font.size'] = 12
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3

# Verifica que todas las columnas requeridas estén presentes
def validate_columns(df, required):
    for col in required:
        if col not in df.columns:
            print(f"❌ ERROR: Falta la columna requerida: '{col}'")
            sys.exit(1)

# Carga y preprocesamiento del archivo CSV
def load_and_process_data(filepath):
    df = pd.read_csv(filepath, skiprows=1)
    validate_columns(df, ['Fecha', 'Hora', 'Etapa', 'Temperatura_1', 'Temperatura_2', 'R', 'G', 'B'])

    df = df[df['Hora'].str.contains(r'\d{2}:\d{2}:\d{2}', na=False)]
    df['Datetime'] = pd.to_datetime(df['Fecha'] + ' ' + df['Hora'], format="%Y-%m-%d %H:%M:%S", errors='coerce')
    df = df.dropna(subset=['Datetime'])
    df = df[df['Etapa'] == 'Tostado'].copy()

    df['Time_seconds'] = (df['Datetime'] - df['Datetime'].iloc[0]).dt.total_seconds()
    df['Time_minutes'] = df['Time_seconds'] / 60
    df = df.rename(columns={'Temperatura_1': 'T1_Grano', 'Temperatura_2': 'T2_Tambor'})
    df['RoR'] = df['T1_Grano'].diff().rolling(window=10, min_periods=1).mean() * 60

    return df

# Fases de secado y maillard
def identify_phases(df):
    key_points = {}
    min_idx = df['T1_Grano'].idxmin()
    t_inicio = df.loc[min_idx, 'Time_minutes']

    # Fase de secado (100°C a 150°C)
    secado_end = df[(df.index > min_idx) & (df['T1_Grano'] >= 150)]
    if not secado_end.empty:
        sec_end_row = secado_end.iloc[0]
        key_points['Secado'] = {
            'Inicio': t_inicio,
            'Fin': sec_end_row['Time_minutes'],
            'Duración': sec_end_row['Time_minutes'] - t_inicio
        }
    else:
        key_points['Secado'] = {'Inicio': t_inicio, 'Fin': t_inicio, 'Duración': 0}

    # Fase de Maillard (150°C a 180°C)
    if not secado_end.empty:
        maillard_end = df[(df.index > secado_end.index[0]) & (df['T1_Grano'] >= 180)]
        if not maillard_end.empty:
            mai_end_row = maillard_end.iloc[0]
            key_points['Maillard'] = {
                'Inicio': sec_end_row['Time_minutes'],
                'Fin': mai_end_row['Time_minutes'],
                'Duración': mai_end_row['Time_minutes'] - sec_end_row['Time_minutes']
            }
        else:
            key_points['Maillard'] = {
                'Inicio': sec_end_row['Time_minutes'],
                'Fin': sec_end_row['Time_minutes'],
                'Duración': 0
            }
    else:
        key_points['Maillard'] = {'Inicio': t_inicio, 'Fin': t_inicio, 'Duración': 0}

    return key_points

# Eventos clave del perfil
def identify_key_events(df):
    key_points = {}
    key_points['Tiempo Total'] = df['Time_minutes'].iloc[-1]

    # Primer crack (T1 entre 190 y 205 y RoR más alto)
    crack_df = df[(df['T1_Grano'] >= 190) & (df['T1_Grano'] <= 205)]
    if not crack_df.empty:
        crack_idx = crack_df['RoR'].idxmax()
        key_points['Primer Crack'] = {
            'Tiempo': df.loc[crack_idx, 'Time_minutes'],
            'T1': df.loc[crack_idx, 'T1_Grano'],
            'T2': df.loc[crack_idx, 'T2_Tambor'],
            'RoR': df.loc[crack_idx, 'RoR'],
            'es_RoR': False
        }

    # Pico RoR
    ror_peak_idx = df['RoR'].idxmax()
    key_points['Pico RoR'] = {
        'Tiempo': df.loc[ror_peak_idx, 'Time_minutes'],
        'T1': df.loc[ror_peak_idx, 'RoR'],
        'RoR': df.loc[ror_peak_idx, 'RoR'],
        'es_RoR': True
    }

    # Temperaturas específicas alcanzadas
    min_idx = df['T1_Grano'].idxmin()
    for temp in [150, 170, 180, 200]:
        subset = df[(df.index > min_idx) & (df['T1_Grano'] > temp)]
        if not subset.empty:
            idx = subset.index[0]
            key_points[f'T1 alcanza {temp}°C'] = {
                'Tiempo': df.loc[idx, 'Time_minutes'],
                'T1': df.loc[idx, 'T1_Grano'],
                'es_RoR': False
            }
        else:
            key_points[f'T1 alcanza {temp}°C'] = {'Tiempo': 0, 'T1': 0, 'es_RoR': False}

    key_points['Correlación T1-T2'] = df['T1_Grano'].corr(df['T2_Tambor'])

    return key_points

# Análisis de RGB para identificar cambios de color
def analyze_rgb(df):
    df['Luminosidad'] = df[['R', 'G', 'B']].mean(axis=1)
    df['Cambio_RGB'] = df['Luminosidad'].diff().abs()
    max_idx = df['Cambio_RGB'].idxmax()
    return {
        'Máximo Cambio RGB': {
            'Tiempo': df.loc[max_idx, 'Time_minutes'],
            'T1': df.loc[max_idx, 'T1_Grano'],
            'RGB': (df.loc[max_idx, 'R'], df.loc[max_idx, 'G'], df.loc[max_idx, 'B']),
            'Luminosidad': df.loc[max_idx, 'Luminosidad']
        }
    }

# Creación del PDF con gráfica y reporte
def create_pdf_report(df, eventos, fases, rgb, filename="reporte_tostado_final.pdf"):
    with PdfPages(filename) as pdf:
        fig, ax1 = plt.subplots()
        ax1.plot(df['Time_minutes'], df['T1_Grano'], 'r-', label='T1 (Grano)')
        ax1.plot(df['Time_minutes'], df['T2_Tambor'], 'm-', label='T2 (Tambor)')
        ax2 = ax1.twinx()
        ax2.plot(df['Time_minutes'], df['RoR'], 'b-', label='RoR', alpha=0.7)

        ax1.set_xlabel("Tiempo (min)")
        ax1.set_ylabel("Temperatura (°C)", color='red')
        ax2.set_ylabel("RoR (°C/min)", color='blue')
        ax1.set_title("Perfil de Tostado con Eventos Clave")

        for label, data in eventos.items():
            if isinstance(data, dict) and 'Tiempo' in data:
                if data.get('es_RoR', False):
                    ax2.scatter(data['Tiempo'], data['T1'], label=label, s=100)
                    ax2.text(data['Tiempo'], data['T1'] + 1, label, fontsize=9, ha='center')
                else:
                    ax1.scatter(data['Tiempo'], data['T1'], label=label, s=100)
                    ax1.text(data['Tiempo'], data['T1'] + 5, label, fontsize=9, ha='center')

        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        plt.tight_layout()
        pdf.savefig()
        plt.close()

        # Texto del reporte
        lines = []
        lines.append("=== REPORTE DE TOSTADO ===")
        lines.append(f"Tiempo total: {eventos['Tiempo Total']:.2f} minutos\n")

        for fase, val in fases.items():
            lines.append(f"--- Fase de {fase} ---")
            for k, v in val.items():
                lines.append(f"{k}: {v:.2f} min")
            lines.append("")

        for k, v in eventos.items():
            if isinstance(v, dict):
                lines.append(f"--- {k} ---")
                for subk, subv in v.items():
                    if subk != 'es_RoR':
                        lines.append(f"{subk}: {subv:.2f}")
                lines.append("")

        lines.append("--- Correlación T1-T2 ---")
        lines.append(f"{eventos['Correlación T1-T2']:.3f}\n")

        rgb_ev = rgb['Máximo Cambio RGB']
        lines.append("--- Análisis de Color ---")
        lines.append(f"Tiempo: {rgb_ev['Tiempo']:.2f} min")
        lines.append(f"T1: {rgb_ev['T1']:.2f} °C")
        lines.append(f"Luminosidad: {rgb_ev['Luminosidad']:.2f}")
        lines.append(f"RGB: {rgb_ev['RGB']}")

        # Paginación en caso de texto largo
        for i in range(0, len(lines), 30):
            fig, ax = plt.subplots(figsize=(11, 8))
            ax.axis('off')
            ax.text(0.05, 0.95, "\n".join(lines[i:i+30]), va='top', ha='left', fontsize=12, family='monospace')
            pdf.savefig()
            plt.close()

        print(f"✅ PDF generado como: {filename}")

# Función principal
def main(filepath):
    df = load_and_process_data(filepath)
    fases = identify_phases(df)
    eventos = identify_key_events(df)
    rgb = analyze_rgb(df)
    create_pdf_report(df, eventos, fases, rgb)

# Llamada al script (ajusta el nombre según tu archivo CSV)
if __name__ == "__main__":
    main("data_2025-06-03_18-22-08.csv")
