# control_acceso_app.py
# App de control de accesos para autos y motos, con registro, escaneo y administración.
# Diseño estilo móvil (360×640), navegación Home/Register/Scan/Admin.
from supabase import create_client, Client
import os

# Configuración Supabase
SUPABASE_URL = "https://cwcadrsyuhurwavinsgh.supabase.co"  # Ej: "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImN3Y2FkcnN5dWh1cndhdmluc2doIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5Nzg4MDYsImV4cCI6MjA2MTU1NDgwNn0.ORS872DKQV24jR_VsORfoXc8tmD44l-I6Uwl008Ik5U"  # Ej: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
import sys
import subprocess
import os

import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox

from PIL import Image, ImageTk, ImageDraw, ImageFont
import smtplib
from email.message import EmailMessage
import tkinter as tk
import sys
import qrcode
import socket

import socket


def get_remote_config(feature):
    """Consulta Supabase para saber si una función está habilitada para este dispositivo."""
    device_id = socket.gethostname()
    try:
        res = supabase.table('remote_config').select('enabled').eq('device_id', device_id).eq('feature', feature).limit(1).execute()
        if res.data and 'enabled' in res.data[0]:
            return bool(res.data[0]['enabled'])
        # Si no hay configuración, por defecto habilitado
        return True
    except Exception as e:
        print(f"Error consultando remote_config: {e}")
        # Si hay error, por seguridad deshabilita la función
        return False
    
def mostrar_aviso_privacidad():
    aviso = aviso = (
    "Nombre de la aplicación: Control de Accesos\n"
    "Responsable del tratamiento: FUENTES ESTEVES MAGALI \n"
    "Correo de contacto: controldeaccesoas@gmail.com\n\n"

    "1. Finalidad del tratamiento de datos\n"
    "Los datos personales que se recaban a través de esta aplicación (nombre, tipo de vehículo, placas, correo electrónico y datos de acceso) serán utilizados exclusivamente para las siguientes finalidades:\n"
    "- Verificar la identidad de los usuarios y controlar el acceso vehicular autorizado.\n"
    "- Registrar y consultar accesos mediante escaneo de códigos QR.\n"
    "- Enviar notificaciones relacionadas con el acceso y la seguridad.\n"
    "- Generar reportes de uso para propósitos administrativos internos.\n\n"

    "2. Datos personales recabados\n"
    "- Nombre del propietario\n"
    "- Tipo de vehículo (auto o motocicleta)\n"
    "- Placas del vehículo\n"
    "- Correo electrónico\n"
    "- Fecha y hora de accesos registrados\n\n"

    "3. Transferencia de datos\n"
    "Los datos no serán compartidos con terceros, salvo que exista obligación legal, orden judicial o autorización expresa del titular.\n\n"

    "4. Derechos ARCO\n"
    "El titular de los datos puede en todo momento ejercer sus derechos de Acceso, Rectificación, Cancelación u Oposición al tratamiento de sus datos personales, enviando una solicitud al correo electrónico indicado.\n"
    "La solicitud deberá contener:\n"
    "- Nombre del titular\n"
    "- Descripción clara de los datos respecto de los que se solicita ejercer algún derecho\n"
    "- Medio para comunicar la respuesta (correo electrónico)\n\n"

    "5. Medidas de seguridad\n"
    "La aplicación implementa protocolos de seguridad como cifrado de datos en tránsito (HTTPS), autenticación y restricción de acceso para proteger la información.\n"
    "Los datos están almacenados de forma segura en la plataforma Supabase, la cual cumple con estándares internacionales de seguridad.\n\n"

    "6. Cambios al aviso de privacidad\n"
    "Nos reservamos el derecho de modificar este Aviso de Privacidad. Cualquier cambio será notificado a través de la aplicación."
)
    def abrir_aviso_completo():
        ventana_aviso = tk.Toplevel(root)
        ventana_aviso.title("Aviso de Privacidad Completo")
        ventana_aviso.geometry("400x300")
        texto = tk.Text(ventana_aviso, wrap="word")
        texto.insert("1.0", aviso)
        texto.config(state="disabled")
        texto.pack(expand=True, fill="both", padx=10, pady=10)
        tk.Button(ventana_aviso, text="Cerrar", command=ventana_aviso.destroy).pack(pady=10)

    def aceptar():
        root.destroy()  # Cierra la ventana del aviso y continúa con la app

    def cancelar():
        root.destroy()
        sys.exit()      # Cierra toda la app

    root = tk.Tk()
    root.title("Aviso de Privacidad")
    root.geometry("350x200")
    label = tk.Label(root, text="¿Acepta el aviso de privacidad para continuar?", wraplength=320, justify="left")
    label.pack(pady=15)
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Cancelar", width=10, command=cancelar).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Ver aviso completo", width=18, command=abrir_aviso_completo).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Aceptar", width=10, command=aceptar).pack(side="left", padx=5)

    # Si el usuario cierra la ventana con el tache, también se cierra la app
    root.protocol("WM_DELETE_WINDOW", cancelar)

    root.mainloop()

