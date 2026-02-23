import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import hashlib
import os
import base64
from pathlib import Path
import threading

# Try imports for crypto libraries; if not available, we'll disable related features.
try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except Exception:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP
    PYCRYPTODOME_AVAILABLE = True
except Exception:
    PYCRYPTODOME_AVAILABLE = False

# ---------------------------
# App-wide config
# ---------------------------
APP_NAME = "Shoaib Crypto-Toolkit"
CONFIG_DIR = Path.home() / ".encryption_toolkit"
PRIVATE_PEM = CONFIG_DIR / "private.pem"
PUBLIC_PEM = CONFIG_DIR / "public.pem"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# default theme variables (light modern)
THEMES = {
    'Light Modern': {
        'root_bg': '#f6f8fa',
        'sidebar_bg': '#ffffff',
        'content_bg': '#f2f6f9',
        'accent': '#286ef0',
        'btn_bg': '#286ef0',
        'btn_hover': '#1f56d6',
        'text_bg': '#ffffff',
        'text_fg': '#0b1220',
        'muted_fg': '#546579'
    },
    'Dark': {
        'root_bg': '#121212',
        'sidebar_bg': '#0f1720',
        'content_bg': '#071013',
        'accent': '#00ADB5',
        'btn_bg': '#00ADB5',
        'btn_hover': '#02979a',
        'text_bg': '#0b1718',
        'text_fg': '#e6f7f7',
        'muted_fg': '#dfe6e9'
    },
    'Blue': {
        'root_bg': '#eaf3ff',
        'sidebar_bg': '#cfe1ff',
        'content_bg': '#ffffff',
        'accent': '#0b61d9',
        'btn_bg': '#0b61d9',
        'btn_hover': '#094fb8',
        'text_bg': '#ffffff',
        'text_fg': '#0b1220',
        'muted_fg': '#4b6b9b'
    }
}
CURRENT_THEME = 'Light Modern'

# ---------------------------
# Helper utility functions
# ---------------------------

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  # now it stays on clipboard
    messagebox.showinfo("Copied", "Result copied to clipboard.")


def flash_widget(widget, start_bg, flash_bg="#ffeaa7", times=2, interval=120):
    # simple flash animation for result boxes
    def _flash(count):
        if count <= 0:
            try:
                widget.config(bg=start_bg)
            except Exception:
                pass
            return
        try:
            widget.config(bg=flash_bg if (count % 2 == 0) else start_bg)
        except Exception:
            pass
        widget.after(interval, _flash, count - 1)

    _flash(times * 2)


def set_result(text_widget, text):
    # set content and flash the box
    text_widget.config(state="normal")
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, text)
    text_widget.config(state="disabled")
    flash_widget(text_widget, start_bg=text_widget.cget("bg"))


# ---------------------------
# Small UI helpers / animations
# ---------------------------

def make_fancy_button(btn, normal_bg, hover_bg, active_bg=None):
    # add hover behavior
    def on_enter(e):
        try:
            btn.config(bg=hover_bg)
        except Exception:
            pass
    def on_leave(e):
        try:
            btn.config(bg=normal_bg)
        except Exception:
            pass
    btn.config(bg=normal_bg, activebackground=active_bg if active_bg else hover_bg, fg="#ffffff", bd=0)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)


def animate_indicator_to(y_target, steps=10, delay=12):
    # moves indicator_frame to y_target using small steps
    current = indicator_frame.winfo_y()
    dy = (y_target - current) / max(1, steps)
    def _step(i, cur):
        if i <= 0:
            indicator_frame.place(y=y_target)
            return
        indicator_frame.place(y=int(cur + dy))
        indicator_frame.after(delay, _step, i - 1, cur + dy)
    _step(steps, current)


# ---------------------------
# Caesar Cipher
# ---------------------------

def caesar_encrypt(text, shift):
    result = ""
    for ch in text:
        if ch.isalpha():
            base = ord('A') if ch.isupper() else ord('a')
            result += chr((ord(ch) - base + shift) % 26 + base)
        else:
            result += ch
    return result


def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)


def caesar_encrypt_action():
    t = caesar_text.get("1.0", tk.END).rstrip("\n")
    try:
        s = int(caesar_shift_var.get()) % 26
    except ValueError:
        messagebox.showerror("Input error", "Shift must be an integer.")
        return
    out = caesar_encrypt(t, s)
    set_result(caesar_result, out)


