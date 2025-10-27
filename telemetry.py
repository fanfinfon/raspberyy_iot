import psutil

def get_cpu_temp():
    """Return CPU temperature in °C."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read()) / 1000.0, 1)
    except FileNotFoundError:
        return None

def get_telemetry():
    """Return system telemetry: CPU temp, usage %, net in/out (KB)."""
    cpu_temp = get_cpu_temp()
    cpu_usage = psutil.cpu_percent(interval=None)

    net = psutil.net_io_counters()
    net_in = round(net.bytes_recv / 1024.0, 2)
    net_out = round(net.bytes_sent / 1024.0, 2)

    return {
        "cpu_temp": cpu_temp,
        "cpu_usage": cpu_usage,
        "net_in": net_in,
        "net_out": net_out
    }
