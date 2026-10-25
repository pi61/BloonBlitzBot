import ctypes
import os
import re
from ctypes import wintypes
from dataclasses import dataclass


GAME_TITLE_PARTS = ("bloon", "blitz")
MONITOR_DEFAULTTONEAREST = 2
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SM_CXSCREEN = 0
SM_CYSCREEN = 1
GOOGLE_PLAY_GAMES_PROCESSES = {"crosvm.exe", "googleplaygames.exe"}


class MonitorInfo(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
    ]


@dataclass(frozen=True)
class DisplayInfo:
    game_window_title: str
    primary_screen_resolution: tuple[int, int]
    game_monitor_resolution: tuple[int, int]
    window_position: tuple[int, int]
    window_size: tuple[int, int]
    client_position: tuple[int, int]
    game_resolution: tuple[int, int]


def _normalized_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.casefold())


def get_display_info() -> DisplayInfo:
    if os.name != "nt":
        raise OSError("Display and window inspection is only supported on Windows.")

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    set_thread_dpi_context = user32.SetThreadDpiAwarenessContext
    set_thread_dpi_context.argtypes = [wintypes.HANDLE]
    set_thread_dpi_context.restype = wintypes.HANDLE
    previous_dpi_context = set_thread_dpi_context(ctypes.c_void_p(-4))
    if not previous_dpi_context:
        raise ctypes.WinError(ctypes.get_last_error())

    try:
        return _get_display_info(user32)
    finally:
        if not set_thread_dpi_context(previous_dpi_context):
            raise ctypes.WinError(ctypes.get_last_error())


def _get_display_info(user32) -> DisplayInfo:
    hwnd_type = wintypes.HWND
    callback_type = ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        hwnd_type,
        wintypes.LPARAM,
    )

    user32.EnumWindows.argtypes = [callback_type, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.IsWindowVisible.argtypes = [hwnd_type]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.GetWindowTextLengthW.argtypes = [hwnd_type]
    user32.GetWindowTextLengthW.restype = ctypes.c_int
    user32.GetWindowTextW.argtypes = [hwnd_type, wintypes.LPWSTR, ctypes.c_int]
    user32.GetWindowTextW.restype = ctypes.c_int
    user32.GetWindowRect.argtypes = [hwnd_type, ctypes.POINTER(wintypes.RECT)]
    user32.GetWindowRect.restype = wintypes.BOOL
    user32.GetClientRect.argtypes = [hwnd_type, ctypes.POINTER(wintypes.RECT)]
    user32.GetClientRect.restype = wintypes.BOOL
    user32.ClientToScreen.argtypes = [hwnd_type, ctypes.POINTER(wintypes.POINT)]
    user32.ClientToScreen.restype = wintypes.BOOL
    user32.GetSystemMetrics.argtypes = [ctypes.c_int]
    user32.GetSystemMetrics.restype = ctypes.c_int
    user32.MonitorFromWindow.argtypes = [hwnd_type, wintypes.DWORD]
    user32.MonitorFromWindow.restype = wintypes.HMONITOR
    user32.GetMonitorInfoW.argtypes = [
        wintypes.HMONITOR,
        ctypes.POINTER(MonitorInfo),
    ]
    user32.GetMonitorInfoW.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = [
        hwnd_type,
        ctypes.POINTER(wintypes.DWORD),
    ]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPWSTR,
        ctypes.POINTER(wintypes.DWORD),
    ]
    kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    titled_windows: list[tuple[int, str, int]] = []

    @callback_type
    def collect_windows(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        title_length = user32.GetWindowTextLengthW(hwnd)
        if title_length == 0:
            return True
        title_buffer = ctypes.create_unicode_buffer(title_length + 1)
        user32.GetWindowTextW(hwnd, title_buffer, len(title_buffer))
        title = title_buffer.value
        normalized_title = _normalized_title(title)
        if all(part in normalized_title for part in GAME_TITLE_PARTS):
            process_id = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            titled_windows.append((hwnd, title, process_id.value))
        return True

    ctypes.set_last_error(0)
    if not user32.EnumWindows(collect_windows, 0):
        error_code = ctypes.get_last_error()
        raise ctypes.WinError(error_code)

    matching_windows: list[tuple[int, str]] = []
    for hwnd, title, process_id in titled_windows:
        process_handle = kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION,
            False,
            process_id,
        )
        if not process_handle:
            continue
        try:
            image_path = ctypes.create_unicode_buffer(32768)
            path_length = wintypes.DWORD(len(image_path))
            if not kernel32.QueryFullProcessImageNameW(
                process_handle,
                0,
                image_path,
                ctypes.byref(path_length),
            ):
                continue
            process_name = image_path.value.rsplit("\\", 1)[-1].casefold()
            if process_name in GOOGLE_PLAY_GAMES_PROCESSES:
                matching_windows.append((hwnd, title))
        finally:
            kernel32.CloseHandle(process_handle)

    if not matching_windows:
        raise LookupError(
            "Could not find a visible Bloon Blitz window hosted by Google Play "
            "Games. Open Bloon Blitz, then try again."
        )
    if len(matching_windows) > 1:
        titles = ", ".join(title for _, title in matching_windows)
        raise LookupError(
            "Found multiple Bloon Blitz windows; unable to select one safely: "
            + titles
        )

    hwnd, title = matching_windows[0]
    window_rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(window_rect)):
        raise ctypes.WinError(ctypes.get_last_error())

    client_rect = wintypes.RECT()
    if not user32.GetClientRect(hwnd, ctypes.byref(client_rect)):
        raise ctypes.WinError(ctypes.get_last_error())

    client_origin = wintypes.POINT(0, 0)
    if not user32.ClientToScreen(hwnd, ctypes.byref(client_origin)):
        raise ctypes.WinError(ctypes.get_last_error())

    monitor = user32.MonitorFromWindow(hwnd, MONITOR_DEFAULTTONEAREST)
    if not monitor:
        raise ctypes.WinError(ctypes.get_last_error())
    monitor_info = MonitorInfo()
    monitor_info.cbSize = ctypes.sizeof(MonitorInfo)
    if not user32.GetMonitorInfoW(monitor, ctypes.byref(monitor_info)):
        raise ctypes.WinError(ctypes.get_last_error())

    monitor_rect = monitor_info.rcMonitor
    return DisplayInfo(
        game_window_title=title,
        primary_screen_resolution=(
            user32.GetSystemMetrics(SM_CXSCREEN),
            user32.GetSystemMetrics(SM_CYSCREEN),
        ),
        game_monitor_resolution=(
            monitor_rect.right - monitor_rect.left,
            monitor_rect.bottom - monitor_rect.top,
        ),
        window_position=(window_rect.left, window_rect.top),
        window_size=(
            window_rect.right - window_rect.left,
            window_rect.bottom - window_rect.top,
        ),
        client_position=(client_origin.x, client_origin.y),
        game_resolution=(
            client_rect.right - client_rect.left,
            client_rect.bottom - client_rect.top,
        ),
    )
