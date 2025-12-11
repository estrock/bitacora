# -*- coding: utf-8 -*-
import pandas as pd
from typing import Dict, Any

def calculate_key_metrics(df_trades: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula las métricas de rendimiento y actividad solicitadas.
    
    Args:
        df_trades: DataFrame de trades preprocesado.
        
    Returns:
        Dict[str, Any]: Diccionario con todas las métricas calculadas.
    """
    if df_trades.empty:
        return {"Error": "El DataFrame está vacío. No se pueden calcular métricas."}

    # Separar trades ganadores y perdedores
    winners = df_trades[df_trades['ganancia/perdida'] > 0]
    losers = df_trades[df_trades['ganancia/perdida'] < 0]
    total_trades = len(df_trades)
    
    metrics = {}
    
    # 1. Métricas de Rentabilidad Global
    metrics['ganancia_promedio_total'] = winners['ganancia/perdida'].mean() if not winners.empty else 0
    metrics['perdida_promedio_total'] = losers['ganancia/perdida'].mean() if not losers.empty else 0
    metrics['rentabilidad_neta_total'] = df_trades['ganancia/perdida'].sum()
    metrics['tasa_de_exito'] = len(winners) / total_trades if total_trades > 0 else 0
    
    # 2. Activo más operado
    metrics['activo_mas_operado'] = df_trades['activo'].mode().iloc[0] if not df_trades['activo'].empty else "N/A"
    
    # 3. Mejora más repetitiva
    metrics['mejora_mas_repetitiva'] = df_trades['mejorar'].mode().iloc[0] if not df_trades['mejorar'].empty else "N/A"
    
    # 4. Rendimiento por Tipo de Entrada
    metrics['rendimiento_por_tipo_entrada'] = df_trades.groupby('tipo entrada')['ganancia/perdida'].agg(['mean', 'count']).reset_index().to_dict('records')

    # Lógica a incluir en data_analyzer.py (si no existe aún)
    df_grouped_asset = df_trades.groupby('activo')['ganancia/perdida'].agg(['mean', 'count']).reset_index()
    metrics['rendimiento_por_activo'] = df_grouped_asset.to_dict('records')

    
    return metrics

def analyze_confirmations(df_trades: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula la asertividad y la ineficiencia de cada confirmación.
    
    Args:
        df_trades: DataFrame de trades preprocesado.
        
    Returns:
        Dict[str, Any]: Resultados del análisis por confirmación.
    """
    conf_results = {}
    
    # Obtener solo las columnas que representan confirmaciones
    conf_cols = [col for col in df_trades.columns if col.startswith('conf_')]
    
    for col in conf_cols:
        conf_name = col.replace('conf_', '')
        
        # Trades donde esta confirmación fue TRUE
        trades_con_conf = df_trades[df_trades[col] == True]
        
        if trades_con_conf.empty:
            conf_results[conf_name] = {'total': 0, 'asertividad': 0, 'ineficiencia': 0, 'rentabilidad_promedio': 0}
            continue

        total_conf_trades = len(trades_con_conf)
        winners_conf = trades_con_conf[trades_con_conf['ganancia/perdida'] > 0]
        losers_conf = trades_con_conf[trades_con_conf['ganancia/perdida'] < 0]

        # Asertividad (Tasa de éxito)
        asertividad = len(winners_conf) / total_conf_trades
        
        # Ineficiencia (Tasa de pérdida)
        ineficiencia = len(losers_conf) / total_conf_trades
        
        conf_results[conf_name] = {
            'total': total_conf_trades,
            'asertividad': round(asertividad * 100, 2), # En porcentaje
            'ineficiencia': round(ineficiencia * 100, 2), # En porcentaje
            'rentabilidad_promedio': trades_con_conf['ganancia/perdida'].mean()
        }

    # Ordenar por rentabilidad promedio para ver las mejores/peores
    sorted_results = sorted(
        conf_results.items(), 
        key=lambda item: item[1]['rentabilidad_promedio'], 
        reverse=True
    )
    
    # Extraer las 3 mejores y 3 peores
    top_3_assertive = sorted_results[:3]
    bottom_3_inefficient = sorted_results[-3:]
    
    return {
        'analisis_completo': conf_results,
        'top_3_confirmaciones_rentables': top_3_assertive,
        'bottom_3_confirmaciones_ineficientes': bottom_3_inefficient
    }