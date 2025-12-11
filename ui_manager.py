# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict, Any

# Importar las funciones de los módulos (se importarán en main.py y se pasarán aquí)

class TradingAnalysisApp(tk.Tk):
    """Clase principal de la aplicación Tkinter."""
    def __init__(self, data_loader_funcs, preprocessor_func, analyzer_funcs):
        super().__init__()
        self.title("Análisis y Minería de Datos de Trades")
        self.geometry("1000x800")
        
        # Almacenar referencias a las funciones externas (DIP - Inversión de Dependencias)
        self.loader = data_loader_funcs
        self.preprocess = preprocessor_func
        self.analyze = analyzer_funcs
        
        # Variables de estado
        self.raw_data = self.loader['load_all_data']()
        self.df_trades = self.preprocess(self.raw_data['trades'])
        
        self.create_widgets()
        self.run_analysis() # Ejecutar el análisis inicial

    def create_widgets(self):
        """Configura la estructura de pestañas de la interfaz."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Pestaña 1: Análisis (Dashboard)
        self.analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_frame, text="Análisis de Rendimiento")
        self.setup_analysis_tab()
        
        # Pestaña 2: Agregar Datos (Formularios)
        self.add_data_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_data_frame, text="Agregar Registros")
        self.setup_add_data_tab()

        # Pestaña 3: Todos lo trades
        self.read_trades_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.read_trades_frame, text="Consultar Trades")
        self.read_trades_tab()

    # --- PESTAÑA DE CONSULTAR TRADES ---

    def read_trades_tab(self):
        """
        Configura la pestaña para mostrar todos los trades en una tabla (ttk.Treeview),
        consolidando todas las confirmaciones activas en una sola columna.
        """
        container = self.read_trades_frame
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        if self.df_trades.empty:
            ttk.Label(container, text="No hay trades registrados para mostrar.").pack(pady=20)
            return

        # 1. Identificar las columnas de confirmación
        all_cols = list(self.df_trades.columns)
        self.conf_cols_names = [col for col in all_cols if col.startswith('conf_')]
        
        # 2. Definir las columnas a mostrar en el Treeview
        # Excluir las columnas de confirmación individuales y la columna 'resultado'.
        display_columns = [
            col for col in all_cols 
            if col not in self.conf_cols_names and col != 'resultado'
        ]
        display_columns.append('Confirmaciones') 

        # Crear el Treeview
        self.trades_tree = ttk.Treeview(container, columns=display_columns, show='headings')
        
        # Configurar Scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.trades_tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.trades_tree.xview)
        self.trades_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Colocar Treeview y Scrollbars usando Grid
        self.trades_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        # Configurar encabezados y ancho de columna
        for col in display_columns:
                
            # Formateo del encabezado (ej: 'ganancia/perdida' -> 'Ganancia/Perdida')
            header_text = col.replace('_', ' ').title()
            self.trades_tree.heading(col, text=header_text, anchor='w')
            
            # Ajuste de ancho de columna
            if 'ganancia/perdida' in col:
                self.trades_tree.column(col, width=120, anchor='center')
            elif col == 'Confirmaciones': # Columna consolidada más ancha
                self.trades_tree.column(col, width=250, anchor='w')
            else:
                self.trades_tree.column(col, width=100, anchor='w')

        self.populate_trades_tree()

    def populate_trades_tree(self):
        """
        Llena el Treeview con los datos del DataFrame de trades,
        utilizando la lista de columnas de confirmación almacenada.
        """
        if not hasattr(self, 'trades_tree'):
            return 
            
        # Determinar las columnas de confirmación por si la lista ha cambiado (e.g., después de agregar una nueva conf.)
        all_cols = list(self.df_trades.columns)
        conf_cols = [col for col in all_cols if col.startswith('conf_')]
        
        # Excluir la columna 'resultado' y las de confirmación del Treeview
        non_conf_cols = [col for col in all_cols if col not in conf_cols and col != 'resultado']

        # Limpiar datos existentes
        self.trades_tree.delete(*self.trades_tree.get_children())
        
        # Insertar nuevas filas
        for index, row in self.df_trades.iterrows():
            row_values = []
            
            # 1. Agregar valores de columnas no-confirmación (excluyendo 'resultado')
            for col in non_conf_cols:
                row_values.append(row[col])
            
            # 2. Consolidar confirmaciones
            active_confs = []
            for conf_col in conf_cols:
                # Si la confirmación es True
                if row[conf_col]: 
                    # Extraer el nombre de la confirmación (ej: 'conf_hch' -> 'HCH')
                    conf_name = conf_col.split('_', 1)[1].upper()
                    active_confs.append(conf_name)
            
            # 3. Formatear la cadena de confirmaciones
            confs_str = ", ".join(active_confs) if active_confs else "Ninguna"
            
            # 4. Agregar la cadena consolidada al final
            row_values.append(confs_str)
            
            # Insertar la fila
            self.trades_tree.insert("", "end", values=row_values)


    # --- PESTAÑA DE AGREGAR REGISTROS ---
    
    def setup_add_data_tab(self):
        """Configura los formularios para Trades, Confirmaciones y Mejoras."""
        main_container = ttk.Frame(self.add_data_frame, padding="10")
        main_container.pack(fill='both', expand=True)

        # 1. Formulario para agregar TRADE
        trade_frame = ttk.LabelFrame(main_container, text="Nuevo Movimiento (Trade)", padding="10")
        trade_frame.pack(fill='x', pady=10, padx=10)
        
        self.trade_vars = {
            "activo": tk.StringVar(), "accion": tk.StringVar(), 
            # "resultado" omitido permanentemente
            "ganancia/perdida": tk.DoubleVar(),
            "tipo entrada": tk.StringVar(), "mejorar": tk.StringVar(value="N/A")
        }
        self.conf_vars = {}

        activos = [
            "ORO",        # Gold (in Spanish) - CORREGIDO: Coma agregada
            "DJ30",     # Dow Jones 30 Index
            "NAS100",    # NASDAQ 100 Index
            "SP500",     # S&P 500 Index            
            "BTCUSD",    # Bitcoin / US Dollar
            "AUDJPY",    # Australian Dollar / Japanese Yen
            "AUDUSD",    # Australian Dollar / US Dollar
            "CADJPY",    # Canadian Dollar / Japanese Yen
            "CHFJPY",    # Franco dolar / yen
            "EURGBP",    # Euro / British Pound
            "EURUSD",    # Euro / US Dollar
            "EURJPY",    # Euro / Japanese Yen
            "GBPJPY",    # British Pound / Japanese Yen
            "GBPUSD",    # British Pound / US Dollar
            "NZDUSD",    # New Zealand Dollar / US Dollar
            "USDCAD",    # US Dollar / Canadian Dollar
            "USDCHF",    # US Dollar / Swiss Franc
            "USDJPY",    # US Dollar / Japanese Yen
        ]

        ordenes=["BUY","SELL","SELL LIMIT","BUY LIMIT","SELL STOP","BUY STOP"]
        
        rowvar =0
        
        # Campo 1: Activo (Combobox)
        ttk.Label(trade_frame, text="Activo:").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Combobox(trade_frame, textvariable=self.trade_vars["activo"], values=activos, width=10).grid(row=0, column=1, padx=5, pady=5)
        rowvar = rowvar +1

        # Campo 2: Tipo de orden (Combobox)
        ttk.Label(trade_frame, text="tipo de orden:").grid(row=rowvar, column=0, padx=5, pady=2, sticky='w')
        ttk.Combobox(trade_frame, textvariable=self.trade_vars["accion"], values=ordenes, width=10).grid(row=rowvar, column=1, padx=5, pady=5)
        rowvar = rowvar +1

        # Campo 3: Ganancia/Pérdida (Entry)
        ttk.Label(trade_frame, text="Ganancia/Pérdida:").grid(row=rowvar, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(trade_frame, textvariable=self.trade_vars["ganancia/perdida"]).grid(row=rowvar, column=1, padx=5, pady=2, sticky='ew')
        rowvar = rowvar +1
        
        # Campo 4: Tipo Entrada (Entry)
        ttk.Label(trade_frame, text="Tipo Entrada:").grid(row=rowvar, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(trade_frame, textvariable=self.trade_vars["tipo entrada"]).grid(row=rowvar, column=1, padx=5, pady=2, sticky='ew')
        rowvar = rowvar +1
        
        # Campo 5: ¿Que puedo mejorar? (Entry)
        ttk.Label(trade_frame, text="¿Que puedo mejorar?:").grid(row=rowvar, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(trade_frame, textvariable=self.trade_vars["mejorar"]).grid(row=rowvar, column=1, padx=5, pady=2, sticky='ew')
        rowvar = rowvar +1

        # Generar Checkbuttons para Confirmaciones dinámicamente
        self.conf_check_frame = ttk.LabelFrame(trade_frame, text="Confirmaciones")
        # CORREGIDO: rowspan se ajusta a 5 para cubrir las filas 0 a 4
        self.conf_check_frame.grid(row=0, column=2, rowspan=5, padx=10, sticky='ns')
        self.update_confirmation_checks()
        
        # Botón
        ttk.Button(trade_frame, text="Agregar Trade", command=self.handle_add_trade).grid(row=rowvar, column=0, columnspan=2, pady=10)
        rowvar = rowvar+1

        # 2. Formulario para agregar CONFIRMACIÓN
        conf_frame = ttk.LabelFrame(main_container, text="Nueva Confirmación (Catálogo)", padding="10")
        conf_frame.pack(fill='x', pady=10, padx=10)
        self.new_conf_name = tk.StringVar()
        self.new_conf_desc = tk.StringVar()
        ttk.Label(conf_frame, text="Nombre (ID):").grid(row=0, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(conf_frame, textvariable=self.new_conf_name).grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        ttk.Label(conf_frame, text="Descripción:").grid(row=1, column=0, padx=5, pady=2, sticky='w')
        ttk.Entry(conf_frame, textvariable=self.new_conf_desc).grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        ttk.Button(conf_frame, text="Agregar Confirmación", command=self.handle_add_confirmation).grid(row=2, column=0, columnspan=2, pady=10)

    def update_confirmation_checks(self):
        """Actualiza la lista de Checkbuttons de confirmaciones en el formulario de Trade."""
        # Limpiar widgets existentes
        for widget in self.conf_check_frame.winfo_children():
            widget.destroy()
        self.conf_vars = {} # Resetear variables
            
        # Recargar catálogo para obtener las últimas
        self.raw_data = self.loader['load_all_data']()
        confirmations = self.raw_data['confirmations']
        
        for i, conf in enumerate(confirmations):
            name = conf['nombre']
            var = tk.BooleanVar(value=False)
            self.conf_vars[name] = var
            ttk.Checkbutton(self.conf_check_frame, text=name, variable=var).grid(row=i, column=0, sticky='w')


    def handle_add_trade(self):
        """Procesa y agrega un nuevo trade a través del data_loader."""
        try:
            new_trade = {
                "activo": self.trade_vars["activo"].get(),
                "accion": self.trade_vars["accion"].get(),
                # "resultado" fue removido de trade_vars
                "ganancia/perdida": self.trade_vars["ganancia/perdida"].get(),
                "tipo entrada": self.trade_vars["tipo entrada"].get(),
                "mejorar": self.trade_vars["mejorar"].get(),
                "confirmaciones": {k: v.get() for k, v in self.conf_vars.items() if v.get()} # Solo True
            }
            
            # Validación básica
            if not new_trade['activo'] or not new_trade['tipo entrada']:
                messagebox.showerror("Error de entrada", "Los campos Activo y Tipo Entrada son obligatorios.")
                return

            self.loader['add_trade'](new_trade)
            messagebox.showinfo("Éxito", "Trade agregado y datos guardados.")
            
            # Recargar datos y análisis
            self.raw_data = self.loader['load_all_data']()
            self.df_trades = self.preprocess(self.raw_data['trades'])
            self.run_analysis()
            
            # Actualizar la tabla de trades en la pestaña 3 si ya fue inicializada
            if hasattr(self, 'trades_tree'):
                self.populate_trades_tree()
            
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al agregar trade: {e}")

    def handle_add_confirmation(self):
        """Procesa y agrega una nueva confirmación al catálogo."""
        name = self.new_conf_name.get().strip().lower()
        desc = self.new_conf_desc.get().strip()

        if not name or not desc:
            messagebox.showerror("Error de entrada", "Nombre y Descripción son obligatorios.")
            return

        try:
            self.loader['add_confirmation']({"nombre": name, "descripcion": desc})
            messagebox.showinfo("Éxito", f"Confirmación '{name}' agregada.")
            self.new_conf_name.set("")
            self.new_conf_desc.set("")
            self.update_confirmation_checks() # Actualizar los checkbuttons
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al agregar confirmación: {e}")

    # --- PESTAÑA DE ANÁLISIS ---

    def setup_analysis_tab(self):
        """Configura el layout del dashboard de análisis con scrollbar."""
        
        # Configurar Scrollbar Vertical
        vscrollbar = ttk.Scrollbar(self.analysis_frame, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)

        # Crear Canvas para hacer scroll
        canvas = tk.Canvas(self.analysis_frame, yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)

        # Vincular Scrollbar al Canvas
        vscrollbar.config(command=canvas.yview)

        # Crear el Frame interior que contendrá todo el dashboard
        self.dashboard_frame = ttk.Frame(canvas, padding="10")
        
        # Colocar el dashboard_frame dentro del canvas
        canvas.create_window((0, 0), window=self.dashboard_frame, anchor="nw")

        # Configurar el scroll region del canvas cuando cambie el tamaño del frame interior
        self.dashboard_frame.bind("<Configure>", 
            lambda event: canvas.config(scrollregion=canvas.bbox("all"))
        )
        # Asegurar que el frame se expanda horizontalmente con el canvas
        canvas.bind('<Configure>', 
            lambda e: canvas.itemconfig(canvas.find_all()[0], width=e.width)
        )


        # --- Estructura Grid del Dashboard ---

        # Marco para las métricas clave (fila 0, columna 0)
        self.metrics_frame = ttk.LabelFrame(self.dashboard_frame, text="Métricas Globales", padding="10")
        self.metrics_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Marco para el análisis de confirmaciones (fila 0, columna 1)
        self.conf_analysis_frame = ttk.LabelFrame(self.dashboard_frame, text="Asertividad de Confirmaciones", padding="10")
        self.conf_analysis_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Marco para las visualizaciones (fila 1, ocupa ambas columnas)
        # NOTA: Los 3 gráficos se incrustarán aquí, ocupando más espacio horizontalmente.
        self.plot_frame = ttk.LabelFrame(self.dashboard_frame, text="Visualizaciones", padding="10")
        self.plot_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # Configuración de pesos para el frame interior (dashboard_frame)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(1, weight=1)
        # La fila 1 (gráficas) necesita peso para expandirse
        self.dashboard_frame.grid_rowconfigure(1, weight=1) 

    def run_analysis(self):
        """Ejecuta el análisis y actualiza la UI."""
        
        # 1. Obtener los resultados del análisis
        key_metrics = self.analyze['calculate_key_metrics'](self.df_trades)
        conf_analysis = self.analyze['analyze_confirmations'](self.df_trades)
        
        # 2. Mostrar Métricas Globales
        self.display_metrics(key_metrics)
        
        # 3. Mostrar Análisis de Confirmaciones
        self.display_confirmation_analysis(conf_analysis)
        
        # 4. Generar y mostrar las visualizaciones
        self.plot_analysis(key_metrics, conf_analysis)

    def display_metrics(self, metrics: Dict[str, Any]):
        """Actualiza la sección de métricas globales."""
        # Limpiar frame
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()

        # Muestra la Tasa de Éxito
        ttk.Label(self.metrics_frame, text="Tasa de Éxito Total:").grid(row=0, column=0, sticky='w')
        ttk.Label(self.metrics_frame, text=f"{metrics.get('tasa_de_exito', 0.0) * 100:.2f}%", font=('Arial', 12, 'bold')).grid(row=0, column=1, sticky='e')

        # Muestra Ganancia/Pérdida Promedio
        ttk.Label(self.metrics_frame, text="Ganancia Promedio (+):").grid(row=1, column=0, sticky='w')
        ttk.Label(self.metrics_frame, text=f"{metrics.get('ganancia_promedio_total', 0.0):.2f}", foreground='green').grid(row=1, column=1, sticky='e')
        
        ttk.Label(self.metrics_frame, text="Pérdida Promedio (-):").grid(row=2, column=0, sticky='w')
        ttk.Label(self.metrics_frame, text=f"{metrics.get('perdida_promedio_total', 0.0):.2f}", foreground='red').grid(row=2, column=1, sticky='e')
        
        # Activo y Mejora
        ttk.Label(self.metrics_frame, text="Activo Más Operado:").grid(row=3, column=0, sticky='w')
        ttk.Label(self.metrics_frame, text=metrics.get('activo_mas_operado', 'N/A')).grid(row=3, column=1, sticky='e')
        
        ttk.Label(self.metrics_frame, text="Mejora Más Repetitiva:").grid(row=4, column=0, sticky='w')
        ttk.Label(self.metrics_frame, text=metrics.get('mejora_mas_repetitiva', 'N/A')).grid(row=4, column=1, sticky='e')
        
    def display_confirmation_analysis(self, conf_analysis: Dict[str, Any]):
        """Actualiza la sección de análisis de confirmaciones."""
        for widget in self.conf_analysis_frame.winfo_children():
            widget.destroy()
            
        ttk.Label(self.conf_analysis_frame, text="Top 3 Confirmaciones Más Rentables:", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 5))
        
        row = 1
        for name, data in conf_analysis['top_3_confirmaciones_rentables']:
            ttk.Label(self.conf_analysis_frame, text=f"{name}:").grid(row=row, column=0, sticky='w', padx=5)
            ttk.Label(self.conf_analysis_frame, text=f"Promedio: {data['rentabilidad_promedio']:.2f} (Éxito: {data['asertividad']}%)", foreground='green').grid(row=row, column=1, sticky='e', padx=5)
            row += 1

        ttk.Label(self.conf_analysis_frame, text="Bottom 3 Confirmaciones Más Ineficientes:", font=('Arial', 10, 'bold')).grid(row=row, column=0, columnspan=2, sticky='w', pady=(10, 5))
        row += 1
        
        for name, data in conf_analysis['bottom_3_confirmaciones_ineficientes']:
            ttk.Label(self.conf_analysis_frame, text=f"{name}:").grid(row=row, column=0, sticky='w', padx=5)
            ttk.Label(self.conf_analysis_frame, text=f"Promedio: {data['rentabilidad_promedio']:.2f} (Fallo: {data['ineficiencia']}%)", foreground='red').grid(row=row, column=1, sticky='e', padx=5)
            row += 1

    def plot_analysis(self, key_metrics, conf_analysis):
        """Genera y muestra las visualizaciones."""
        # Limpiar frame de plots
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        if self.df_trades.empty:
             ttk.Label(self.plot_frame, text="No hay datos suficientes para generar gráficos.").pack(pady=20)
             return

        # Figura principal con 3 subplots en una fila
        fig = plt.Figure(figsize=(15, 6), dpi=100) # Se aumenta el ancho para los 3 gráficos
        
        # --- Gráfico 1: Distribución de Ganancia/Pérdida (Histograma) ---
        ax1 = fig.add_subplot(131)
        self.df_trades['ganancia/perdida'].plot(kind='hist', bins=20, ax=ax1, color='skyblue', edgecolor='black')
        ax1.set_title('Distribución de Ganancia/Pérdida')
        ax1.set_xlabel('Valor (€/$)')
        ax1.axvline(0, color='gray', linestyle='--') # Línea en cero

        # --- Gráfico 2: Rendimiento por Tipo de Entrada (Barras) ---
        ax2 = fig.add_subplot(132)
        rend_data_entrada = pd.DataFrame(key_metrics['rendimiento_por_tipo_entrada'])
        if not rend_data_entrada.empty:
            rend_data_entrada.set_index('tipo entrada')['mean'].plot(kind='bar', ax=ax2, color=['green' if x > 0 else 'red' for x in rend_data_entrada['mean']])
            ax2.set_title('Rentabilidad Promedio por Tipo de Entrada')
            ax2.set_ylabel('Rendimiento Promedio')
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax2.text(0.5, 0.5, 'No hay datos por Tipo de Entrada', transform=ax2.transAxes, ha='center')

        # --- Gráfico 3: Rendimiento por Activo (Barras) ---
        ax3 = fig.add_subplot(133)
        rend_data_activo = pd.DataFrame(key_metrics['rendimiento_por_activo'])
        if not rend_data_activo.empty:
            rend_data_activo.set_index('activo')['mean'].plot(kind='bar', ax=ax3, color=['green' if x > 0 else 'red' for x in rend_data_activo['mean']])
            ax3.set_title('Rentabilidad Promedio por Activo')
            ax3.set_ylabel('Rendimiento Promedio')
            ax3.tick_params(axis='x', rotation=45)
        else:
            ax3.text(0.5, 0.5, 'No hay datos por Activo', transform=ax3.transAxes, ha='center')

        fig.tight_layout() # Ajuste automático para evitar solapamiento

        # Incrustar el gráfico en Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()