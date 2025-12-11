# -*- coding: utf-8 -*-
import pandas as pd
from typing import Dict, List, Any

def preprocess_data(raw_trades: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Toma los datos brutos de trades, los convierte a DataFrame, expande
    el campo anidado 'confirmaciones' y realiza limpieza básica.
    
    Args:
        raw_trades: Lista de diccionarios con los datos de movimientos.
        
    Returns:
        pd.DataFrame: DataFrame limpio y listo para el análisis.
    """
    if not raw_trades:
        print("Advertencia: No hay datos de trades para preprocesar.")
        # Retorna un DataFrame vacío con las columnas esperadas
        return pd.DataFrame(columns=[
            'activo', 'accion', 'resultado', 'ganancia/perdida', 
            'tipo entrada', 'mejorar'
        ])

    df = pd.DataFrame(raw_trades)

    # 1. Expansión del campo 'confirmaciones' (La clave para esquema dinámico)
    # Crea nuevas columnas por cada clave en el diccionario anidado.
    if 'confirmaciones' in df.columns:
        # Usa json_normalize si fuera un JSON más complejo, pero para un diccionario
        # simple dentro de una columna, .apply(pd.Series) es más directo.
        
        # Primero, aseguramos que todos los valores en 'confirmaciones' son diccionarios
        df['confirmaciones'] = df['confirmaciones'].apply(lambda x: x if isinstance(x, dict) else {})
        
        conf_df = df['confirmaciones'].apply(pd.Series).fillna(False).astype(bool)
        
        # Renombrar columnas para claridad (ej. 'hch' -> 'conf_hch')
        conf_df.columns = ['conf_' + col for col in conf_df.columns]
        
        # Combinar el DataFrame original con las nuevas columnas de confirmación
        df = pd.concat([df.drop('confirmaciones', axis=1), conf_df], axis=1)

    # 2. Limpieza básica y conversión de tipos
    # Asegurar que la columna numérica clave esté en el formato correcto
    df['ganancia/perdida'] = pd.to_numeric(df['ganancia/perdida'], errors='coerce')
    df['resultado'] = pd.to_numeric(df['resultado'], errors='coerce')
    
    # Rellenar valores nulos de ganancia/perdida con 0 (o la estrategia más adecuada)
    df['ganancia/perdida'] = df['ganancia/perdida'].fillna(0)

    print(f"Datos preprocesados. Columnas expandidas: {list(conf_df.columns) if 'conf_df' in locals() else 'Ninguna'}")
    return df