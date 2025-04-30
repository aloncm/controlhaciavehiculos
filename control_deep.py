# control_acceso_app.py
import sys
import subprocess
import os

import random
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import qrcode
import cv2
from pyzbar import pyzbar

# --- Configuración inicial ---
subprocess.check_call([sys.executable, "-m", "pip", "install", "qrcode[pil]", "opencv-python", "pyzbar"])

# --- Constantes de Diseño Mejorado ---
WIDTH, HEIGHT = 1280, 720
FONT_TITLE = ('Arial', 24, 'bold')
FONT_TEXT = ('Arial', 12)
COLORS = {
    'bg1': '#e0f0ff',
    'bg2': '#c0e8ff',
    'accent1': '#0078d7',
    'accent2': '#00b4f0',
    'highlight': '#ffd800',
    'glass': '#f0f8ff',
    'text': '#1a1a1a',
    'success': '#00c800',
    'error': '#ff4444'
}
PARTICLE_COLORS = ['#00b4f0', '#0078d7', '#ffd800', '#ffffff']

# --- Base de Datos ---
DB_PATH = 'access_control.db'

cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, vehicle_type TEXT, plate TEXT UNIQUE, qr_path TEXT
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, timestamp TEXT, event TEXT
)''')


# --- Funciones Comunes ---
def generate_qr(data, save_dir='qrcodes'):
    os.makedirs(save_dir, exist_ok=True)
    path = os.path.join(save_dir, f"{data}.png")
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(path)
    return path

def register_user(name, vehicle, plate):
    qr_path = generate_qr(plate)
    try:
        cursor.execute('INSERT INTO users (name, vehicle_type, plate, qr_path) VALUES (?,?,?,?)',
                       (name, vehicle, plate, qr_path))
       
        return True, qr_path
   
        return False, None

def log_event(user_id, event):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  
                 
  

# --- Sistema de Partículas Mejorado ---
class Particle:
    def __init__(self, canvas):
        self.canvas = canvas
        self.size = random.randint(2, 6)
        self.color = random.choice(PARTICLE_COLORS)
        x = random.randint(0, WIDTH)
        y = random.randint(HEIGHT, HEIGHT + 100)
        self.id = canvas.create_oval(x, y, x+self.size, y+self.size, 
                                   fill=self.color, outline='')
        self.active = True

    def update(self):
        if not self.active:
            return False
        try:
            coords = self.canvas.coords(self.id)
            if not coords or len(coords) < 4:
                self.active = False
                return False
                
            self.canvas.move(self.id, random.uniform(-0.5, 0.5), random.uniform(-3, -1))
            
            if coords[1] < -10:
                self.canvas.delete(self.id)
                self.active = False
                return False
            return True
        except tk.TclError:
            self.active = False
            return False

# --- Componentes de UI Animados ---
class GlassButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=240, height=80):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=COLORS['bg1'], bd=0)
        self.command = command
        self.width = width
        self.height = height
        self.active = False
        
        self.bg_img = Image.new('RGBA', (width, height))
        self.draw_bg()
        self.bg_texture = ImageTk.PhotoImage(self.bg_img)
        self.create_image(0, 0, image=self.bg_texture, anchor='nw')
        self.create_text(width/2, height/2, text=text, 
                        font=FONT_TEXT, fill=COLORS['text'])
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_click)

    def draw_bg(self, alpha=0.4):
        draw = ImageDraw.Draw(self.bg_img)
        draw.rounded_rectangle((0,0,self.width,self.height), 20, 
                              fill=(255,255,255,int(255*alpha)))
        
    def on_enter(self, event):
        self.active = True
        self.animate_scale(1.1)
        self.draw_bg(0.6)
        self.bg_texture = ImageTk.PhotoImage(self.bg_img)
        self.itemconfig(1, image=self.bg_texture)
        
    def on_leave(self, event):
        self.active = False
        self.animate_scale(1.0)
        self.draw_bg(0.4)
        self.bg_texture = ImageTk.PhotoImage(self.bg_img)
        self.itemconfig(1, image=self.bg_texture)
        
    def on_click(self, event):
        if self.command:
            self.command()
            self.flash_animation()
            
    def animate_scale(self, target):
        current_scale = 1.0
        def update():
            nonlocal current_scale
            if abs(current_scale - target) < 0.05:
                return
            current_scale += (target - current_scale) * 0.2
            self.scale('all', self.width/2, self.height/2, 
                      current_scale, current_scale)
            self.after(16, update)
        update()
        
    def flash_animation(self):
        overlay = self.create_rectangle(0,0,self.width,self.height,
                                       fill=COLORS['highlight'], stipple='gray50')
        self.tag_lower(overlay)
        self.after(50, lambda: self.delete(overlay))

# --- Ventana Principal con Animaciones ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Control de Accesos - WiiU Style')
        self.geometry(f'{WIDTH}x{HEIGHT}')
        self.configure(bg=COLORS['bg1'])
        self.resizable(True, True)
        
        self.canvas = tk.Canvas(self, bg=COLORS['bg1'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.particles = []
        self.animate_background()
        
        self.current_frame = None
        self.frames = {
            'home': Home(self),
            'register': Register(self),
            'scan': Scan(self),
            'admin': Admin(self)
        }
        for frame in self.frames.values():
            frame.place(x=WIDTH, y=0, width=WIDTH, height=HEIGHT)
        self.show_frame('home')
        
    def animate_background(self):
        self.canvas.delete("all")
        for i in range(HEIGHT):
            ratio = i / HEIGHT
            r = int(224 * (1 - ratio) + 192 * ratio)
            g = int(240 * (1 - ratio) + 224 * ratio)
            b = 255
            self.canvas.create_line(0, i, WIDTH, i, fill=f'#{r:02x}{g:02x}{b:02x}')
        
        self.particles = [p for p in self.particles if p.update()]
        if random.random() < 0.3:
            self.particles.append(Particle(self.canvas))
        self.after(50, self.animate_background)
        
    def show_frame(self, name):
        if self.current_frame:
            self.current_frame.animate_out()
        self.current_frame = self.frames[name]
        self.current_frame.animate_in()

# --- Pantallas Funcionales ---
class Home(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg1'])
        self.canvas = tk.Canvas(self, bg=COLORS['bg1'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.logo_img = ImageTk.PhotoImage(Image.new('RGBA', (300, 300), (0,0,0,0)))
        self.logo = self.canvas.create_image(640, 180, image=self.logo_img)
        self.animate_logo()
        
        buttons = [
            ('Registrar', 'register', (640, 400)),
            ('Escanear', 'scan', (640, 500)),
            ('Admin', 'admin', (640, 600))
        ]
        for text, cmd, pos in buttons:
            btn = GlassButton(self.canvas, text, command=lambda c=cmd: self.master.show_frame(c))
            self.canvas.create_window(pos[0], pos[1], window=btn)
    
    def animate_in(self):
        self.place(x=WIDTH, y=0)
        self._animate(0, 20)
        
    def animate_out(self):
        self._animate(-WIDTH, 20)

    def _animate(self, target_x, delta):
        current_x = self.winfo_x()
        if (current_x < target_x and delta > 0) or (current_x > target_x and delta < 0):
            self.place(x=current_x + delta)
            self.after(10, lambda: self._animate(target_x, delta))
        else:
            self.place(x=target_x)

    def animate_logo(self):
        angle = 0
        def update():
            nonlocal angle
            img = Image.new('RGBA', (300, 300), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((0,0,300,300), outline=COLORS['accent1'], width=10)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except IOError:
                font = ImageFont.load_default()
            draw.text((150,150), "TECNM", anchor='mm', font=font, fill=COLORS['text'])
            img = img.rotate(angle, resample=Image.BILINEAR, expand=True)
            self.logo_img = ImageTk.PhotoImage(img)
            self.canvas.itemconfig(self.logo, image=self.logo_img)
            angle = (angle + 2) % 360
            self.after(50, update)
        update()

class Register(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg1'])
        self.canvas = tk.Canvas(self, bg=COLORS['bg1'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.canvas.create_text(640, 100, text="Registro de Vehículo", 
                              font=FONT_TITLE, fill=COLORS['text'])
        
        self.entries = {}
        labels = ['Nombre', 'Tipo de Vehículo', 'Placa']
        for i, label in enumerate(labels):
            y = 200 + i*100
            self.canvas.create_text(400, y, text=label+":", 
                                  font=FONT_TEXT, fill=COLORS['text'])
            entry = tk.Entry(self.canvas, font=FONT_TEXT,
                        bg=COLORS['glass'], relief='flat')
            if label == 'Tipo de Vehículo':
                entry = ttk.Combobox(self.canvas, values=['Carro', 'Moto'],
                            font=FONT_TEXT, background=COLORS['glass'])
            self.entries[label] = entry
            self.canvas.create_window(800, y, window=entry, width=300)
            
        btn_submit = GlassButton(self.canvas, "Registrar", self.submit)
        self.canvas.create_window(640, 550, window=btn_submit)
        
    def submit(self):
        name = self.entries['Nombre'].get().strip()
        vehicle = self.entries['Tipo de Vehículo'].get().strip()
        plate = self.entries['Placa'].get().strip()
        
        if all([name, vehicle, plate]):
            success, qr_path = register_user(name, vehicle, plate)
            if success:
                tk.messagebox.showinfo("Éxito", f"Usuario {name} registrado exitosamente")
                self.master.show_frame('home')
            else:
                tk.messagebox.showerror("Error", "La placa ya está registrada")
        else:
            tk.messagebox.showwarning("Advertencia", "Todos los campos son obligatorios")
    
    def animate_in(self):
        self.place(x=WIDTH, y=0)
        self._animate(0, 20)
        
    def animate_out(self):
        self._animate(-WIDTH, 20)

    def _animate(self, target_x, delta):
        current_x = self.winfo_x()
        if (current_x < target_x and delta > 0) or (current_x > target_x and delta < 0):
            self.place(x=current_x + delta)
            self.after(10, lambda: self._animate(target_x, delta))
        else:
            self.place(x=target_x)

class Scan(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg1'])
        self.canvas = tk.Canvas(self, bg=COLORS['bg1'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        self.video_label = tk.Label(self.canvas, bg=COLORS['bg1'])
        self.canvas.create_window(640, 360, window=self.video_label, 
                                 width=640, height=480)
        
        btn_back = GlassButton(self.canvas, "Volver", 
                              lambda: self.master.show_frame('home'))
        self.canvas.create_window(120, 50, window=btn_back)
        
        self.cap = None
        self.running = False
        self.last_detect = 0
        self.cooldown = 5

    def on_show(self):
        if not self.running:
            self.running = True
            self.cap = cv2.VideoCapture(0)
            self._update()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def _update(self):
        if self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img).resize((640, 480))
                ph = ImageTk.PhotoImage(img)
                self.video_label.config(image=ph)
                self.video_label.image = ph
                
                now = time.time()
                for barcode in pyzbar.decode(frame):
                    if now - self.last_detect < self.cooldown:
                        break
                    code = barcode.data.decode('utf-8')
                    cursor.execute('SELECT id, name FROM users WHERE plate=?', (code,))
                    user = cursor.fetchone()
                    if user:
                        user_id, name = user
                      
                        last_event = cursor.fetchone()
                        event = 'entrada' if not last_event or last_event[0] == 'salida' else 'salida'
                        log_event(user_id, event)
                        self.show_notification(f"{name} ha realizado {event}")
                        self.last_detect = now
            self.after(100, self._update)

    def show_notification(self, message):
        notification = tk.Label(self.canvas, text=message, font=FONT_TEXT, 
                               bg=COLORS['success'], fg='white')
        self.canvas.create_window(640, 50, window=notification)
        self.after(3000, notification.destroy)

    def animate_in(self):
        self.place(x=WIDTH, y=0)
        self._animate(0, 20)
        self.on_show()
        
    def animate_out(self):
        self._animate(-WIDTH, 20)
        self.stop()

class Admin(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['bg1'])
        self.canvas = tk.Canvas(self, bg=COLORS['bg1'], highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=FONT_TEXT)
        style.configure("Treeview", rowheight=25)
        
        self.tree_users = ttk.Treeview(self.canvas, columns=('ID', 'Nombre', 'Vehículo', 'Placa'))
        self.canvas.create_window(640, 300, window=self.tree_users, 
                                 width=1000, height=400)
        
        btn_back = GlassButton(self.canvas, "Volver", 
                              lambda: self.master.show_frame('home'))
        self.canvas.create_window(120, 50, window=btn_back)
        
        self.load_data()

    def load_data(self):
        for i in self.tree_users.get_children():
            self.tree_users.delete(i)
        for row in cursor.execute('SELECT id, name, vehicle_type, plate FROM users'):
            self.tree_users.insert('', 'end', values=row)

    def animate_in(self):
        self.place(x=WIDTH, y=0)
        self._animate(0, 20)
        self.load_data()
        
    def animate_out(self):
        self._animate(-WIDTH, 20)

if __name__ == '__main__':
    app = App()
    app.mainloop()