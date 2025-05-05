import mysql.connector
import matplotlib.pyplot as plt
from matplotlib import animation
import tkinter as tk
from tkinter import messagebox
import random

# Configuración de la conexión a la base de datos
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="bubble_sort_db"
)
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS pasos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        paso VARCHAR(20),
        estado TEXT
    )
""")
conn.commit()

def bubble_sort(arr):
    frames = []
    cursor.execute("DELETE FROM pasos")
    paso = 0
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            # Guardar estado antes de la comparación
            frames.append((arr.copy(), j, j+1))
            cursor.execute("INSERT INTO pasos (paso, estado) VALUES (%s, %s)", (str(paso), str(arr)))
            paso += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                # Guardar estado después del intercambio
                frames.append((arr.copy(), j, j+1))
                cursor.execute("INSERT INTO pasos (paso, estado) VALUES (%s, %s)", (str(paso), str(arr)))
                paso += 1
    frames.append((arr.copy(), -1, -1))  # Estado final
    cursor.execute("INSERT INTO pasos (paso, estado) VALUES (%s, %s)", ('Final', str(arr)))
    conn.commit()
    return frames

def animate_sort(arr):
    frames = bubble_sort(arr.copy())
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_rects = ax.bar(range(len(arr)), arr, color='purple', align="edge", width=0.8)
    ax.set_xlim(0, len(arr))
    ax.set_ylim(0, max(arr) + 10)
    ax.set_title('Bubble Sort Visualization', fontsize=14)
    ax.set_facecolor('#f0f0f0')
    
    text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=12)
    iteration_text = ax.text(0.02, 0.90, f"Iteración: 0/{len(frames)}", transform=ax.transAxes, fontsize=10)

    def update(frame):
        arr_state, comparing_idx1, comparing_idx2 = frame
        for idx, rect in enumerate(bar_rects):
            rect.set_height(arr_state[idx])
            if idx == comparing_idx1 or idx == comparing_idx2:
                rect.set_color('red')  # Elementos siendo comparados
            else:
                rect.set_color('purple')  # Color morado por defecto
        
        iteration = frames.index(frame) + 1
        text.set_text(f"Estado: {'Comparando' if comparing_idx1 != -1 else 'Finalizado'}")
        iteration_text.set_text(f"Iteración: {iteration}/{len(frames)}")
        return bar_rects

    # Animación más rápida (intervalo reducido a 50ms)
    ani = animation.FuncAnimation(
        fig, update, frames=frames, 
        interval=50, repeat=False, blit=True
    )
    plt.show()

def sort_data():
    input_text = entry.get()
    if not input_text:
        messagebox.showwarning("Advertencia", "Ingresa 20 números o presiona 'Random'")
        return
    try:
        numbers = list(map(int, input_text.split(',')))
        if len(numbers) != 20:
            raise ValueError
        animate_sort(numbers)
    except ValueError:
        messagebox.showerror("Error", "Debes ingresar exactamente 20 números separados por comas")

def generate_random():
    random_numbers = [random.randint(1, 50) for _ in range(20)]
    entry.delete(0, tk.END)
    entry.insert(0, ','.join(map(str, random_numbers)))

# Crear interfaz
root = tk.Tk()
root.title("Bubble Sort Visualizer con MariaDB")

tk.Label(root, text="Ingresa 20 números separados por comas:", font=('Arial', 12)).pack(pady=10)

entry = tk.Entry(root, width=60, font=('Arial', 10))
entry.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

random_btn = tk.Button(btn_frame, text="Random", command=generate_random, width=15, bg='#e1d5f7')
random_btn.pack(side=tk.LEFT, padx=10)

sort_btn = tk.Button(btn_frame, text="Sort", command=sort_data, width=15, bg='#d1c4e9')
sort_btn.pack(side=tk.RIGHT, padx=10)

root.mainloop()
cursor.close()
conn.close()