def caesar_decrypt_action():
    t = caesar_text.get("1.0", tk.END).rstrip("\n")
    try:
        s = int(caesar_shift_var.get()) % 26
    except ValueError:
        messagebox.showerror("Input error", "Shift must be an integer.")
        return
    out = caesar_decrypt(t, s)
    set_result(caesar_result, out)


# ---------------------------
# Vigenere
# ---------------------------

def vigenere_encrypt(plain_text, key):
    result = ""
    key = key.upper()
    j = 0
    for char in plain_text:
        if char.isalpha():
            shift = ord(key[j % len(key)]) - ord('A')
            start = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - start + shift) % 26 + start)
            j += 1
        else:
            result += char
    return result


def vigenere_decrypt(cipher_text, key):
    result = ""
    key = key.upper()
    j = 0
    for char in cipher_text:
        if char.isalpha():
            shift = ord(key[j % len(key)]) - ord('A')
            start = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - start - shift) % 26 + start)
            j += 1
        else:
            result += char
    return result


def vigenere_encrypt_action():
    t = vigenere_text.get("1.0", tk.END).rstrip("\n")
    k = vigenere_key_var.get().strip()
    if not t or not k:
        messagebox.showwarning("Input error", "Enter text and key.")
        return
    out = vigenere_encrypt(t, k)
    set_result(vigenere_result, out)


def vigenere_decrypt_action():
    t = vigenere_text.get("1.0", tk.END).rstrip("\n")
    k = vigenere_key_var.get().strip()
    if not t or not k:
        messagebox.showwarning("Input error", "Enter text and key.")
        return
    out = vigenere_decrypt(t, k)
    set_result(vigenere_result, out)


# ---------------------------
# AES / DES
# ---------------------------