mostrar_aviso_privacidad()

# --- Instalación automática de paquetes ---
REQUIREMENTS = [
    ("qrcode[pil]", "qrcode"),
    ("opencv-python", "cv2"),
    ("pyzbar", "pyzbar")
]
for pkg, module in REQUIREMENTS:
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import qrcode
import cv2
from pyzbar import pyzbar

# --- Base de Datos ---
DB_PATH = 'access_control.db'



# --- Funciones Auxiliares ---
def generate_qr(plate, save_dir='qrcodes'):
    os.makedirs(save_dir, exist_ok=True)
    qr_data = plate.upper()  # Solo la placa en mayúsculas
    path = os.path.join(save_dir, f"{qr_data}.png")
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    img.save(path)
    return path

def register_user(name, vehicle, plate):
    if not name or not vehicle or not plate:
        return False, None

    qr_path = generate_qr(plate)

    try:
        response = supabase.table('users').insert({
            "name": name,
            "vehicle_type": vehicle,
            "plate": plate.upper(),  # Guarda la placa en mayúsculas en la base
            "qr_path": qr_path
        }).execute()

        if response.data:
            return True, qr_path
        return False, None
    except Exception as e:
        print(f"Error al registrar: {e}")
        return False, None

def log_event(user_id, event):
    try:
        supabase.table('access_log').insert({
            "user_id": user_id,
            "event": event
        }).execute()
    except Exception as e:
        print(f"Error en log: {e}")

# --- UI Configuración ---
WIDTH, HEIGHT = 360, 640
PRIMARY = '#6A1B9A'   # Morado principal
SECONDARY = '#8E24AA' # Morado secundario
ACC = '#1ECA3C'
DENY = '#E53935'
BG = '#F3E5F5'        # Fondo lila claro
GRAY = '#B39DDB'
FONT = 'Arial'
def style_button(btn, color=PRIMARY, fg='white'):
    btn.config(
        bg=color, fg=fg, activebackground=SECONDARY, activeforeground='white',
        relief='flat', font=(FONT, 12, 'bold'), bd=0, cursor='hand2', padx=8, pady=4
    )

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Control Accesos')
        self.geometry(f'{WIDTH}x{HEIGHT}')
        self.configure(bg=BG)
        self.resizable(False, False)

     

        # App Bar
        bar = tk.Frame(self, bg=PRIMARY, height=50)
        bar.pack(fill='x')
        tk.Label(bar, text='Control Accesos', bg=PRIMARY, fg='white', font=(FONT,16,'bold')).pack(pady=10)
        # Container
        self.container = tk.Frame(self, bg=BG)
        self.container.pack(fill='both', expand=True)
        # Frames
        self.frames = {}
        for F in (Home, Register, Scan, Admin, UsersList):
            frm = F(self.container, self)
            frm.grid(row=0, column=0, sticky='nsew')
            self.frames[F] = frm
        self.show(Home)

    def show(self, frame_class):
        # Detener cámara si dejamos pantalla Scan
        scan_frame = self.frames.get(Scan)
        if scan_frame and getattr(scan_frame, 'running', False):
            scan_frame.stop()
        # Mostrar nueva
        frame = self.frames[frame_class]
        frame.tkraise()
        if hasattr(frame, 'on_show'): frame.on_show()



