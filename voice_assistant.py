import datetime
import math
import os
import platform
import random
import re
import sys
import threading
import time
import webbrowser
from urllib.parse import quote_plus

import pyttsx3
import speech_recognition as sr
import tkinter as tk


class JarvisAssistant:
    def __init__(self):
        self.name = "Jarvis"
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 170)
        self.engine.setProperty("volume", 1.0)
        self.notes_file = os.path.join(os.getcwd(), "jarvis_notes.txt")
        self.history_file = os.path.join(os.getcwd(), "jarvis_history.txt")
        self.reminders = []
        self.sleeping = False

    def speak(self, text):
        if not text:
            return
        self.engine.say(text)
        self.engine.runAndWait()

    def log_command(self, command):
        with open(self.history_file, "a", encoding="utf-8") as file:
            file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {command}\n")

    def listen(self, prompt_text="Listening..."):
        recognizer = sr.Recognizer()
        recognizer.pause_threshold = 1
        recognizer.energy_threshold = 400

        with sr.Microphone() as source:
            print(prompt_text)
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)

        try:
            query = recognizer.recognize_google(audio, language="en-in")
            print(f"You said: {query}")
            return query.lower()
        except sr.UnknownValueError:
            self.speak("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            self.speak("Network error. Please check your internet connection.")
            return ""
        except Exception:
            self.speak("There was a problem while processing your voice input.")
            return ""

    def wait_for_wake_word(self):
        while True:
            command = self.listen("Waiting for wake word...")
            if not command:
                continue
            if "jarvis" in command or "wake up" in command or "hello jarvis" in command:
                self.speak("Yes, I am listening.")
                return
            if "sleep" in command or "go to sleep" in command:
                self.sleeping = True
                self.speak("Going to sleep mode.")
                return

    def open_website(self, url):
        webbrowser.open(url)

    def search_web(self, query):
        search_url = f"https://www.google.com/search?q={quote_plus(query)}"
        webbrowser.open(search_url)

    def open_application(self, app_name):
        app_map = {
            "notepad": r"C:\Windows\System32\notepad.exe",
            "calculator": r"C:\Windows\System32\calc.exe",
            "command prompt": r"C:\Windows\System32\cmd.exe",
            "paint": r"C:\Windows\System32\mspaint.exe",
            "task manager": r"C:\Windows\System32\taskmgr.exe",
        }

        target = app_map.get(app_name.lower())
        if not target:
            self.speak(f"I do not know how to open {app_name}.")
            return False

        try:
            if hasattr(os, "startfile"):
                os.startfile(target)
            self.speak(f"Opening {app_name}.")
            return True
        except Exception:
            self.speak(f"I could not open {app_name}.")
            return False

    def open_file(self, file_path):
        if not os.path.exists(file_path):
            self.speak("That file does not exist.")
            return False

        try:
            if hasattr(os, "startfile"):
                os.startfile(file_path)
            self.speak("Opening file.")
            return True
        except Exception:
            self.speak("I could not open that file.")
            return False

    def create_greeting(self):
        hour = datetime.datetime.now().hour
        if hour < 12:
            return "Good morning"
        if hour < 18:
            return "Good afternoon"
        return "Good evening"

    def get_current_time(self):
        return datetime.datetime.now().strftime("%I:%M %p")

    def get_current_date(self):
        return datetime.datetime.now().strftime("%A, %d %B %Y")

    def save_note(self, note_text):
        with open(self.notes_file, "a", encoding="utf-8") as file:
            file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {note_text}\n")
        self.speak("Note saved successfully.")

    def read_notes(self):
        if not os.path.exists(self.notes_file):
            self.speak("You have no saved notes yet.")
            return

        with open(self.notes_file, "r", encoding="utf-8") as file:
            notes = file.read().strip()

        if notes:
            self.speak(notes)
        else:
            self.speak("There are no notes in your file.")

    def set_reminder(self, command):
        match = re.search(r"in\s+(\d+)\s+(second|seconds|minute|minutes|hour|hours)", command)
        if not match:
            self.speak("Please use a format like: remind me in 5 minutes to drink water.")
            return

        value = int(match.group(1))
        unit = match.group(2)
        reminder_text = command.split("to ", 1)[1].strip() if " to " in command else "your reminder"

        if unit.startswith("second"):
            delay = value
        elif unit.startswith("minute"):
            delay = value * 60
        else:
            delay = value * 3600

        timer = threading.Timer(delay, lambda: self.speak(f"Reminder: {reminder_text}"))
        timer.daemon = True
        timer.start()
        self.reminders.append((delay, reminder_text))
        self.speak(f"Reminder set for {value} {unit} from now.")

    def calculate_expression(self, command):
        cleaned = command.replace("calculate", "").replace("what is", "")
        cleaned = cleaned.replace("plus", "+").replace("minus", "-")
        cleaned = cleaned.replace("multiplied by", "*").replace("divided by", "/")
        cleaned = cleaned.replace("times", "*").replace("into", "/")
        cleaned = re.sub(r"[^0-9+\-*/().% ]", "", cleaned)
        cleaned = cleaned.strip()

        if not cleaned:
            return None

        try:
            return eval(cleaned, {"__builtins__": {}}, {})
        except Exception:
            return None

    def get_system_info(self):
        return (
            f"Operating system: {platform.system()} {platform.release()}. "
            f"Computer name: {platform.node()}. "
            f"Processor: {platform.processor() or 'Unknown'}."
        )

    def show_help(self):
        help_text = (
            "I can tell the time, date, open websites, open apps like notepad or calculator, "
            "search the web, save and read notes, set reminders, answer simple calculations, "
            "show system information, tell jokes, and exit."
        )
        self.speak(help_text)

    def handle_command(self, command):
        if not command:
            return

        command = command.strip().lower()
        self.log_command(command)

        if "sleep" in command or "go to sleep" in command:
            self.sleeping = True
            self.speak("Going to sleep mode.")
            return

        if command.startswith("jarvis"):
            command = command.replace("jarvis", "", 1).strip()

        if any(word in command for word in ["hello", "hi", "hey"]):
            self.speak("Hello! I am Jarvis, your personal assistant. How may I help you?")
            return

        if "help" in command:
            self.show_help()
            return

        if "time" in command:
            self.speak(f"The time is {self.get_current_time()}.")
            return

        if "date" in command:
            self.speak(f"Today is {self.get_current_date()}.")
            return

        if "good morning" in command or "good afternoon" in command or "good evening" in command:
            self.speak(f"{self.create_greeting()}! How can I help you?")
            return

        if "open youtube" in command:
            self.speak("Opening YouTube.")
            self.open_website("https://youtube.com")
            return

        if "open google" in command:
            self.speak("Opening Google.")
            self.open_website("https://google.com")
            return

        if "open github" in command:
            self.speak("Opening GitHub.")
            self.open_website("https://github.com")
            return

        if "open news" in command or "news" in command:
            self.speak("Opening the latest news.")
            self.open_website("https://news.google.com")
            return

        if "open notepad" in command:
            self.open_application("notepad")
            return

        if "open calculator" in command:
            self.open_application("calculator")
            return

        if "open command prompt" in command or "open cmd" in command:
            self.open_application("command prompt")
            return

        if "open paint" in command:
            self.open_application("paint")
            return

        if "search for" in command or "search" in command:
            query = command.replace("search for", "", 1).replace("search", "", 1).strip()
            if query:
                self.speak(f"Searching for {query}.")
                self.search_web(query)
            else:
                self.speak("What would you like me to search for?")
            return

        if "weather" in command:
            self.speak("Opening weather information.")
            self.open_website("https://www.google.com/search?q=weather")
            return

        if "who are you" in command or "your name" in command:
            self.speak(f"I am {self.name}, your personal voice assistant built to help with your daily tasks.")
            return

        if "joke" in command:
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs.",
                "I told my computer I needed a break, and it sent me to sleep mode.",
                "Why do coders call it debugging? Because they are trying to remove the bugs."
            ]
            self.speak(random.choice(jokes))
            return

        if "remember" in command or "note" in command:
            note = command.replace("remember", "", 1).replace("note", "", 1).strip()
            if note:
                self.save_note(note)
            else:
                self.speak("What should I remember?")
            return

        if "read notes" in command or "open notes" in command:
            self.read_notes()
            return

        if "remind me" in command or "set reminder" in command:
            self.set_reminder(command)
            return

        if "calculate" in command or "what is" in command:
            result = self.calculate_expression(command)
            if result is not None:
                self.speak(f"The result is {result}.")
            else:
                self.speak("I could not understand that calculation. Please try again.")
            return

        if "system info" in command or "computer info" in command:
            self.speak(self.get_system_info())
            return

        if "exit" in command or "quit" in command or "shutdown" in command:
            self.speak("Goodbye. See you soon.")
            raise SystemExit

        self.speak(
            f"I heard: {command}. I can help with websites, apps, notes, reminders, calculations, search, and system info."
        )

    def run(self):
        self.speak(f"{self.create_greeting()} Anushka. I am {self.name}, your advanced assistant. I am online and waiting for my wake word.")

        while True:
            if self.sleeping:
                self.speak("I am sleeping. Say Jarvis to wake me up.")
                command = self.listen("Sleeping... waiting for wake word...")
                if command and ("jarvis" in command or "wake up" in command or "hello jarvis" in command):
                    self.sleeping = False
                    self.speak("I am back online.")
                continue

            self.wait_for_wake_word()
            command = self.listen("What can I do for you?")
            if not command:
                continue

            if "sleep" in command or "go to sleep" in command:
                self.sleeping = True
                continue

            self.handle_command(command)


