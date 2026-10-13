import time
import json
from datetime import datetime, timezone
import win32gui
import win32process
import psutil

def get_active_app():
    """Returns (process_name, window_title) for the foreground window."""
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return ("unknown", "")
    title = win32gui.GetWindowText(hwnd)
    pid = win32process.GetWindowThreadProcessId(hwnd)[1]
    try:
        proc_name = psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        proc_name = "unknown"
    return (proc_name, title)

def heartbeat_loop(events_file="events.jsonl", interval=10):
    """
    Polls the foreground window every `interval` seconds.
    Appends a JSON line per state change.
    Each event: {start, end, app, title}
    """
    current_app, current_title = get_active_app()
    start = datetime.now(timezone.utc)
    
    with open(events_file, "a") as f:
        while True:
            time.sleep(interval)
            new_app, new_title = get_active_app()
            
            if (new_app, new_title) != (current_app, current_title):
                # Close current event
                end = datetime.now(timezone.utc)
                event = {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "app": current_app,
                    "title": current_title,
                    "duration_s": (end - start).total_seconds()
                }
                f.write(json.dumps(event) + "\n")
                f.flush()
                
                # Start new event
                current_app, current_title = new_app, new_title
                start = end

# Run it
heartbeat_loop(interval=10)