# === CLASE PRINCIPAL HOME ===
class Home(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        logo = 'tecnm_logo.png'

        if os.path.exists(logo):
            img = Image.open(logo).resize((120,120), Image.LANCZOS)
        else:
            img = Image.new('RGB', (120,120), BG)
            d = ImageDraw.Draw(img)
            f = ImageFont.load_default()
            text = 'TECNM'
            bbox = d.textbbox((0, 0), text, font=f)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            d.text(((120-w)/2, (120-h)/2), text, fill=PRIMARY, font=f)

        ph = ImageTk.PhotoImage(img)
        tk.Label(self, image=ph, bg=BG).pack(pady=20)
        self.logo = ph

        # Título grande
        tk.Label(self, text="Bienvenido", bg=BG, fg=PRIMARY, font=(FONT, 20, 'bold')).pack(pady=(0, 10))

        for text, cls in [('Registrar', Register), ('Escanear', Scan), ('Admin', Admin)]:
            btn = tk.Button(
                self, text=text, width=18,
                command=lambda c=cls: controller.show(c)
            )
            style_button(btn)
            btn.pack(pady=12)
       



class Register(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        tk.Label(self, text='Registro de Vehículo', bg=BG, fg=PRIMARY, font=(FONT,14)).pack(pady=10)
        frm = tk.Frame(self, bg=BG); frm.pack(pady=5, padx=20, fill='x')
        self.e_name = self._mk(frm, 'Nombre completo:', 0)
        self.vtype = ttk.Combobox(frm, values=['Carro','Moto'], state='readonly')
        self._place(frm, 'Tipo de vehículo:', 2, self.vtype)
        self.e_plate = self._mk(frm, 'Placa:', 4)
        self.note = tk.Label(self, text='', bg=BG, font=(FONT,12)); self.note.pack(pady=5)

        # Label para QR
        self.qr_label = tk.Label(self, bg=BG)
        self.qr_label.pack(pady=10)

        # Botones principales (Registrar, Guardar QR, Enviar Email)
        self.btn_frame_main = tk.Frame(self, bg=BG)
        self.btn_frame_main.pack(pady=5)
        self.btn_register = tk.Button(self.btn_frame_main, text='Registrar', bg=PRIMARY, fg='white',
                                      width=12, relief='raised', command=self.do_register)
        self.btn_register.pack(side='left', padx=5)
        self.btn_save = tk.Button(self.btn_frame_main, text='Guardar QR', bg=PRIMARY, fg='white',
                                  width=12, relief='raised', state='disabled', command=self.save_qr)
        self.btn_save.pack(side='left', padx=5)
        self.btn_email = tk.Button(self.btn_frame_main, text='Enviar Email', bg=PRIMARY, fg='white',
                                   width=12, relief='raised', state='disabled', command=self.email_qr)
        self.btn_email.pack(side='left', padx=5)
        

        # Navegación abajo (Home, Admin)
        nav_frame = tk.Frame(self, bg=BG)
        nav_frame.pack(side='bottom', pady=10)
        tk.Button(nav_frame, text='Home', bg='gray', fg='white', width=12,
                  relief='raised', command=lambda: controller.show(Home)).pack(side='left', padx=5)
        tk.Button(nav_frame, text='Admin', bg='gray', fg='white', width=12,
                  relief='raised', command=lambda: controller.show(Admin)).pack(side='left', padx=5)

        self.current_qr = None

    def _mk(self, parent, label, row):
        tk.Label(parent, text=label, bg=BG).grid(row=row, column=0, sticky='e', padx=5, pady=5)
        e = tk.Entry(parent, bd=1, relief='solid'); e.grid(row=row, column=1, pady=5, sticky='we')
        parent.grid_columnconfigure(1, weight=1)
        return e

    def _place(self, parent, label, row, widget):
        tk.Label(parent, text=label, bg=BG).grid(row=row, column=0, sticky='e', padx=5, pady=5)
        widget.grid(row=row, column=1, pady=5, sticky='we'); parent.grid_columnconfigure(1, weight=1)

    def do_register(self):
        name = self.e_name.get().strip()
        vt = self.vtype.get()
        plate = self.e_plate.get().strip()
        ok, qr_path = register_user(name, vt, plate)
        if ok:
            self.note.config(text=f'✔ {name} registrado', fg=ACC)
            # mostrar QR
            img = Image.open(qr_path).resize((120,120), Image.LANCZOS)
            ph = ImageTk.PhotoImage(img)
            self.qr_label.config(image=ph); self.qr_label.image = ph
            self.current_qr = qr_path
            # habilitar botones
            self.btn_save.config(state='normal')
            self.btn_email.config(state='normal')
        else:
            self.note.config(text='✖ Error: Placa ya existe o datos incompletos', fg=DENY)

    def save_qr(self):
        if not self.current_qr: return
        dest = filedialog.asksaveasfilename(defaultextension='.png',
                                            filetypes=[('PNG Image','*.png')])
        if dest:
            Image.open(self.current_qr).save(dest)
            messagebox.showinfo('Guardado', f'QR guardado en:\n{dest}')

    def email_qr(self):
        if not get_remote_config('email'):
            messagebox.showerror('Error', 'La función de enviar email está desactivada remotamente.')
            return
        if not self.current_qr:
            return
        to_addr = simpledialog.askstring('Enviar Email', 'Dirección de correo destino:')
        if not to_addr:
            return
        try:
            # Configura tus credenciales SMTP aquí
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
            smtp_user = 'memosonic1@gmail.com'
            smtp_pass = 'wzhs xxps cadt nwom'

            msg = EmailMessage()
            msg['Subject'] = 'Tu Código QR de Acceso'
            msg['From'] = smtp_user
            msg['To'] = to_addr
            msg.set_content('Adjunto encontrarás tu código QR de acceso.'
                            ' Este es el aviso de privacidad:\n\n'
                            "Nombre de la aplicación: Control de Accesos\n"
                            "Responsable del tratamiento: FUENTES ESTEVES MAGALI\n"
                            "Correo de contacto: controldeaccesoas@gmail.com\n\n"
                            "1. Finalidad del tratamiento de datos\n"
                            "Los datos personales que se recaban a través de esta aplicación (nombre, tipo de vehículo, placas, correo electrónico y datos de acceso) serán utilizados exclusivamente para las siguientes finalidades:\n"
                            "- Verificar la identidad de los usuarios y controlar el acceso vehicular autorizado.\n"
                            "- Registrar y consultar accesos mediante escaneo de códigos QR.\n"
                            "- Enviar notificaciones relacionadas con el acceso y la seguridad.\n"
                            "- Generar reportes de uso para propósitos administrativos internos.\n\n"
                            "2. Datos personales recabados\n"
                            "- Nombre del propietario\n"
                            "- Tipo de vehículo (auto o motocicleta)\n"
                            "- Placas del vehículo\n"
                            "- Correo electrónico\n"
                            "- Fecha y hora de accesos registrados\n\n"
                            "3. Transferencia de datos\n"
                            "Los datos no serán compartidos con terceros, salvo que exista obligación legal, orden judicial o autorización expresa del titular.\n\n"
                            "4. Derechos ARCO\n"
                            "El titular de los datos puede en todo momento ejercer sus derechos de Acceso, Rectificación, Cancelación u Oposición al tratamiento de sus datos personales, enviando una solicitud al correo electrónico indicado.\n"
                            "La solicitud deberá contener:\n"
                            "- Nombre del titular\n"
                            "- Descripción clara de los datos respecto de los que se solicita ejercer algún derecho\n"
                            "- Medio para comunicar la respuesta (correo electrónico)\n\n"
                            "5. Medidas de seguridad\n"
                            "La aplicación implementa protocolos de seguridad como cifrado de datos en tránsito (HTTPS), autenticación y restricción de acceso para proteger la información.\n"
                            "Los datos están almacenados de forma segura en la plataforma Supabase, la cual cumple con estándares internacionales de seguridad.\n\n"
                            "6. Cambios al aviso de privacidad\n"
                            "Nos reservamos el derecho de modificar este Aviso de Privacidad. Cualquier cambio será notificado a través de la aplicación."
            )

            with open(self.current_qr, 'rb') as f:
                data = f.read()
            msg.add_attachment(data, maintype='image', subtype='png', filename=os.path.basename(self.current_qr))

            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()
                smtp.login(smtp_user, smtp_pass)
                smtp.send_message(msg)
            messagebox.showinfo('Email enviado', f'QR enviado a {to_addr}')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo enviar email:\n{e}')
            
    def on_show(self):
        # Consulta el flag remoto cada vez que se muestra la pantalla
        email_enabled = get_remote_config('email')
        state = 'normal' if email_enabled else 'disabled'
        self.btn_email.config(state=state)
        # Opcional: muestra un aviso si está deshabilitado
        if not email_enabled:
            self.note.config(text='Función de email desactivada remotamente', fg=DENY)
        else:
            self.note.config(text='', fg=ACC)


class Scan(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        
        # Widgets de la interfaz
        tk.Label(self, text='Escaneo QR', bg=BG, fg=PRIMARY, font=(FONT,14)).pack(pady=10)
        self.video = tk.Label(self, bg=BG)
        self.video.pack(pady=5)
        
        # Frame de información
        self.info_frame = tk.Frame(self, bg=BG)
        self.info_frame.pack(pady=5)
        
        # Labels para mostrar datos
        self.icon_label = tk.Label(self.info_frame, bg=BG)
        self.icon_label.grid(row=0, column=0, rowspan=3, padx=5)
        
        self.lbl_name = tk.Label(self.info_frame, text='Nombre:', bg=BG, font=(FONT,12,'bold'))
        self.lbl_name.grid(row=0, column=1, sticky='w')
        
        self.lbl_vehicle = tk.Label(self.info_frame, text='Vehículo:', bg=BG, font=(FONT,12,'bold'))
        self.lbl_vehicle.grid(row=1, column=1, sticky='w')
        
        self.lbl_plate = tk.Label(self.info_frame, text='Placa:', bg=BG, font=(FONT,12,'bold'))
        self.lbl_plate.grid(row=2, column=1, sticky='w')

        # Botones de navegación
        btns = tk.Frame(self, bg=BG)
        btns.pack(pady=10)
        tk.Button(btns, text='Home', bg='gray', fg='white', width=10,
                command=lambda: controller.show(Home)).pack(side='left', padx=5)
        tk.Button(btns, text='Admin', bg='gray', fg='white', width=10,
                command=lambda: controller.show(Admin)).pack(side='left', padx=5)

        # Configuración de cámara y detección
        self.cap = None
        self.running = False
        self.last_detect = 0
        self.cooldown = 5

        # Carga de íconos con manejo de errores
        self.icons = {}
        
        # Ícono para Carro
        try:
            car_img = Image.open('car.png').resize((48, 48), Image.LANCZOS)
            self.icons['Carro'] = ImageTk.PhotoImage(car_img)
        except Exception as e:
            img = Image.new('RGB', (48, 48), BG)
            d = ImageDraw.Draw(img)
            d.text((10, 10), "🚗", fill="black", font=ImageFont.load_default())  # Emoji alternativo
            self.icons['Carro'] = ImageTk.PhotoImage(img)

        # Ícono para Moto
        try:
            moto_img = Image.open('moto.png').resize((48, 48), Image.LANCZOS)
            self.icons['Moto'] = ImageTk.PhotoImage(moto_img)
        except Exception as e:
            img = Image.new('RGB', (48, 48), BG)
            d = ImageDraw.Draw(img)
            d.text((10, 10), "🏍️", fill="black", font=ImageFont.load_default())  # Emoji alternativo
            self.icons['Moto'] = ImageTk.PhotoImage(img)

    def on_show(self):
        if not self.running:
            self.running = True
            try:
                self.cap = cv2.VideoCapture(0)
            except Exception as e:
                messagebox.showerror('Error cámara', f"No se pudo acceder a la cámara: {str(e)}")
                return
            self._update()

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None

    def _update(self):
        if not self.running:
          return
            
        ret, frame = self.cap.read()
        if ret:
        # Procesamiento del frame
         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img).resize((340, 200))
        ph = ImageTk.PhotoImage(img)
        
        # Actualizar video
        self.video.config(image=ph)
        self.video.image = ph
        
        # Detección de QR
        now = time.time()
        for barcode in pyzbar.decode(gray):
            if now - self.last_detect < self.cooldown:
                break
            
            code = barcode.data.decode()
            
            # Consulta a Supabase (reemplaza esto con tu consulta real)
            user_data = supabase.table("users").select("*").eq("plate", code).execute()
            
            if user_data.data:
                user = user_data.data[0]
                user_id = user['id']
                name = user['name']
                vehicle_type = user['vehicle_type']
                plate = user['plate']
                
                # Determinar tipo de evento
                last_event = supabase.table("access_log")\
                    .select("event")\
                    .eq("user_id", user_id)\
                    .order("id", desc=True)\
                    .limit(1)\
                    .execute()
                
                event = 'entrada' if not last_event.data or last_event.data[0]['event'] == 'salida' else 'salida'
                
                # Registrar evento
                log_event(user_id, event)
                
                # Actualizar interfaz
                self.icon_label.config(image=self.icons.get(vehicle_type))
                self.lbl_name.config(text=f'Nombre: {name}', fg=ACC if event == 'entrada' else DENY)
                self.lbl_vehicle.config(text=f'Vehículo: {vehicle_type}')
                self.lbl_plate.config(text=f'Placa: {plate}')
                self.last_detect = now

        self.after(100, self._update)

class Admin(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        tk.Label(self, text='Administración - Accesos', bg=BG, fg=PRIMARY, font=(FONT,14)).pack(pady=10)
        cols2=('ID','Usuario','Fecha','Evento')
        self.log=ttk.Treeview(self,columns=cols2,show='headings',height=8)
        for col in cols2:
            self.log.heading(col,text=col); self.log.column(col,width=int((WIDTH-20)/4),anchor='center')
        self.log.pack(fill='x',padx=10,pady=5)
        nav=tk.Frame(self,bg=BG); nav.pack(pady=10)
        tk.Button(nav,text='Home',bg='gray',fg='white',width=10,command=lambda:controller.show(Home)).pack(side='left',padx=5)
        tk.Button(nav,text='Escanear',bg='gray',fg='white',width=10,command=lambda:controller.show(Scan)).pack(side='left',padx=5)
        tk.Button(nav,text='Ver Usuarios',bg=PRIMARY,fg='white',width=12,command=lambda:controller.show(UsersList)).pack(side='left',padx=5)

    def on_show(self):
        for i in self.log.get_children(): self.log.delete(i)
        for r in cursor.execute('''SELECT l.id,u.name,l.timestamp,l.event 
                                   FROM access_log l JOIN users u ON u.id=l.user_id 
                                   ORDER BY l.id DESC'''):
            self.log.insert('',tk.END,values=r)
    def on_show(self):
        for i in self.log.get_children(): 
            self.log.delete(i)
        
        data = supabase.table('access_log').select(
            "id, users(name), timestamp, event"
        ).execute()
        
        for row in data.data:
            self.log.insert('', tk.END, values=(
                row['id'],
                row['users']['name'],
                row['timestamp'],
                row['event']
            ))

class UsersList(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        tk.Label(self, text='Usuarios Registrados', bg=BG, fg=PRIMARY, font=(FONT,14)).pack(pady=10)

        # Tabla de usuarios
        cols = ('ID','Nombre','Vehículo','Placa')
        self.tbl = ttk.Treeview(self, columns=cols, show='headings', height=8)
        for col in cols:
            self.tbl.heading(col, text=col)
            self.tbl.column(col, width=int((WIDTH-20)/4), anchor='center')
        self.tbl.pack(fill='x', padx=10, pady=5)

        # Botones Eliminar / Volver
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text='Eliminar', bg=DENY, fg='white', width=12, command=self.delete_user).pack(side='left', padx=5)
        tk.Button(btn_frame, text='Volver', bg=GRAY, fg='white', width=12, command=lambda: controller.show(Admin)).pack(side='left', padx=5)

    def on_show(self):
        # Recarga la tabla desde Supabase
        for i in self.tbl.get_children():
            self.tbl.delete(i)
        data = supabase.table('users').select("*").execute()
        for row in data.data:
            self.tbl.insert('', tk.END, values=(
                row['id'],
                row['name'],
                row['vehicle_type'],
                row['plate']
            ))

    def delete_user(self):
        sel = self.tbl.selection()
        if not sel:
            messagebox.showwarning('Seleccionar', 'Por favor selecciona un usuario para eliminar.')
            return

        uid = self.tbl.item(sel)['values'][0]
        if not messagebox.askyesno('Confirmar eliminación', f'¿Eliminar usuario ID={uid} y todos sus registros?'):
            return

        # Borra primero los logs de acceso de ese usuario
        supabase.table('access_log').delete().eq('user_id', uid).execute()
        # Luego borra el usuario
        supabase.table('users').delete().eq('id', uid).execute()

        # Refresca la tabla
        self.on_show()


if __name__=='__main__':
    App().mainloop()