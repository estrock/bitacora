# -*- coding: utf-8 -*-
import json
import os
from typing import List, Dict, Any

# Definición de las rutas de los archivos JSON
DATA_DIR = "data"
TRADES_FILE = os.path.join(DATA_DIR, "movimientos.json")
CONFIRMATIONS_FILE = os.path.join(DATA_DIR, "confirmaciones.json")
IMPROVEMENTS_FILE = os.path.join(DATA_DIR, "mejoras.json")
ACTIVOS = os.path.join(DATA_DIR, "activos.json")

def _initialize_data_directory():
    """Asegura que el directorio de datos exista."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Directorio creado: {DATA_DIR}")

def _load_json_data(filepath: str) -> List[Dict[str, Any]]:
    """Función helper para cargar datos de un archivo JSON."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print(f"Advertencia: Archivo {filepath} no encontrado o vacío. Inicializando con lista vacía.")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: El archivo {filepath} no tiene un formato JSON válido.")
            return []

def _save_json_data(filepath: str, data: List[Dict[str, Any]]):
    """Función helper para guardar datos en un archivo JSON."""
    _initialize_data_directory() # Asegurar la existencia antes de guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        # Uso de indent para que el archivo sea legible
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_all_data() -> Dict[str, List[Dict[str, Any]]]:
    """Carga los tres datasets principales del proyecto."""
    data = {
        'trades': _load_json_data(TRADES_FILE),
        'confirmations': _load_json_data(CONFIRMATIONS_FILE),
        'improvements': _load_json_data(IMPROVEMENTS_FILE)
    }
    return data

# --- Lógica de Persistencia y Agregación (CRUD) ---

def add_trade(trade_data: Dict[str, Any]):
    """Agrega un nuevo registro de trade y guarda el archivo."""
    trades = _load_json_data(TRADES_FILE)
    trades.append(trade_data)
    _save_json_data(TRADES_FILE, trades)
    print(f"Trade agregado exitosamente: {trade_data.get('activo')}")

def add_confirmation(conf_data: Dict[str, str]):
    """Agrega una nueva confirmación al catálogo."""
    confirmations = _load_json_data(CONFIRMATIONS_FILE)
    # Evitar duplicados basados en el campo 'nombre'
    if not any(c['nombre'] == conf_data['nombre'] for c in confirmations):
        confirmations.append(conf_data)
        _save_json_data(CONFIRMATIONS_FILE, confirmations)
        print(f"Confirmación agregada: {conf_data['nombre']}")
    else:
        print(f"Advertencia: La confirmación '{conf_data['nombre']}' ya existe.")

def add_improvement(improv_data: Dict[str, str]):
    """Agrega una nueva mejora al catálogo."""
    improvements = _load_json_data(IMPROVEMENTS_FILE)
    # Evitar duplicados basados en el campo 'nombre'
    if not any(i['nombre'] == improv_data['nombre'] for i in improvements):
        improvements.append(improv_data)
        _save_json_data(IMPROVEMENTS_FILE, improvements)
        print(f"Mejora agregada: {improv_data['nombre']}")
    else:
        print(f"Advertencia: La mejora '{improv_data['nombre']}' ya existe.")

# Para inicialización y pruebas, se crearán archivos JSON de ejemplo en el siguiente paso.