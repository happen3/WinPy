import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

# Constants
CW_USEDEFAULT = 0x80000000
WS_OVERLAPPEDWINDOW = 0xCF0000
WM_DESTROY = 0x0002
WM_PAINT = 0x000F
WM_CLOSE = 0x0010


# Utility function to convert Python string to LPCWSTR
def to_lpcwstr(string):
    return ctypes.c_wchar_p(string)


# Utility function to register a window class
def RegisterWdnClass(class_name, wndproc):
    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int)

    class WNDCLASSEX(ctypes.Structure):
        _fields_ = [
            ("cbSize", wintypes.UINT),
            ("style", wintypes.UINT),
            ("lpfnWndProc", WNDPROC),
            ("cbClsExtra", wintypes.INT),
            ("cbWndExtra", wintypes.INT),
            ("hInstance", wintypes.HINSTANCE),
            ("hIcon", wintypes.HICON),
            ("hCursor", wintypes.HCURSOR),
            ("hbrBackground", wintypes.HBRUSH),
            ("lpszMenuName", wintypes.LPCWSTR),
            ("lpszClassName", wintypes.LPCWSTR),
            ("hIconSm", wintypes.HICON)
        ]

    hInstance = kernel32.GetModuleHandleW(None)
    wnd_class = WNDCLASSEX()
    wnd_class.cbSize = ctypes.sizeof(WNDCLASSEX)
    wnd_class.style = 0
    wnd_class.lpfnWndProc = WNDPROC(wndproc)
    wnd_class.cbClsExtra = 0
    wnd_class.cbWndExtra = 0
    wnd_class.hInstance = hInstance
    wnd_class.hIcon = user32.LoadIconW(0, 1)
    wnd_class.hCursor = user32.LoadCursorW(0, 32512)
    wnd_class.hbrBackground = gdi32.GetStockObject(5)
    wnd_class.lpszMenuName = None
    wnd_class.lpszClassName = to_lpcwstr(class_name)
    wnd_class.hIconSm = user32.LoadIconW(0, 1)

    if not user32.RegisterClassExW(ctypes.byref(wnd_class)):
        raise ctypes.WinError()

    return hInstance


# Utility function to create a window
def CreateWindow(class_name, window_name, wndproc):
    hInstance = RegisterWdnClass(class_name, wndproc)
    hwnd = user32.CreateWindowExW(
        0,
        to_lpcwstr(class_name),
        to_lpcwstr(window_name),
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        800,
        600,
        None,
        None,
        hInstance,
        None
    )
    if not hwnd:
        raise ctypes.WinError()
    return hwnd


# Utility function to run the message loop
def message_loop():
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
