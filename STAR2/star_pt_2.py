import tsim
import numpy as np
import matplotlib.pyplot as plt
import pymatching
import csv
import os
import time

CSV_FILE = "results.csv"
FLUSH_EVERY = 1      # how often to force write to disk
SHOTS = 1_000_000

def physical_angle(logical_angle_in_pi: float, num_physical_rotations: int) -> float:
    assert num_physical_rotations % 2 == 1 and num_physical_rotations > 0
    sign = -1 if (num_physical_rotations + 1) % 4 == 0 else 1
    logical_angle_in_rad = logical_angle_in_pi * np.pi
    x = np.tan(logical_angle_in_rad / 2) ** (1 / num_physical_rotations)
    theta_phys = 2 * np.arctan(x)
    return float(sign * theta_phys / np.pi)


def run_single_experiment(dist, logical_angle):
    p_angle = physical_angle(logical_angle, dist)

    with open(f"assets/star_circuits/star_d={dist}.stim", "r") as f:
        template = f.read()

    stim_circuit_text = template.format(
        physical_angle=f"{p_angle:.10f}",
        logical_angle=f"{logical_angle:.10f}",
    )

    with open("temp_circuit.stim", "w") as f:
        f.write(stim_circuit_text)

    c = tsim.Circuit.from_file("temp_circuit.stim")
    sampler = c.compile_detector_sampler()

    detector_error_model = c.detector_error_model()
    matcher = pymatching.Matching.from_detector_error_model(detector_error_model)

    detections, observations = sampler.sample(SHOTS, separate_observables=True)
    predictions = matcher.decode_batch(detections)

    # post-select on perfect stabilizers
    good = [
        i for i in range(len(detections))
        if not any(detections[i][:(3*(dist**2 - 1))])
    ]

    num_errors = 0
    for idx in good:
        if not np.array_equal(observations[idx], predictions[idx]):
            num_errors += 1

    error = num_errors / len(good)
    return error / dist


def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "distance", "logical_angle", "error_rate"])


def append_result(writer, dist, logical_angle, error_rate):
    writer.writerow([time.time(), dist, logical_angle, error_rate])


def plot_from_csv():
    import collections

    data = collections.defaultdict(dict)

    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = int(row["distance"])
            a = float(row["logical_angle"])
            e = float(row["error_rate"])
            data[d][a] = e

    plt.figure(figsize=(7,5))
    for d, rates in data.items():
        x = sorted(rates.keys())
        y = [rates[p] for p in x]
        plt.plot(x, y, marker='o', label=f"d={d}")

    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel("Rotation")
    plt.ylabel("Logical error rate / distance")
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.legend()
    plt.show()


# ================= MAIN LOOP =================

init_csv()

flush_counter = 0

try:
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        while True:
            for dist in [3, 5, 7]:
                for x in range(0, 12):
                    logical_angle = 0.8 / (2 ** x)

                    print(f"d={dist}  angle={logical_angle}")

                    err = run_single_experiment(dist, logical_angle)

                    append_result(writer, dist, logical_angle, err)
                    flush_counter += 1

                    if flush_counter % FLUSH_EVERY == 0:
                        f.flush()
                        os.fsync(f.fileno())
                        print("Flushed to disk.")

except KeyboardInterrupt:
    print("\n\nCtrl+C detected. Plotting accumulated results...\n")
    plot_from_csv()