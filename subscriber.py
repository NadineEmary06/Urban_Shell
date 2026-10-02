"""Telemetry subscriber: receives packets, parses variables, prints and logs to CSV."""
import csv
import json
import socket
import time

HOST, PORT = "0.0.0.0", 5005
CSV_FILE = "telemetry_log.csv"
TIMEOUT_S = 0.5                                       # stale data limit
FAULTS = {0: "OK", 1: "CAN timeout", 2: "Throttle fault", 3: "Over-temperature"}


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    sock.settimeout(TIMEOUT_S)
    with open(CSV_FILE, "w", newline="") as f:
        log = csv.writer(f)
        log.writerow(["time", "seq", "speed_kmh", "lv_voltage_v",
                      "soc_pct", "motor_current_a", "fault_state"])
        print("Listening on port", PORT, "(Ctrl+C to stop)")
        try:
            while True:
                try:
                    data, _ = sock.recvfrom(1024)
                except socket.timeout:
                    print("NO DATA (telemetry link lost?)")
                    continue
                pkt = json.loads(data.decode())
                # parse into separate variables
                t = pkt["time"]
                seq = pkt["seq"]
                speed = pkt["speed_kmh"]
                lv_v = pkt["lv_voltage_v"]
                soc = pkt["soc_pct"]
                i_motor = pkt["motor_current_a"]
                fault = pkt["fault_state"]
                print(f"#{seq:05d} | speed {speed:5.1f} km/h | LV {lv_v:5.2f} V | "
                      f"SOC {soc:5.1f} % | I_motor {i_motor:5.1f} A | "
                      f"fault {fault} ({FAULTS.get(fault, '?')})")
                log.writerow([t, seq, speed, lv_v, soc, i_motor, fault])
                f.flush()
        except KeyboardInterrupt:
            print("Subscriber stopped. Log saved to", CSV_FILE)


if __name__ == "__main__":
    main()