class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JARVIS | Assistant Console")
        self.root.geometry("1120x760")
        self.root.configure(bg="#020b14")
        self.root.minsize(950, 620)

        self.assistant = JarvisAssistant()
        self.stop_event = threading.Event()
        self.status_colors = ["#22d3ee", "#38bdf8", "#67e8f9", "#a5f3fc"]
        self.status_index = 0
        self.state = "Idle"
        self.phase = 0.0

        topbar = tk.Frame(root, bg="#020b14")
        topbar.pack(fill=tk.X, padx=28, pady=(18, 10))

        self.indicator = tk.Canvas(topbar, width=18, height=18, bg="#020b14", highlightthickness=0)
        self.indicator.pack(side=tk.LEFT)
        self.indicator.create_oval(2, 2, 16, 16, fill="#22d3ee", outline="#22d3ee")

        title_label = tk.Label(
            topbar,
            text="JARVIS CORE",
            fg="#e0f2fe",
            bg="#020b14",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(side=tk.LEFT, padx=(12, 0))

        self.status_label = tk.Label(
            topbar,
            text="Status: Idle",
            fg="#cbd5e1",
            bg="#020b14",
            font=("Segoe UI", 11, "bold")
        )
        self.status_label.pack(side=tk.RIGHT)

        dashboard = tk.Frame(root, bg="#020b14")
        dashboard.pack(fill=tk.X, padx=28, pady=(0, 14))

        cards = [
            ("time", "TIME", "--:--"),
            ("date", "DATE", "--/--/----"),
            ("mic", "MIC", "READY"),
            ("ai", "AI", "STABLE"),
        ]

        for index, (card_key, label_text, default) in enumerate(cards):
            card_frame = tk.Frame(dashboard, bg="#071827", bd=1, relief=tk.FLAT, highlightbackground="#16314d")
            card_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12) if index < 3 else (0, 0))
            tk.Label(card_frame, text=label_text, fg="#7dd3fc", bg="#071827", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
            if card_key == "time":
                self.time_label = tk.Label(card_frame, text=default, fg="#f8fafc", bg="#071827", font=("Segoe UI", 18, "bold"))
                self.time_label.pack(anchor="w", padx=12, pady=(5, 12))
            elif card_key == "date":
                self.date_label = tk.Label(card_frame, text=default, fg="#f8fafc", bg="#071827", font=("Segoe UI", 12, "bold"))
                self.date_label.pack(anchor="w", padx=12, pady=(6, 12))
            elif card_key == "mic":
                self.mic_label = tk.Label(card_frame, text=default, fg="#f8fafc", bg="#071827", font=("Segoe UI", 12, "bold"))
                self.mic_label.pack(anchor="w", padx=12, pady=(6, 12))
            else:
                self.ai_label = tk.Label(card_frame, text=default, fg="#f8fafc", bg="#071827", font=("Segoe UI", 12, "bold"))
                self.ai_label.pack(anchor="w", padx=12, pady=(6, 12))

        main_panel = tk.Frame(root, bg="#020b14")
        main_panel.pack(fill=tk.BOTH, expand=True, padx=28, pady=(0, 18))

        self.core_panel = tk.Frame(main_panel, bg="#071827", highlightbackground="#12314b", highlightthickness=1)
        self.core_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 14))

        self.core_canvas = tk.Canvas(
            self.core_panel,
            width=430,
            height=430,
            bg="#071827",
            highlightthickness=0
        )
        self.core_canvas.pack(expand=True, pady=18)

        self.core_label = tk.Label(
            self.core_panel,
            text="READY",
            fg="#a5f3fc",
            bg="#071827",
            font=("Segoe UI", 18, "bold")
        )
        self.core_label.pack(pady=(0, 18))

        right_panel = tk.Frame(main_panel, bg="#020b14")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        log_title = tk.Label(
            right_panel,
            text="ACTIVITY LOG",
            fg="#93c5fd",
            bg="#020b14",
            font=("Segoe UI", 12, "bold")
        )
        log_title.pack(anchor="w", pady=(8, 8))

        self.log_area = tk.Text(
            right_panel,
            height=18,
            bg="#071827",
            fg="#dbeafe",
            font=("Segoe UI", 10),
            wrap="word",
            padx=12,
            pady=12,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        self.log_area.insert(tk.END, "System online.\n")
        self.log_area.config(state=tk.DISABLED)
        self.log_area.pack(fill=tk.BOTH, expand=True)

        bottom = tk.Frame(root, bg="#020b14")
        bottom.pack(fill=tk.X, padx=28, pady=(0, 20))

        self.command_entry = tk.Entry(
            bottom,
            font=("Segoe UI", 12),
            bg="#071827",
            fg="#f8fafc",
            insertbackground="#f8fafc",
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground="#1e3a5f"
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)
        self.command_entry.bind("<Return>", lambda event: self.run_manual_command())

        self.mic_button = tk.Button(
            bottom,
            text="LISTEN",
            command=self.listen_and_process,
            bg="#0891b2",
            fg="#ecfeff",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.mic_button.pack(side=tk.LEFT, padx=(10, 0))

        run_button = tk.Button(
            bottom,
            text="RUN",
            command=self.run_manual_command,
            bg="#2563eb",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        run_button.pack(side=tk.LEFT, padx=(10, 0))

        test_button = tk.Button(
            bottom,
            text="TEST",
            command=self.speak_test,
            bg="#0f172a",
            fg="#bae6fd",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        test_button.pack(side=tk.LEFT, padx=(10, 0))

        idle_button = tk.Button(
            bottom,
            text="IDLE",
            command=self.start_idle_mode,
            bg="#0f172a",
            fg="#dbeafe",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        idle_button.pack(side=tk.LEFT, padx=(10, 0))

        exit_button = tk.Button(
            bottom,
            text="EXIT",
            command=self.close_app,
            bg="#7f1d1d",
            fg="#fee2e2",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        exit_button.pack(side=tk.LEFT, padx=(10, 0))

        self.set_state("Idle")
        self.root.after(1000, self.update_clock)
        self.root.after(40, self.animate_loop)

    def update_clock(self):
        now = datetime.datetime.now()
        self.time_label.config(text=now.strftime("%I:%M:%S %p"))
        self.date_label.config(text=now.strftime("%A, %d %B %Y"))
        self.root.after(1000, self.update_clock)

    def set_state(self, state):
        self.state = state
        state_map = {
            "Idle": ("#22d3ee", "READY", "READY", "STABLE"),
            "Listening": ("#38bdf8", "LISTENING", "ACTIVE", "AWAITING INPUT"),
            "Processing": ("#f59e0b", "PROCESSING", "READY", "ANALYZING"),
            "Speaking": ("#a78bfa", "SPEAKING", "ACTIVE", "RESPONDING"),
        }
        color, core_label_text, mic_text, ai_text = state_map.get(state, ("#22d3ee", "READY", "READY", "STABLE"))
        self.status_label.config(text=f"Status: {state}")
        self.core_label.config(text=core_label_text)
        self.indicator.itemconfig(1, fill=color, outline=color)
        self.mic_label.config(text=mic_text)
        self.ai_label.config(text=ai_text)

    def animate_loop(self):
        self.phase += 0.12
        self.core_canvas.delete("all")

        cx = 215
        cy = 215
        radius = 120

        if self.state == "Idle":
            base = 0.7
            ripple = 0.3
            color = "#67e8f9"
        elif self.state == "Listening":
            base = 1.4
            ripple = 1.1
            color = "#38bdf8"
        elif self.state == "Processing":
            base = 1.7
            ripple = 0.9
            color = "#fbbf24"
        else:
            base = 2.1
            ripple = 1.5
            color = "#a78bfa"

        for i in range(7):
            wave = radius + i * 18 + math.sin(self.phase * (2.3 + i * 0.2) + i) * (12 + 10 * ripple)
            ring = self.core_canvas.create_oval(
                cx - wave,
                cy - wave,
                cx + wave,
                cy + wave,
                outline=color,
                width=2 if i % 2 == 0 else 1,
                dash=(4, 8) if self.state in {"Idle", "Listening"} else ()
            )
            self.core_canvas.tag_lower(ring)

        for i in range(18):
            angle = (i / 18) * (2 * math.pi) + self.phase * (0.8 if self.state in {"Listening", "Speaking"} else 0.5)
            dist = radius + 55 + math.sin(self.phase * 2 + i) * (10 + 8 * ripple)
            x = cx + math.cos(angle) * dist
            y = cy + math.sin(angle) * dist
            size = 3 + (i % 3)
            particle_color = "#67e8f9" if self.state in {"Listening", "Processing"} else "#93c5fd"
            self.core_canvas.create_oval(x - size, y - size, x + size, y + size, fill=particle_color, outline="")

        glow_radius = radius * (0.75 + 0.18 * math.sin(self.phase * 2.0)) + 12 * base
        self.core_canvas.create_oval(
            cx - glow_radius,
            cy - glow_radius,
            cx + glow_radius,
            cy + glow_radius,
            outline=color,
            width=2,
            stipple="gray50"
        )

        core_size = 86 + 18 * math.sin(self.phase * 3)
        core_fill = "#7dd3fc" if self.state in {"Listening", "Speaking"} else "#38bdf8"
        self.core_canvas.create_oval(
            cx - core_size,
            cy - core_size,
            cx + core_size,
            cy + core_size,
            fill=core_fill,
            outline="#e0f2fe",
            width=2
        )
        self.core_canvas.create_oval(
            cx - 24,
            cy - 24,
            cx + 24,
            cy + 24,
            fill="#dbeafe",
            outline="#cffafe",
            width=1
        )

        if self.state == "Speaking":
            for i in range(4):
                offset = 16 + i * 18 + math.sin(self.phase * 8 + i) * 12
                self.core_canvas.create_oval(
                    cx - offset,
                    cy - offset,
                    cx + offset,
                    cy + offset,
                    outline="#c084fc",
                    width=1,
                    stipple="gray25"
                )

        self.root.after(40, self.animate_loop)

    def append_log(self, text):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{text}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)

    def speak_test(self):
        self.set_state("Speaking")
        self.assistant.speak("JARVIS desktop assistant is active.")
        self.append_log("System: Voice test played.")
        self.set_state("Idle")

    def run_manual_command(self):
        command = self.command_entry.get().strip()
        if not command:
            self.append_log("System: Please enter a command.")
            return
        self.execute_command(command)

    def execute_command(self, command):
        self.append_log(f"You: {command}")
        self.set_state("Processing")
        try:
            self.assistant.handle_command(command)
        finally:
            self.set_state("Idle")
        self.command_entry.delete(0, tk.END)

    def listen_and_process(self):
        self.set_state("Listening")
        self.append_log("System: Listening for a command...")
        thread = threading.Thread(target=self._listen_and_process_thread, daemon=True)
        thread.start()

    def _listen_and_process_thread(self):
        command = self.assistant.listen()
        if command:
            self.root.after(0, lambda: self.set_state("Processing"))
            self.root.after(0, lambda: self.execute_command(command))
        else:
            self.root.after(0, lambda: self.set_state("Idle"))
            self.root.after(0, lambda: self.append_log("System: No command recognized."))

    def start_idle_mode(self):
        self.set_state("Idle")
        self.append_log("System: JARVIS is waiting for the wake word...")
        thread = threading.Thread(target=self._idle_thread, daemon=True)
        thread.start()

    def _idle_thread(self):
        while not self.stop_event.is_set():
            command = self.assistant.listen("Waiting for wake word...")
            if not command:
                continue
            if "jarvis" in command or "wake up" in command or "hello jarvis" in command:
                self.assistant.speak("Yes, I am listening.")
                self.append_log("System: JARVIS activated by wake word.")
                self.set_state("Listening")
                break

    def close_app(self):
        self.assistant.speak("Goodbye.")
        self.root.destroy()


def main():
    if len(sys.argv) > 1 and sys.argv[1].lower() in {"--cli", "-cli", "cli"}:
        assistant = JarvisAssistant()
        try:
            assistant.run()
        except KeyboardInterrupt:
            assistant.speak("Goodbye!")
        except SystemExit:
            pass
        return

    root = tk.Tk()
    app = JarvisGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


