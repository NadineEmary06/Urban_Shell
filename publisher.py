"""Fake vehicle data publisher: sends one JSON packet over UDP at 10 Hz."""
import json
import math
import random
import socket
import time

HOST, PORT = "127.0.0.1", 5005
RATE_HZ = 10
PERIOD = 1.0 / RATE_HZ


def make_packet(t0, seq, soc):
    t = time.time() - t0
    speed = 25 + 20 * math.sin(t / 5)                 # km/h, slow wave
    lv_voltage = 13.8 + random.uniform(-0.15, 0.15)   # V
    motor_current = max(0.0, speed * 0.9 + random.uniform(-2, 2))  # A
    fault = 0
    if 20 < t % 60 < 23:                              # fake fault every minute
        fault = 3                                     # e.g. over-temperature
    return {
        "seq": seq,
        "time": round(time.time(), 3),
        "speed_kmh": round(speed, 1),
        "lv_voltage_v": round(lv_voltage, 2),
        "soc_pct": round(soc, 1),
        "motor_current_a": round(motor_current, 1),
        "fault_state": fault,
    }


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    t0 = time.time()
    soc, seq = 95.0, 0
    next_t = time.perf_counter()
    print(f"Publishing fake vehicle data at {RATE_HZ} Hz to {HOST}:{PORT} (Ctrl+C to stop)")
    try:
        while True:
            pkt = make_packet(t0, seq, soc)
            sock.sendto(json.dumps(pkt).encode(), (HOST, PORT))
            seq += 1
            soc = max(0.0, soc - 0.005)               # battery slowly drains
            next_t += PERIOD                          # fixed schedule, no drift
            time.sleep(max(0.0, next_t - time.perf_counter()))
    except KeyboardInterrupt:
        print("Publisher stopped.")


if __name__ == "__main__":
    main()
