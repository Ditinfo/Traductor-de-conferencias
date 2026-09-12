"""
Traducción en vivo — Inglés a Español (aplicación de escritorio)

Escucha el micrófono, transcribe lo que se dice en inglés, lo traduce
al español y lo muestra en pantalla (opcionalmente lo lee en voz alta).

Requisitos: ver requirements.txt / README.md
"""

import datetime
import queue
import threading
import tkinter as tk
from tkinter import messagebox

import speech_recognition as sr
from deep_translator import GoogleTranslator
import pyttsx3

# ---------- Paleta y estilo ----------
BG = "#0F1216"
PANEL = "#171B21"
PANEL_2 = "#1C2129"
LINE = "#262B33"
TEXT_HI = "#F2F4F7"
TEXT_LO = "#97A1AF"
AMBER = "#E8A33D"
RED = "#D96B6B"
GREEN = "#5FAE82"

UI_FONT = ("Segoe UI", 11)
LABEL_FONT = ("Segoe UI Semibold", 11)


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Traducción en vivo · Inglés → Español")
        root.geometry("960x680")
        root.minsize(720, 480)
        root.configure(bg=BG)

        self.listening = False
        self.stop_listening_fn = None
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = pyttsx3.init()
        self.tts_queue = queue.Queue()
        self.transcript = []  # [{"time","original","translated"}]

        self.auto_speak = tk.BooleanVar(value=False)
        self.font_size = tk.IntVar(value=28)
        self.voice_names = []

        self._build_ui()
        self._populate_voices()
        self._start_tts_worker()

        threading.Thread(target=self._init_microphone, daemon=True).start()

    # ---------- UI ----------
    def _build_ui(self):
        topbar = tk.Frame(self.root, bg=PANEL, height=56)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        left = tk.Frame(topbar, bg=PANEL)
        left.pack(side="left", padx=20)

        self.status_dot = tk.Canvas(left, width=12, height=12, bg=PANEL, highlightthickness=0)
        self.status_dot.pack(side="left", pady=20)
        self._dot_id = self.status_dot.create_oval(1, 1, 11, 11, fill=TEXT_LO, outline="")

        tk.Label(left, text="Traducción en vivo", font=("Segoe UI Semibold", 13),
                 bg=PANEL, fg=TEXT_HI).pack(side="left", padx=10)
        tk.Label(left, text="Inglés → Español", font=UI_FONT,
                 bg=PANEL, fg=TEXT_LO).pack(side="left", padx=6)

        self.status_label = tk.Label(topbar, text="Iniciando micrófono…", font=UI_FONT,
                                      bg=PANEL, fg=TEXT_LO)
        self.status_label.pack(side="right", padx=20)

        # panel original (arriba, más chico)
        original_wrap = tk.Frame(self.root, bg=PANEL)
        original_wrap.pack(fill="x", side="top")
        tk.Label(original_wrap, text="Original (inglés)", font=LABEL_FONT,
                 bg=PANEL, fg=TEXT_LO).pack(anchor="w", padx=22, pady=(12, 4))

        self.original_box = tk.Text(original_wrap, height=6, wrap="word", bg=PANEL,
                                     fg=TEXT_LO, font=("Segoe UI", 12), bd=0,
                                     highlightthickness=0, state="disabled")
        self.original_box.pack(fill="x", padx=22, pady=(0, 14))

        # separador
        tk.Frame(self.root, bg=LINE, height=1).pack(fill="x")

        # panel traducido (abajo, grande)
        translated_wrap = tk.Frame(self.root, bg=BG)
        translated_wrap.pack(fill="both", expand=True, side="top")
        tk.Label(translated_wrap, text="Traducción (español)", font=LABEL_FONT,
                 bg=BG, fg=TEXT_LO).pack(anchor="w", padx=22, pady=(14, 4))

        self.translated_box = tk.Text(translated_wrap, wrap="word", bg=BG, fg=TEXT_HI,
                                       font=("Segoe UI", self.font_size.get()), bd=0,
                                       highlightthickness=0, state="disabled")
        self.translated_box.pack(fill="both", expand=True, padx=22, pady=(0, 14))

        # barra inferior de controles
        controls = tk.Frame(self.root, bg=PANEL)
        controls.pack(fill="x", side="bottom")
        inner = tk.Frame(controls, bg=PANEL)
        inner.pack(fill="x", padx=16, pady=12)

        self.toggle_btn = tk.Button(inner, text="Iniciar traducción", font=("Segoe UI Semibold", 11),
                                     bg=AMBER, fg="#1a1207", relief="flat", padx=16, pady=8,
                                     activebackground=AMBER, command=self.toggle_listening,
                                     state="disabled")
        self.toggle_btn.pack(side="left")

        speak_chk = tk.Checkbutton(inner, text="Leer traducción en voz alta", variable=self.auto_speak,
                                    bg=PANEL, fg=TEXT_LO, selectcolor=PANEL_2,
                                    activebackground=PANEL, font=UI_FONT)
        speak_chk.pack(side="left", padx=16)

        tk.Label(inner, text="Voz:", bg=PANEL, fg=TEXT_LO, font=UI_FONT).pack(side="left", padx=(10, 4))
        self.voice_var = tk.StringVar()
        self.voice_menu = tk.OptionMenu(inner, self.voice_var, "")
        self.voice_menu.config(bg=PANEL_2, fg=TEXT_HI, relief="flat", highlightthickness=0)
        self.voice_menu.pack(side="left")

        tk.Button(inner, text="A−", font=("Segoe UI Semibold", 10), bg=PANEL_2, fg=TEXT_HI,
                  relief="flat", padx=10, command=lambda: self._change_font(-4)).pack(side="left", padx=(16, 2))
        tk.Button(inner, text="A+", font=("Segoe UI Semibold", 10), bg=PANEL_2, fg=TEXT_HI,
                  relief="flat", padx=10, command=lambda: self._change_font(4)).pack(side="left")

        tk.Button(inner, text="Limpiar", font=UI_FONT, bg=PANEL_2, fg=TEXT_HI, relief="flat",
                  padx=14, command=self.clear_all).pack(side="right", padx=(6, 0))
        tk.Button(inner, text="Guardar transcripción", font=UI_FONT, bg=PANEL_2, fg=TEXT_HI,
                  relief="flat", padx=14, command=self.save_transcript).pack(side="right")

    # ---------- micrófono ----------
    def _init_microphone(self):
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.root.after(0, self._mic_ready)
        except Exception as e:
            self.root.after(0, lambda: self._mic_failed(str(e)))

    def _mic_ready(self):
        self.toggle_btn.config(state="normal")
        self._set_status("idle", "Listo — presioná Iniciar")

    def _mic_failed(self, err):
        self._set_status("error", "No se encontró micrófono")
        messagebox.showerror("Micrófono no disponible",
                              f"No se pudo inicializar el micrófono.\n\nDetalle: {err}")

    # ---------- estado visual ----------
    def _set_status(self, state, text):
        colors = {"idle": TEXT_LO, "live": GREEN, "error": RED}
        self.status_dot.itemconfig(self._dot_id, fill=colors.get(state, TEXT_LO))
        self.status_label.config(text=text)

    # ---------- escuchar / traducir ----------
    def toggle_listening(self):
        if not self.listening:
            self.start_listening()
        else:
            self.pause_listening()

    def start_listening(self):
        self.listening = True
        self.toggle_btn.config(text="Detener traducción", bg=RED, fg="#1a1010")
        self._set_status("live", "Escuchando…")
        self.stop_listening_fn = self.recognizer.listen_in_background(
            self.microphone, self._on_audio, phrase_time_limit=8
        )

    def pause_listening(self):
        self.listening = False
        if self.stop_listening_fn:
            self.stop_listening_fn(wait_for_stop=False)
        self.toggle_btn.config(text="Iniciar traducción", bg=AMBER, fg="#1a1207")
        self._set_status("idle", "Detenido")

    def _on_audio(self, recognizer, audio):
        # corre en un hilo secundario (callback de speech_recognition)
        try:
            text = recognizer.recognize_google(audio, language="en-US")
        except sr.UnknownValueError:
            return
        except sr.RequestError as e:
            self.root.after(0, lambda: self._set_status("error", f"Error de red: {e}"))
            return
        text = text.strip()
        if not text:
            return
        self.root.after(0, self._add_original_line, text)
        threading.Thread(target=self._translate_and_display, args=(text,), daemon=True).start()

    def _add_original_line(self, text):
        self.original_box.configure(state="normal")
        self.original_box.insert(tk.END, text + "\n")
        self.original_box.see(tk.END)
        self.original_box.configure(state="disabled")

    def _translate_and_display(self, text):
        try:
            translated = GoogleTranslator(source="en", target="es").translate(text)
        except Exception:
            translated = "[No se pudo traducir esta frase]"

        record = {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "original": text,
            "translated": translated,
        }
        self.transcript.append(record)
        self.root.after(0, self._add_translated_line, translated)

        if self.auto_speak.get() and not translated.startswith("["):
            self.tts_queue.put(translated)

    def _add_translated_line(self, text):
        self.translated_box.configure(state="normal")
        self.translated_box.insert(tk.END, text + "\n\n")
        self.translated_box.see(tk.END)
        self.translated_box.configure(state="disabled")

    # ---------- texto a voz ----------
    def _populate_voices(self):
        try:
            voices = self.tts_engine.getProperty("voices")
        except Exception:
            voices = []
        spanish_voices = [v for v in voices if "es" in (v.languages[0].decode(errors="ignore")
                          if v.languages else "").lower() or "spanish" in v.name.lower()
                          or "español" in v.name.lower()]
        candidates = spanish_voices if spanish_voices else voices
        self.voice_map = {v.name: v.id for v in candidates}
        names = list(self.voice_map.keys()) or ["(sin voces disponibles)"]

        menu = self.voice_menu["menu"]
        menu.delete(0, "end")
        for name in names:
            menu.add_command(label=name, command=lambda n=name: self.voice_var.set(n))
        self.voice_var.set(names[0])

    def _start_tts_worker(self):
        def worker():
            while True:
                text = self.tts_queue.get()
                try:
                    voice_id = self.voice_map.get(self.voice_var.get())
                    if voice_id:
                        self.tts_engine.setProperty("voice", voice_id)
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                except Exception:
                    pass
        threading.Thread(target=worker, daemon=True).start()

    # ---------- controles varios ----------
    def _change_font(self, delta):
        self.font_size.set(max(16, min(56, self.font_size.get() + delta)))
        self.translated_box.configure(font=("Segoe UI", self.font_size.get()))

    def clear_all(self):
        for box in (self.original_box, self.translated_box):
            box.configure(state="normal")
            box.delete("1.0", tk.END)
            box.configure(state="disabled")
        self.transcript = []

    def save_transcript(self):
        if not self.transcript:
            messagebox.showinfo("Transcripción", "Todavía no hay nada para guardar.")
            return
        filename = f"transcripcion-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("Transcripción de traducción en vivo (inglés → español)\n\n")
            for r in self.transcript:
                f.write(f"[{r['time']}]\nEN: {r['original']}\nES: {r['translated']}\n\n")
        messagebox.showinfo("Transcripción guardada", f"Se guardó como:\n{filename}")


def main():
    root = tk.Tk()
    TranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
