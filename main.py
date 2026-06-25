import customtkinter as ctk
import sqlite3
from datetime import datetime

ctk.set_appearance_mode("Dark")

# Paleta inspirada en el ecosistema Apple (Modo Oscuro)
BG_MAIN = "#000000"           
BG_CARD = "#1C1C1E"           
BG_INPUT = "#2C2C2E"          
COLOR_NARANJA = "#F97316"     
COLOR_NARANJA_HOVER = "#EA580C"
TEXTO_SECUNDARIO = "#8E8E93"  
COLOR_INGRESO = "#32D74B"     
COLOR_GASTO = "#FF453A"       

class FinanceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mis Finanzas")
        self.geometry("950x650") 
        self.configure(fg_color=BG_MAIN) 
        
        self.setup_database()
        self.setup_ui()
        self.refresh_data()

    def setup_database(self):
        self.conn = sqlite3.connect("mis_finanzas.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                tipo TEXT,
                monto REAL,
                descripcion TEXT
            )
        ''')
        self.conn.commit()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        fuente_titulo = ctk.CTkFont(size=26, weight="bold")
        fuente_inputs = ctk.CTkFont(size=14)
        fuente_boton = ctk.CTkFont(size=15, weight="bold")
        fuente_balance = ctk.CTkFont(size=42, weight="bold")
        
        # --- Panel Izquierdo (Formulario flotante) ---
        self.frame_izq = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_izq.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        self.lbl_titulo_form = ctk.CTkLabel(self.frame_izq, text="Registro", font=fuente_titulo, anchor="w")
        self.lbl_titulo_form.pack(pady=(20, 25), fill="x")

        self.tipo_var = ctk.StringVar(value="Ingreso")
        
        # Reemplazo por CTkSegmentedButton (Estilo iOS)
        self.seg_tipo = ctk.CTkSegmentedButton(
            self.frame_izq, 
            values=["Ingreso", "Gasto"], 
            variable=self.tipo_var,
            fg_color=BG_INPUT,                 # Fondo general del contenedor
            selected_color=COLOR_NARANJA,      # Color de la opción activa
            selected_hover_color=COLOR_NARANJA_HOVER,
            unselected_color=BG_INPUT,         # Color de la opción inactiva
            unselected_hover_color=BG_CARD,
            font=fuente_inputs,
            height=40,
            corner_radius=10
        )
        self.seg_tipo.pack(pady=10, fill="x")

        self.ent_monto = ctk.CTkEntry(
            self.frame_izq, 
            placeholder_text="Monto", 
            fg_color=BG_INPUT,
            border_width=0,
            font=fuente_inputs,
            height=40, 
            corner_radius=10
        )
        self.ent_monto.pack(pady=10, fill="x")

        self.ent_desc = ctk.CTkEntry(
            self.frame_izq, 
            placeholder_text="Descripción", 
            fg_color=BG_INPUT,
            border_width=0,
            font=fuente_inputs,
            height=40, 
            corner_radius=10
        )
        self.ent_desc.pack(pady=10, fill="x")

        self.btn_guardar = ctk.CTkButton(
            self.frame_izq, 
            text="Guardar", 
            command=self.guardar_registro,
            fg_color=COLOR_NARANJA,
            hover_color=COLOR_NARANJA_HOVER,
            font=fuente_boton,
            height=45, 
            corner_radius=22 
        )
        self.btn_guardar.pack(pady=(35, 20), fill="x") 

        # --- Panel Derecho (Resumen e Historial) ---
        self.frame_der = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_der.grid(row=0, column=1, padx=(10, 40), pady=40, sticky="nsew")
        self.frame_der.grid_rowconfigure(1, weight=1)
        self.frame_der.grid_columnconfigure(0, weight=1)

        self.lbl_balance = ctk.CTkLabel(self.frame_der, text="$0.00", font=fuente_balance, anchor="w")
        self.lbl_balance.grid(row=0, column=0, pady=(10, 25), sticky="w")

        self.scroll_historial = ctk.CTkScrollableFrame(
            self.frame_der, 
            fg_color="transparent",
            scrollbar_button_color=BG_CARD,
            scrollbar_button_hover_color=BG_INPUT
        )
        self.scroll_historial.grid(row=1, column=0, sticky="nsew")

    def guardar_registro(self):
        tipo = self.tipo_var.get()
        monto_str = self.ent_monto.get()
        desc = self.ent_desc.get()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

        try:
            monto = float(monto_str)
        except ValueError:
            return

        self.cursor.execute("INSERT INTO transacciones (fecha, tipo, monto, descripcion) VALUES (?, ?, ?, ?)",
                            (fecha, tipo, monto, desc))
        self.conn.commit()

        self.ent_monto.delete(0, 'end')
        self.ent_desc.delete(0, 'end')
        
        self.refresh_data()

    def refresh_data(self):
        for widget in self.scroll_historial.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT tipo, monto, descripcion, fecha FROM transacciones ORDER BY id DESC")
        registros = self.cursor.fetchall()

        balance = 0.0

        for reg in registros:
            tipo, monto, desc, fecha = reg
            
            if tipo == "Ingreso":
                balance += monto
                color_monto = COLOR_INGRESO
            else:
                balance -= monto
                color_monto = COLOR_GASTO

            row_frame = ctk.CTkFrame(self.scroll_historial, fg_color=BG_CARD, corner_radius=12)
            row_frame.pack(fill="x", pady=5, ipady=6) 
            
            info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            info_frame.pack(side="left", padx=15, fill="y", expand=True)

            lbl_desc = ctk.CTkLabel(info_frame, text=desc, font=ctk.CTkFont(size=14, weight="bold"), anchor="w")
            lbl_desc.pack(fill="x")
            
            lbl_fecha = ctk.CTkLabel(info_frame, text=fecha[:10], text_color=TEXTO_SECUNDARIO, font=ctk.CTkFont(size=12), anchor="w")
            lbl_fecha.pack(fill="x")
            
            lbl_monto = ctk.CTkLabel(row_frame, text=f"${monto:.2f}", text_color=color_monto, font=ctk.CTkFont(size=18, weight="bold"))
            lbl_monto.pack(side="right", padx=15)

        self.lbl_balance.configure(text=f"${balance:.2f}")

if __name__ == "__main__":
    app = FinanceApp()
    app.mainloop()