import importlib


def check_module(name):
    try:
        importlib.import_module(name)
        return True
    except Exception:
        return False


def main():
    required_modules = ["pyttsx3", "speech_recognition"]
    missing = []

    for module_name in required_modules:
        if not check_module(module_name):
            missing.append(module_name)

    if missing:
        print("Missing dependencies:", ", ".join(missing))
        print("Install them with: pip install pyttsx3 SpeechRecognition")
        return

    print("Jarvis environment check passed.")
    print("All required modules are installed and ready.")


if __name__ == "__main__":
    main()
