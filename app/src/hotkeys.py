from pynput import keyboard


class HotkeyManager:
    def __init__(self, on_start, on_stop, on_pause):
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_pause = on_pause
        self.listener = None

    def start(self):
        hotkeys = {
            '<ctrl>+<shift>+r': self.on_start,
            '<ctrl>+<shift>+s': self.on_stop,
            '<ctrl>+<shift>+p': self.on_pause,
        }
        self.listener = keyboard.GlobalHotKeys(hotkeys)
        self.listener.start()

    def stop(self):
        if self.listener:
            self.listener.stop()
