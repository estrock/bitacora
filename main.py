# -*- coding: utf-8 -*-
import pandas as pd
import data_loader as dl
import preprocessor as pp
import analyzer as an
import ui_manager as ui
import os
import json

# --- Funciones de Inicialización de Datos de Ejemplo ---

def create_initial_json_files():
    """Crea los archivos JSON iniciales con datos de ejemplo si no existen."""
    # Asegurarse de que el directorio exista (data_loader ya lo hace, pero por seguridad)
    if not os.path.exists(dl.DATA_DIR):
        os.makedirs(dl.DATA_DIR)

    # 1. Movimientos de Ejemplo (Trades)
    if not os.path.exists(dl.TRADES_FILE) or os.path.getsize(dl.TRADES_FILE) == 0:
        trades_ejemplo = [
            {
                "activo": "EURUSD",
                "accion": "COMPRA",
                "resultado": 1.0750,
                "ganancia/perdida": 45.20,
                "tipo entrada": "Rebrote",
                "mejorar": "Toma Parcial",
                "confirmaciones": {"hch": True, "fuerza": True}
            },
            {
                "activo": "GBPUSD",
                "accion": "VENTA",
                "resultado": 1.2500,
                "ganancia/perdida": -30.50,
                "tipo entrada": "Ruptura",
                "mejorar": "Ninguna",
                "confirmaciones": {"noticia": True, "fuerza": False}
            },
            {
                "activo": "EURUSD",
                "accion": "COMPRA",
                "resultado": 1.0780,
                "ganancia/perdida": 12.00,
                "tipo entrada": "Rebrote",
                "mejorar": "Manejo Riego",
                "confirmaciones": {"fuerza": True, "volatilidad": True}
            },
            {
                "activo": "AUDUSD",
                "accion": "VENTA",
                "resultado": 0.6550,
                "ganancia/perdida": -55.00,
                "tipo entrada": "Rango",
                "mejorar": "Toma Parcial",
                "confirmaciones": {"hch": False, "volatilidad": True}
            },
            # Ejemplo con nueva confirmación (demostrando el esquema dinámico)
            {
                "activo": "EURUSD",
                "accion": "COMPRA",
                "resultado": 1.0800,
                "ganancia/perdida": 80.50,
                "tipo entrada": "Rebrote",
                "mejorar": "Manejo Riego",
                "confirmaciones": {"noticia": True, "divergencia": True, "hch": True}
            }
        ]
        with open(dl.TRADES_FILE, 'w', encoding='utf-8') as f:
            json.dump(trades_ejemplo, f, indent=4, ensure_ascii=False)
        print(f"Archivo de trades de ejemplo creado en: {dl.TRADES_FILE}")


    # 2. Confirmaciones de Ejemplo (Catálogo)
    if not os.path.exists(dl.CONFIRMATIONS_FILE) or os.path.getsize(dl.CONFIRMATIONS_FILE) == 0:
        confirmations_ejemplo = [
            {"nombre": "hch", "descripcion": "Formación Hombro-Cabeza-Hombro."},
            {"nombre": "fuerza", "descripcion": "Indicador de fuerza relativa."},
            {"nombre": "noticia", "descripcion": "Activado por evento noticioso importante."},
            {"nombre": "volatilidad", "descripcion": "Alta volatilidad del mercado."}
        ]
        with open(dl.CONFIRMATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(confirmations_ejemplo, f, indent=4, ensure_ascii=False)
        print(f"Archivo de confirmaciones de ejemplo creado en: {dl.CONFIRMATIONS_FILE}")


    # 3. Mejoras de Ejemplo (Catálogo)
    if not os.path.exists(dl.IMPROVEMENTS_FILE) or os.path.getsize(dl.IMPROVEMENTS_FILE) == 0:
        improvements_ejemplo = [
            {"nombre": "Toma Parcial", "descripcion": "Cierre de una porción de la posición."},
            {"nombre": "Manejo Riego", "descripcion": "Ajuste de stop loss durante el trade."},
            {"nombre": "Ninguna", "descripcion": "No se aplicó ninguna mejora."},
        ]
        with open(dl.IMPROVEMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(improvements_ejemplo, f, indent=4, ensure_ascii=False)
        print(f"Archivo de mejoras de ejemplo creado en: {dl.IMPROVEMENTS_FILE}")

def main():
    """Punto de entrada de la aplicación."""
    print("--- Iniciando Proyecto de Análisis de Trades ---")

    # 1. Crear archivos de datos de ejemplo si no existen
    create_initial_json_files()
    
    # 2. Ensamblar las funciones para inyección de dependencias
    loader_functions = {
        'load_all_data': dl.load_all_data,
        'add_trade': dl.add_trade,
        'add_confirmation': dl.add_confirmation,
        'add_improvement': dl.add_improvement,
    }
    
    analyzer_functions = {
        'calculate_key_metrics': an.calculate_key_metrics,
        'analyze_confirmations': an.analyze_confirmations,
    }

    # 3. Iniciar la aplicación de Tkinter
    app = ui.TradingAnalysisApp(
        data_loader_funcs=loader_functions,
        preprocessor_func=pp.preprocess_data,
        analyzer_funcs=analyzer_functions
    )
    
    # Asegurarse de que el análisis inicial se muestre correctamente al inicio.
    app.mainloop()

if __name__ == "__main__":
    # Aseguramos que pandas pueda usar Float64 para cálculos
    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    main()