def aes_encrypt_action():
    if not CRYPTOGRAPHY_AVAILABLE:
        messagebox.showerror("Missing library", "cryptography package is required for AES/DES.")
        return
    t = sym_text.get("1.0", tk.END).rstrip("\n")
    key_text = sym_key_var.get()
    if not t or not key_text:
        messagebox.showwarning("Input error", "Enter text and key.")
        return
    key = key_text.encode().ljust(32, b'0')[:32]
    iv = os.urandom(16)
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(t.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    b64 = base64.b64encode(iv + ciphertext).decode()
    set_result(sym_result, f"AES (base64 iv+cipher):\n{b64}")


def aes_decrypt_action():
    if not CRYPTOGRAPHY_AVAILABLE:
        messagebox.showerror("Missing library", "cryptography package is required for AES/DES.")
        return
    b64 = sym_text.get("1.0", tk.END).strip()
    key_text = sym_key_var.get()
    if not b64 or not key_text:
        messagebox.showwarning("Input error", "Enter base64 iv+cipher text and key.")
        return
    try:
        raw = base64.b64decode(b64)
    except Exception:
        messagebox.showerror("Input error", "Invalid base64 input.")
        return
    iv = raw[:16]
    ciphertext = raw[16:]
    key = key_text.encode().ljust(32, b'0')[:32]
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
    set_result(sym_result, f"AES Decrypted:\n{decrypted.decode()}")


def des_encrypt_action():
    if not CRYPTOGRAPHY_AVAILABLE:
        messagebox.showerror("Missing library", "cryptography package is required for AES/DES.")
        return
    t = sym_text.get("1.0", tk.END).rstrip("\n")
    key_text = sym_key_var.get()
    if not t or not key_text:
        messagebox.showwarning("Input error", "Enter text and key.")
        return
    key = key_text.encode().ljust(8, b'0')[:8]
    iv = os.urandom(8)
    backend = default_backend()
    cipher = Cipher(algorithms.TripleDES(key * 3), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(64).padder()
    padded_data = padder.update(t.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    b64 = base64.b64encode(iv + ciphertext).decode()
    set_result(sym_result, f"DES/TripleDES (base64 iv+cipher):\n{b64}")


def des_decrypt_action():
    if not CRYPTOGRAPHY_AVAILABLE:
        messagebox.showerror("Missing library", "cryptography package is required for AES/DES.")
        return
    b64 = sym_text.get("1.0", tk.END).strip()
    key_text = sym_key_var.get()
    if not b64 or not key_text:
        messagebox.showwarning("Input error", "Enter base64 iv+cipher text and key.")
        return
    try:
        raw = base64.b64decode(b64)
    except Exception:
        messagebox.showerror("Input error", "Invalid base64 input.")
        return
    iv = raw[:8]
    ciphertext = raw[8:]
    key = key_text.encode().ljust(8, b'0')[:8]
    backend = default_backend()
    cipher = Cipher(algorithms.TripleDES(key * 3), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(64).unpadder()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
    set_result(sym_result, f"DES Decrypted:\n{decrypted.decode()}")


# ---------------------------
# Hashing Frame (SHA-256)
# ---------------------------

def hash_action():
    t = hash_text.get("1.0", tk.END).rstrip("\n")
    if not t:
        messagebox.showwarning("Input error", "Enter text to hash.")
        return
    h = hashlib.sha256(t.encode('utf-8')).hexdigest()
    set_result(hash_result, h)


# ---------------------------
# RSA Frame - generate and autosave to fixed files
# ---------------------------

def rsa_generate_keys():
    if not PYCRYPTODOME_AVAILABLE:
        messagebox.showerror("Missing library", "pycryptodome required for RSA.")
        return
    try:
        size = int(rsa_keysize_var.get())
    except Exception:
        messagebox.showerror("Input error", "Key size must be an integer.")
        return

    # run generation in a background thread so UI stays responsive
    def _gen():
        try:
            key = RSA.generate(size)
            priv = key.export_key()
            pub = key.publickey().export_key()
            rsa_state['priv'] = priv
            rsa_state['pub'] = pub
            # autosave to fixed locations
            with open(PRIVATE_PEM, 'wb') as f:
                f.write(priv)
            with open(PUBLIC_PEM, 'wb') as f:
                f.write(pub)
            set_result(rsa_result, f"Private and public keys generated and saved:\n{PRIVATE_PEM}\n{PUBLIC_PEM}")
        except Exception as e:
            messagebox.showerror("Generation failed", str(e))

    threading.Thread(target=_gen, daemon=True).start()


def rsa_save_private():
    if 'priv' not in rsa_state:
        messagebox.showwarning("No key", "Generate or load a private key first.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".pem", filetypes=[("PEM files","*.pem"),("All files","*.*")])
    if path:
        with open(path, "wb") as f:
            f.write(rsa_state["priv"])
        messagebox.showinfo("Saved", f"Private key saved to {path}")


def rsa_save_public():
    if 'pub' not in rsa_state:
        messagebox.showwarning("No key", "Generate or load a public key first.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".pem", filetypes=[("PEM files","*.pem"),("All files","*.*")])
    if path:
        with open(path, "wb") as f:
            f.write(rsa_state["pub"])
        messagebox.showinfo("Saved", f"Public key saved to {path}")


def rsa_load_private():
    path = filedialog.askopenfilename(filetypes=[("PEM files","*.pem"),("All files","*.*")])
    if path:
        with open(path, "rb") as f:
            data = f.read()
        rsa_state["priv"] = data
        set_result(rsa_result, "Private key loaded from:\n" + path)


def rsa_load_public():
    path = filedialog.askopenfilename(filetypes=[("PEM files","*.pem"),("All files","*.*")])
    if path:
        with open(path, "rb") as f:
            data = f.read()
        rsa_state["pub"] = data
        set_result(rsa_result, "Public key loaded from:\n" + path)


def rsa_encrypt_action():
    if not PYCRYPTODOME_AVAILABLE:
        messagebox.showerror("Missing library", "pycryptodome required for RSA.")
        return
    if 'pub' not in rsa_state:
        # try to auto-load from default PUBLIC_PEM if exists
        if PUBLIC_PEM.exists():
            with open(PUBLIC_PEM, 'rb') as f:
                rsa_state['pub'] = f.read()
        else:
            messagebox.showwarning("No public key", "Load or generate a public key first.")
            return
    try:
        pubobj = RSA.import_key(rsa_state['pub'])
    except Exception as e:
        messagebox.showerror("Key error", f"Failed to import public key: {e}")
        return
    plaintext = rsa_text_in.get("1.0", tk.END).rstrip("\n")
    if not plaintext:
        messagebox.showwarning("Input error", "Enter text to encrypt.")
        return
    cipher = PKCS1_OAEP.new(pubobj)
    ct = cipher.encrypt(plaintext.encode("utf-8"))
    b64 = base64.b64encode(ct).decode()
    set_result(rsa_result, f"Encrypted (base64):\n{b64}")


def rsa_decrypt_action():
    if not PYCRYPTODOME_AVAILABLE:
        messagebox.showerror("Missing library", "pycryptodome required for RSA.")
        return
    if 'priv' not in rsa_state:
        # try auto-load default private
        if PRIVATE_PEM.exists():
            with open(PRIVATE_PEM, 'rb') as f:
                rsa_state['priv'] = f.read()
        else:
            messagebox.showwarning("No private key", "Load or generate a private key first.")
            return
    try:
        privobj = RSA.import_key(rsa_state['priv'])
    except Exception as e:
        messagebox.showerror("Key error", f"Failed to import private key: {e}")
        return
    b64 = rsa_text_in.get("1.0", tk.END).strip()
    if not b64:
        messagebox.showwarning("Input error", "Enter base64 encrypted text.")
        return
    try:
        ct = base64.b64decode(b64)
        cipher = PKCS1_OAEP.new(privobj)
        pt = cipher.decrypt(ct)
    except Exception as e:
        messagebox.showerror("Decryption failed", f"{e}")
        return
    set_result(rsa_result, "Decrypted plaintext:\n" + pt.decode())


# ---------------------------
# GUI: main window and layout
# ---------------------------

root = tk.Tk()
root.title(f"🔐{APP_NAME} ")
root.geometry("980x650")
root.resizable(False, False)

# color placeholders (will be set by apply_theme)
BG_ROOT = '#f6f8fa'
SIDEBAR_BG = '#ffffff'
CONTENT_BG = '#f2f6f9'
ACCENT = '#286ef0'
BTN_BG = '#286ef0'
BTN_HOVER = '#1f56d6'
TEXT_BG = '#ffffff'
TEXT_FG = '#0b1220'
MUTED_FG = '#546579'

root.config(bg=BG_ROOT)

# Left sidebar for tool selection
sidebar = tk.Frame(root, bg=SIDEBAR_BG, width=220)
sidebar.pack(side="left", fill="y")

# Animated indicator
indicator_frame = tk.Frame(sidebar, bg=ACCENT, width=6, height=38)
indicator_frame.place(x=8, y=60)

logo = tk.Label(sidebar, text="🔐", bg=SIDEBAR_BG, fg=ACCENT, font=("Segoe UI", 22))
logo.place(x=40, y=12)

title = tk.Label(sidebar, text=APP_NAME, bg=SIDEBAR_BG, fg=MUTED_FG, font=("Segoe UI", 11, "bold"))
title.place(x=72, y=22)

# store references to sidebar buttons for animation
sidebar_buttons = []

TOOLS = [
    ("Caesar Cipher", "caesar"),
    ("Vigenère Cipher", "vigenere"),
    ("AES / DES (Symmetric)", "symmetric"),
    ("SHA-256 Hash", "hash"),
    ("RSA (Public-Key)", "rsa"),
]

for i, (lbl, key) in enumerate(TOOLS):
    y = 60 + i * 52
    b = tk.Button(sidebar, text=lbl, anchor="w", width=20, relief="flat", bg=SIDEBAR_BG, fg=MUTED_FG,
                  command=lambda k=key, btn_index=i: (show_frame(k), animate_indicator_to(60 + btn_index*52)))
    b.place(x=22, y=y)
    make_fancy_button(b, normal_bg=SIDEBAR_BG, hover_bg='#eef6ff', active_bg='#e0edff')
    sidebar_buttons.append(b)

# Main content area
content = tk.Frame(root, bg=CONTENT_BG)
content.pack(side="right", fill="both", expand=True)

content_frames = {}

# ---------- Top tab bar (duplicate quick access as tabs) ----------

top_bar = tk.Frame(content, bg=CONTENT_BG)
top_bar.pack(fill='x', pady=(12, 0))

def on_top_tab(name, index):
    show_frame(name)
    animate_indicator_to(60 + index * 52)

for i, (lbl, key) in enumerate(TOOLS):
    tb = tk.Button(top_bar, text=lbl, bd=0, relief='flat', bg=BTN_BG, fg='white', padx=10, pady=6,
                   command=lambda k=key, idx=i: on_top_tab(k, idx))
    tb.pack(side='left', padx=6)
    make_fancy_button(tb, normal_bg=BTN_BG, hover_bg=BTN_HOVER, active_bg=None)

# Theme selector on the right of top bar

def apply_theme(theme_name):
    global BG_ROOT, SIDEBAR_BG, CONTENT_BG, ACCENT, BTN_BG, BTN_HOVER, TEXT_BG, TEXT_FG, MUTED_FG, CURRENT_THEME
    t = THEMES.get(theme_name, THEMES['Light Modern'])
    BG_ROOT = t['root_bg']
    SIDEBAR_BG = t['sidebar_bg']
    CONTENT_BG = t['content_bg']
    ACCENT = t['accent']
    BTN_BG = t['btn_bg']
    BTN_HOVER = t['btn_hover']
    TEXT_BG = t['text_bg']
    TEXT_FG = t['text_fg']
    MUTED_FG = t['muted_fg']
    CURRENT_THEME = theme_name

    # apply to root and main containers
    root.config(bg=BG_ROOT)
    sidebar.config(bg=SIDEBAR_BG)
    content.config(bg=CONTENT_BG)
    indicator_frame.config(bg=ACCENT)
    logo.config(bg=SIDEBAR_BG, fg=ACCENT)
    title.config(bg=SIDEBAR_BG, fg=MUTED_FG)
    footer.config(bg=BG_ROOT, fg=MUTED_FG)

    # sidebar buttons
    for b in sidebar_buttons:
        try:
            b.config(bg=SIDEBAR_BG, fg=MUTED_FG)
        except Exception:
            pass

    # top bar buttons
    for child in top_bar.winfo_children():
        if isinstance(child, tk.Button):
            try:
                child.config(bg=BTN_BG, fg='white')
            except Exception:
                pass

    # update content frames widgets (text areas and labels)
    for frame in content_frames.values():
        try:
            frame.config(bg=CONTENT_BG)
            for w in frame.winfo_children():
                # labels
                if isinstance(w, tk.Label):
                    w.config(bg=CONTENT_BG, fg=MUTED_FG)
                # text widgets
                if isinstance(w, tk.Text):
                    w.config(bg=TEXT_BG, fg=TEXT_FG, insertbackground=TEXT_FG)
                # frames inside
                if isinstance(w, tk.Frame):
                    w.config(bg=CONTENT_BG)
                    for c in w.winfo_children():
                        try:
                            if isinstance(c, tk.Button):
                                c.config(bg=BTN_BG, fg='white')
                            if isinstance(c, tk.Label):
                                c.config(bg=CONTENT_BG, fg=MUTED_FG)
                        except Exception:
                            pass
        except Exception:
            pass

# theme dropdown
theme_var = tk.StringVar(value=CURRENT_THEME)

def on_theme_change(*args):
    apply_theme(theme_var.get())

theme_menu = ttk.OptionMenu(top_bar, theme_var, CURRENT_THEME, *THEMES.keys(), command=lambda v: apply_theme(v))
theme_menu.pack(side='right', padx=12)

# ---------- Helper to switch frames ----------

def show_frame(name):
    for f in content_frames.values():
        f.pack_forget()
    content_frames[name].pack(fill="both", expand=True, padx=18, pady=12)


# ---------- Caesar Frame ----------
f_caesar = tk.Frame(content, bg=CONTENT_BG)
content_frames["caesar"] = f_caesar

tk.Label(f_caesar, text="Caesar Cipher", font=("Segoe UI", 16, "bold"), bg=CONTENT_BG, fg=ACCENT).pack(pady=6)
tk.Label(f_caesar, text="Enter message:", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
caesar_text = tk.Text(f_caesar, height=5, width=82, bd=0, relief="flat", font=("Consolas", 11), bg=TEXT_BG, fg=TEXT_FG, insertbackground=TEXT_FG)
caesar_text.pack(padx=6, pady=6)

tk.Label(f_caesar, text="Shift (0-25):", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
caesar_shift_var = tk.StringVar(value="3")
shift_entry = tk.Entry(f_caesar, textvariable=caesar_shift_var, width=6, bd=0, relief="flat", bg=TEXT_BG, fg=TEXT_FG, insertbackground=TEXT_FG)
shift_entry.pack(anchor="w", padx=6)

btnframe = tk.Frame(f_caesar, bg=CONTENT_BG)
btnframe.pack(pady=8)
enc_btn = tk.Button(btnframe, text="Encrypt", width=14, command=caesar_encrypt_action)
dec_btn = tk.Button(btnframe, text="Decrypt", width=14, command=caesar_decrypt_action)
copy_btn = tk.Button(btnframe, text="Copy Result", width=14, command=lambda: copy_to_clipboard(caesar_result.get("1.0", tk.END).strip()))
enc_btn.grid(row=0, column=0, padx=8)
dec_btn.grid(row=0, column=1, padx=8)
copy_btn.grid(row=0, column=2, padx=8)
for b in (enc_btn, dec_btn, copy_btn):
    make_fancy_button(b, normal_bg=BTN_BG, hover_bg=BTN_HOVER, active_bg=None)


tk.Label(f_caesar, text="Result:", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
caesar_result = tk.Text(f_caesar, height=5, width=82, bd=0, relief="flat", font=("Consolas", 11), state="disabled", bg=TEXT_BG, fg=TEXT_FG)
caesar_result.pack(padx=6, pady=6)

# ---------- Vigenere Frame ----------
f_vigenere = tk.Frame(content, bg=CONTENT_BG)
content_frames["vigenere"] = f_vigenere

tk.Label(f_vigenere, text="Vigenère Cipher", font=("Segoe UI", 16, "bold"), bg=CONTENT_BG, fg=ACCENT).pack(pady=6)
tk.Label(f_vigenere, text="Enter text:", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
vigenere_text = tk.Text(f_vigenere, height=5, width=82, bd=0, relief="flat", font=("Consolas", 11), bg=TEXT_BG, fg=TEXT_FG)
vigenere_text.pack(padx=6, pady=6)

tk.Label(f_vigenere, text="Keyword:", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
vigenere_key_var = tk.StringVar()
key_entry = tk.Entry(f_vigenere, textvariable=vigenere_key_var, width=30, bd=0, relief="flat", bg=TEXT_BG, fg=TEXT_FG)
key_entry.pack(anchor="w", padx=6, pady=6)

vbtnframe = tk.Frame(f_vigenere, bg=CONTENT_BG)
vbtnframe.pack(pady=8)
ve_enc = tk.Button(vbtnframe, text="Encrypt", width=14, command=vigenere_encrypt_action)
ve_dec = tk.Button(vbtnframe, text="Decrypt", width=14, command=vigenere_decrypt_action)
ve_copy = tk.Button(vbtnframe, text="Copy Result", width=14, command=lambda: copy_to_clipboard(vigenere_result.get("1.0", tk.END).strip()))
ve_enc.grid(row=0, column=0, padx=8)
ve_dec.grid(row=0, column=1, padx=8)
ve_copy.grid(row=0, column=2, padx=8)
for b in (ve_enc, ve_dec, ve_copy):
    make_fancy_button(b, normal_bg=BTN_BG, hover_bg=BTN_HOVER, active_bg=None)


tk.Label(f_vigenere, text="Result:", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
vigenere_result = tk.Text(f_vigenere, height=5, width=82, bd=0, relief="flat", font=("Consolas", 11), state="disabled", bg=TEXT_BG, fg=TEXT_FG)
vigenere_result.pack(padx=6, pady=6)

# ---------- Symmetric (AES/DES) Frame ----------
f_sym = tk.Frame(content, bg=CONTENT_BG)
content_frames["symmetric"] = f_sym

tk.Label(f_sym, text="AES / DES (Symmetric)", font=("Segoe UI", 16, "bold"), bg=CONTENT_BG, fg=ACCENT).pack(pady=6)
tk.Label(f_sym, text="Enter text (for encrypt) or paste base64 (iv+cipher) for decrypt:", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
sym_text = tk.Text(f_sym, height=6, width=82, bd=0, relief="flat", font=("Consolas", 11), bg=TEXT_BG, fg=TEXT_FG)
sym_text.pack(padx=6, pady=6)

tk.Label(f_sym, text="Key (any text):", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
sym_key_var = tk.StringVar()
key_entry_sym = tk.Entry(f_sym, textvariable=sym_key_var, width=44, bd=0, relief="flat", bg=TEXT_BG, fg=TEXT_FG)
key_entry_sym.pack(anchor="w", padx=6, pady=6)

sbtnframe = tk.Frame(f_sym, bg=CONTENT_BG)
sbtnframe.pack(pady=8)
aes_enc_btn = tk.Button(sbtnframe, text="AES Encrypt", width=14, command=aes_encrypt_action)
aes_dec_btn = tk.Button(sbtnframe, text="AES Decrypt", width=14, command=aes_decrypt_action)
des_enc_btn = tk.Button(sbtnframe, text="DES Encrypt", width=14, command=des_encrypt_action)
des_dec_btn = tk.Button(sbtnframe, text="DES Decrypt", width=14, command=des_decrypt_action)
copy_sym = tk.Button(sbtnframe, text="Copy Result", width=14, command=lambda: copy_to_clipboard(sym_result.get("1.0", tk.END).strip()))
aes_enc_btn.grid(row=0, column=0, padx=8)
aes_dec_btn.grid(row=0, column=1, padx=8)
des_enc_btn.grid(row=0, column=2, padx=8)
des_dec_btn.grid(row=0, column=3, padx=8)
copy_sym.grid(row=0, column=4, padx=8)
for b in (aes_enc_btn, aes_dec_btn, des_enc_btn, des_dec_btn, copy_sym):
    make_fancy_button(b, normal_bg=BTN_BG, hover_bg=BTN_HOVER, active_bg=None)


tk.Label(f_sym, text="Result:", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
sym_result = tk.Text(f_sym, height=6, width=82, bd=0, relief="flat", font=("Consolas", 11), state="disabled", bg=TEXT_BG, fg=TEXT_FG)
sym_result.pack(padx=6, pady=6)

if not CRYPTOGRAPHY_AVAILABLE:
    aes_enc_btn.config(state="disabled")
    aes_dec_btn.config(state="disabled")
    des_enc_btn.config(state="disabled")
    des_dec_btn.config(state="disabled")
    set_result(sym_result, "cryptography package is NOT installed. AES/DES functions are disabled.\nInstall with: pip install cryptography")

# ---------- Hash Frame ----------
f_hash = tk.Frame(content, bg=CONTENT_BG)
content_frames["hash"] = f_hash

tk.Label(f_hash, text="SHA-256 Hash", font=("Segoe UI", 16, "bold"), bg=CONTENT_BG, fg=ACCENT).pack(pady=6)
tk.Label(f_hash, text="Enter text to hash:", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
hash_text = tk.Text(f_hash, height=6, width=82, bd=0, relief="flat", font=("Consolas", 11), bg=TEXT_BG, fg=TEXT_FG)
hash_text.pack(padx=6, pady=6)

hash_btn = tk.Button(f_hash, text="Compute SHA-256", width=18, command=hash_action)
copy_hash = tk.Button(f_hash, text="Copy Result", width=14, command=lambda: copy_to_clipboard(hash_result.get("1.0", tk.END).strip()))
hash_btn.pack(pady=8)
copy_hash.pack()
for b in (hash_btn, copy_hash):
    make_fancy_button(b, normal_bg=BTN_BG, hover_bg=BTN_HOVER, active_bg=None)


tk.Label(f_hash, text="Result (hex):", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6, pady=(8,0))
hash_result = tk.Text(f_hash, height=4, width=82, bd=0, relief="flat", font=("Consolas", 11), state="disabled", bg=TEXT_BG, fg=TEXT_FG)
hash_result.pack(padx=6, pady=6)

# ---------- RSA Frame ----------
f_rsa = tk.Frame(content, bg=CONTENT_BG)
content_frames["rsa"] = f_rsa

tk.Label(f_rsa, text="RSA (Public-Key)", font=("Segoe UI", 16, "bold"), bg=CONTENT_BG, fg=ACCENT).pack(pady=6)

rsa_controls = tk.Frame(f_rsa, bg=CONTENT_BG)
rsa_controls.pack(anchor="w", padx=6)

tk.Label(rsa_controls, text="Key size:", bg=CONTENT_BG, fg=MUTED_FG).grid(row=0, column=0, padx=6, pady=6, sticky="w")
rsa_keysize_var = tk.StringVar(value="2048")
key_entry_rsa = tk.Entry(rsa_controls, textvariable=rsa_keysize_var, width=8, bd=0, relief="flat", bg=TEXT_BG, fg=TEXT_FG)
key_entry_rsa.grid(row=0, column=1, padx=6)

rsa_btns = tk.Frame(rsa_controls, bg=CONTENT_BG)
rsa_btns.grid(row=0, column=2, padx=6)

btn_generate = tk.Button(rsa_btns, text="Generate Keys", command=rsa_generate_keys)
btn_save_priv = tk.Button(rsa_btns, text="Save Private", command=rsa_save_private)
btn_save_pub = tk.Button(rsa_btns, text="Save Public", command=rsa_save_public)
btn_generate.grid(row=0, column=0, padx=6)
btn_save_priv.grid(row=0, column=1, padx=6)
btn_save_pub.grid(row=0, column=2, padx=6)
for b in (btn_generate, btn_save_priv, btn_save_pub):
    make_fancy_button(b, normal_bg=BTN_BG, hover_bg=BTN_HOVER, active_bg=None)

rsa_loads = tk.Frame(rsa_controls, bg=CONTENT_BG)
rsa_loads.grid(row=1, column=0, columnspan=3, pady=6, sticky="w")
btn_load_priv = tk.Button(rsa_loads, text="Load Private", command=rsa_load_private)
btn_load_pub = tk.Button(rsa_loads, text="Load Public", command=rsa_load_public)
btn_load_priv.grid(row=0, column=0, padx=6)
btn_load_pub.grid(row=0, column=1, padx=6)
for b in (btn_load_priv, btn_load_pub):
    make_fancy_button(b, normal_bg='#222831', hover_bg='#1b2427', active_bg='#162022')


tk.Label(f_rsa, text="Input (for encrypt or decrypt):", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
rsa_text_in = tk.Text(f_rsa, height=6, width=82, bd=0, relief="flat", font=("Consolas", 11), bg=TEXT_BG, fg=TEXT_FG)
rsa_text_in.pack(padx=6, pady=6)

rsa_actions = tk.Frame(f_rsa, bg=CONTENT_BG)
rsa_actions.pack()
enc_btn_r = tk.Button(rsa_actions, text="Encrypt with Public", command=rsa_encrypt_action, width=18)
dec_btn_r = tk.Button(rsa_actions, text="Decrypt with Private", command=rsa_decrypt_action, width=18)
copy_r = tk.Button(rsa_actions, text="Copy Result", width=14, command=lambda: copy_to_clipboard(rsa_result.get("1.0", tk.END).strip()))
enc_btn_r.grid(row=0, column=0, padx=6)
dec_btn_r.grid(row=0, column=1, padx=6)
copy_r.grid(row=0, column=2, padx=6)
for b in (enc_btn_r, dec_btn_r, copy_r):
    make_fancy_button(b, normal_bg=BTN_BG, hover_bg=BTN_HOVER, active_bg=None)


tk.Label(f_rsa, text="Result:", bg=CONTENT_BG, fg=MUTED_FG).pack(anchor="w", padx=6)
rsa_result = tk.Text(f_rsa, height=8, width=82, bd=0, relief="flat", font=("Consolas", 11), state="disabled", bg=TEXT_BG, fg=TEXT_FG)
rsa_result.pack(padx=6, pady=6)

if not PYCRYPTODOME_AVAILABLE:
    set_result(rsa_result, "pycryptodome (Crypto) package NOT installed. RSA functions disabled.\nInstall with: pip install pycryptodome")
    # disable RSA UI buttons
    for child in (btn_generate, btn_save_priv, btn_save_pub, btn_load_priv, btn_load_pub, enc_btn_r, dec_btn_r):
        child.config(state="disabled")

# small state for RSA keys
rsa_state = {}

# Initialize by showing the Caesar frame and moving indicator there
show_frame("caesar")
indicator_frame.place(x=8, y=60)

# Footer
footer = tk.Label(root, text=f"© {APP_NAME} — Designed by Faseeh", bg=BG_ROOT, fg=MUTED_FG, font=("Segoe UI", 9))
footer.place(relx=0.5, rely=0.975, anchor="s")

# apply initial theme
apply_theme(CURRENT_THEME)

# Start GUI loop
root.mainloop()