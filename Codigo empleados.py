import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

# ----------------- BASE DE DATOS -----------------
def inicializar_db():
    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            contraseña TEXT,
            rol TEXT
        )
    ''')
    if cur.execute("SELECT COUNT(*) FROM empleados").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO empleados (usuario, contraseña, rol) VALUES (?, ?, ?)",
            [("Caja", "1234", "cajero"), ("Gerente", "12345", "gerente")]
        )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS llantas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT,
            medida TEXT,
            precio REAL,
            cantidad INTEGER
        )
    ''')
    if cur.execute("SELECT COUNT(*) FROM llantas").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO llantas (marca, medida, precio, cantidad) VALUES (?, ?, ?, ?)",
            [
                ("Michelin", "205/55R16", 1500, 5),
                ("Pirelli", "195/65R15", 1350, 3),
                ("Continental", "215/60R17", 1650, 0)
            ]
        )

    cur.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            llanta_id INTEGER,
            fecha_hora TEXT
        )
    ''')

    conn.commit()
    conn.close()

# ----------------- PANTALLA INICIO -----------------
def mostrar_inicio():
    root = tk.Tk()
    root.title("SYSTEM TIRE")
    root.geometry("600x400")
    root.resizable(False, False)

    try:
        fondo_img = Image.open("fondo.png").resize((600, 400))
        fondo = ImageTk.PhotoImage(fondo_img)
        canvas = tk.Canvas(root, width=600, height=400)
        canvas.pack(fill="both", expand=True)
        canvas.create_image(0, 0, image=fondo, anchor="nw")
    except:
        canvas = tk.Canvas(root, width=600, height=400, bg="#003366")
        canvas.pack(fill="both", expand=True)

    canvas.create_text(300, 40, text="BIENVENIDO", font=("Arial Black", 18), fill="white")
    canvas.create_text(300, 80, text="SYSTEM TIRE", font=("Arial Black", 24), fill="#FFD700")
    canvas.create_text(300, 360,
        text="Tu herramienta integral para administrar inventario,\nventas y operaciones de la llantera.",
        font=("Arial", 10), fill="white", justify="center")

    def ir_login():
        root.destroy()
        mostrar_login()

    boton = tk.Button(root, text="Iniciar sesión", font=("Arial", 9),
                      bg="#28a745", fg="white", width=12, height=1, command=ir_login)
    canvas.create_window(590, 20, window=boton, anchor="ne")
    root.mainloop()

# ----------------- LOGIN -----------------
def mostrar_login():
    login = tk.Tk()
    login.title("Inicio de sesión")
    login.geometry("300x200")
    login.resizable(False, False)

    tk.Label(login, text="Usuario:").pack(pady=5)
    usuario_entry = tk.Entry(login)
    usuario_entry.pack()
    tk.Label(login, text="Contraseña:").pack(pady=5)
    contraseña_entry = tk.Entry(login, show="*")
    contraseña_entry.pack()

    def validar():
        usuario = usuario_entry.get()
        contraseña = contraseña_entry.get()
        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()
        cur.execute("SELECT rol FROM empleados WHERE usuario=? AND contraseña=?", (usuario, contraseña))
        resultado = cur.fetchone()
        conn.close()
        if resultado:
            login.destroy()
            mostrar_menu_por_rol(resultado[0])
        else:
            messagebox.showerror("Error", "Credenciales incorrectas.")

    tk.Button(login, text="Entrar", bg="#007bff", fg="white", command=validar).pack(pady=10)
    login.mainloop()
# ----------------- MENÚ POR ROL -----------------
def mostrar_menu_por_rol(rol):
    ventana = tk.Tk()
    ventana.title("Menú principal")
    ventana.geometry("300x300")

    def cerrar_sesion():
        if messagebox.askyesno("Cerrar sesión", "¿Deseas cerrar sesión?"):
            ventana.destroy()
            mostrar_login()

    if rol == "cajero":
        tk.Label(ventana, text="Bienvenido, CAJERO", font=("Arial", 14)).pack(pady=10)
        tk.Button(ventana, text="Hacer venta", command=mostrar_registro).pack(pady=5)
        tk.Button(ventana, text="Ver productos disponibles", command=mostrar_inventario).pack(pady=5)

    elif rol == "gerente":
        tk.Label(ventana, text="Bienvenido, GERENTE", font=("Arial", 14)).pack(pady=10)
        tk.Button(ventana, text="Ver ventas totales", command=ver_ventas).pack(pady=5)
        tk.Button(ventana, text="Editar precios de llantas", command=editar_precios).pack(pady=5)
        tk.Button(ventana, text="Registrar nuevo empleado", command=registrar_empleado).pack(pady=5)

    tk.Button(ventana, text="Cerrar sesión", bg="#dc3545", fg="white", command=cerrar_sesion).pack(pady=20)
    ventana.mainloop()

# ----------------- FUNCIONES CAJERO -----------------
def mostrar_registro():
    app = tk.Toplevel()
    app.title("Registrar venta")
    app.geometry("400x450")

    tk.Label(app, text="Nombre del Cliente:").pack()
    entrada_nombre = tk.Entry(app)
    entrada_nombre.pack()
    tk.Label(app, text="Teléfono:").pack()
    entrada_telefono = tk.Entry(app)
    entrada_telefono.pack()
    tk.Label(app, text="Selecciona una llanta:").pack()
    lista_llantas = tk.Listbox(app)
    lista_llantas.pack()

    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()
    cur.execute("SELECT id, marca, medida, precio, cantidad FROM llantas")
    llantas = cur.fetchall()
    conn.close()

    for l in llantas:
        estado = "AGOTADO" if l[4] <= 0 else f"{l[4]} disponibles"
        lista_llantas.insert(tk.END, f"{l[1]} {l[2]} - ${l[3]:.2f} | {estado}")

    def registrar():
        nombre = entrada_nombre.get()
        telefono = entrada_telefono.get()
        seleccion = lista_llantas.curselection()
        if not nombre or not telefono or not seleccion:
            messagebox.showerror("Error", "Completa todos los campos.")
            return

        llanta_id, marca, medida, precio, cantidad = llantas[seleccion[0]]
        if cantidad <= 0:
            messagebox.showerror("Error", "Producto agotado.")
            return

        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO clientes (nombre, telefono) VALUES (?, ?)", (nombre, telefono))
        cliente_id = cur.lastrowid
        cur.execute("INSERT INTO compras (cliente_id, llanta_id, fecha_hora) VALUES (?, ?, ?)", (cliente_id, llanta_id, fecha_hora))
        cur.execute("UPDATE llantas SET cantidad = cantidad - 1 WHERE id = ?", (llanta_id,))
        conn.commit()
        conn.close()

        recibo = f"""----- RECIBO -----
Cliente: {nombre}
Teléfono: {telefono}
Llanta: {marca} {medida}
Precio: ${precio:.2f}
Fecha y hora: {fecha_hora}
------------------"""

        with open("recibo_venta.txt", "w", encoding="utf-8") as f:
            f.write(recibo)

        messagebox.showinfo("Compra registrada", recibo)
        entrada_nombre.delete(0, tk.END)
        entrada_telefono.delete(0, tk.END)
        lista_llantas.selection_clear(0, tk.END)

    tk.Button(app, text="Registrar compra", bg="#198754", fg="white", command=registrar).pack(pady=15)

def mostrar_inventario():
    ventana = tk.Toplevel()
    ventana.title("Inventario de llantas")
    ventana.geometry("400x300")
    tk.Label(ventana, text="Llantas disponibles:", font=("Arial", 12)).pack(pady=5)
    lista = tk.Listbox(ventana, width=60)
    lista.pack()

    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()
    cur.execute("SELECT marca, medida, precio, cantidad FROM llantas")
    for marca, medida, precio, cantidad in cur.fetchall():
        estado = "AGOTADO" if cantidad <= 0 else f"{cantidad} disponibles"
        lista.insert(tk.END, f"{marca} {medida} - ${precio:.2f} | {estado}")
    conn.close()

# ----------------- FUNCIONES GERENTE -----------------
def ver_ventas():
    ventana = tk.Toplevel()
    ventana.title("Ventas Totales")
    ventana.geometry("500x350")
    tk.Label(ventana, text="Historial de ventas:", font=("Arial", 12)).pack(pady=5)

    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()
    cur.execute('''
        SELECT clientes.nombre, clientes.telefono, llantas.marca, llantas.medida, llantas.precio, compras.fecha_hora
        FROM compras
        JOIN llantas ON compras.llanta_id = llantas.id
        JOIN clientes ON compras.cliente_id = clientes.id
    ''')
    ventas = cur.fetchall()
    conn.close()

    total = 0
    for nombre, tel, marca, medida, precio, fecha in ventas:
        tk.Label(ventana, text=f"{fecha} – {nombre} ({tel}) compró {marca} {medida} - ${precio:.2f}").pack()
        total += precio

    tk.Label(ventana, text=f"\nTotal acumulado: ${total:.2f}", font=("Arial", 12, "bold")).pack(pady=10)

def editar_precios():
    ventana = tk.Toplevel()
    ventana.title("Editar precios")
    ventana.geometry("400x300")

    conn = sqlite3.connect("llantera.db")
    cur = conn.cursor()
    cur.execute("SELECT id, marca, medida, precio FROM llantas")
    productos = cur.fetchall()
    conn.close()

    lista = tk.Listbox(ventana, width=50)
    for p in productos:
        lista.insert(tk.END, f"{p[0]} - {p[1]} {p[2]} - ${p[3]:.2f}")
    lista.pack()

    entrada_precio = tk.Entry(ventana)
    entrada_precio.pack(pady=5)
    entrada_precio.insert(0, "Nuevo precio")

    def actualizar():
        sel = lista.curselection()
        if not sel:
            messagebox.showwarning("Atención", "Selecciona un producto.")
            return
        try:
            nuevo_precio = float(entrada_precio.get())
            id_llanta = productos[sel[0]][0]
            conn = sqlite3.connect("llantera.db")
            cur = conn.cursor()
            cur.execute("UPDATE llantas SET precio=? WHERE id=?", (nuevo_precio, id_llanta))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Precio actualizado.")
            ventana.destroy()
        except:
            messagebox.showerror("Error", "Precio inválido.")

    tk.Button(ventana, text="Actualizar precio", bg="#ffc107", command=actualizar).pack(pady=5)

def registrar_empleado():
    ventana = tk.Toplevel()
    ventana.title("Registrar empleado")
    ventana.geometry("300x250")

    tk.Label(ventana, text="Usuario:").pack()
    entrada_usuario = tk.Entry(ventana)
    entrada_usuario.pack()
    tk.Label(ventana, text="Contraseña:").pack()
    entrada_contra = tk.Entry(ventana)
    entrada_contra.pack()
    tk.Label(ventana, text="Rol (ej. cajero, gerente):").pack()
    entrada_rol = tk.Entry(ventana)
    entrada_rol.pack()

    def guardar():
        usuario = entrada_usuario.get()
        contra = entrada_contra.get()
        rol = entrada_rol.get()
        if not usuario or not contra or not rol:
            messagebox.showwarning("Campos incompletos", "Llena todos los datos.")
            return
        conn = sqlite3.connect("llantera.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO empleados (usuario, contraseña, rol) VALUES (?, ?, ?)", (usuario, contra, rol))
        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Empleado registrado.")
        ventana.destroy()

    tk.Button(ventana, text="Registrar", bg="#0d6efd", fg="white", command=guardar).pack(pady=10)

# ----------------- EJECUCIÓN -----------------
if __name__ == "__main__":
    inicializar_db()
    mostrar_inicio()
