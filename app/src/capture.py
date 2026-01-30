try:
    import win32gui
except Exception:
    win32gui = None


def list_windows():
    if not win32gui:
        return []

    windows = []

    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                rect = win32gui.GetWindowRect(hwnd)
                windows.append((title, rect))

    win32gui.EnumWindows(enum_handler, None)
    return windows


def get_window_rect(title):
    if not win32gui:
        return None
    for t, rect in list_windows():
        if t == title:
            return rect
    return None
