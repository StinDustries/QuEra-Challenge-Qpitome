import numpy as np
import matplotlib.pyplot as plt
from tsim import Circuit

# ── Parameters ────────────────────────────────────────────────────────────────
D              = 3
LOGICAL_ANGLE  = 0.1    # theta_logical in units of pi
SHOTS          = 100_0000

def physical_angle(logical_angle_in_pi: float, num_physical_rotations: int) -> float:
    assert num_physical_rotations % 2 == 1 and num_physical_rotations > 0
    sign = -1 if (num_physical_rotations + 1) % 4 == 0 else 1
    logical_angle_in_rad = logical_angle_in_pi * np.pi
    x = np.tan(logical_angle_in_rad / 2) ** (1 / num_physical_rotations)
    theta_phys = 2 * np.arctan(x)
    return float(sign * theta_phys / np.pi)

PHYSICAL_ANGLE = physical_angle(LOGICAL_ANGLE, D)  # R_Z angle per qubit on Z_L support
N_DATA         = D * D               # 9
N_BLOCK        = 2 * N_DATA - 1      # 17 (data + syndrome ancilla)
OFFSET         = N_BLOCK             # block 1 starts here

# ── Qubit helpers ─────────────────────────────────────────────────────────────
def data(block):     return list(range(block*OFFSET, block*OFFSET + N_DATA))
def left_col(block): return [block*OFFSET + r*D for r in range(D)]
def top_row(block):  return [block*OFFSET + c   for c in range(D)]

# ── Circuit ───────────────────────────────────────────────────────────────────
def build_circuit(physical_angle):
    lines = []

    # All 34 qubits to |+>  (data + syndrome ancilla on both blocks)
    all_q = list(range(2 * N_BLOCK+1))
    lines.append(f"RX {' '.join(map(str, all_q))}")
    lines.append("TICK")

    # STAR injection: R_Z on ancilla left column only
    for q in left_col(1):            # {17, 20, 23}
        lines.append(f"R_Z({physical_angle}) {q}")
    
    lines.append("TICK")

    # Transversal CNOT main -> ancilla (data qubits only)
    pairs = " ".join(f"{m} {a}" for m, a in zip(data(0), data(1)))
    lines.append(f"CNOT {pairs}")
    lines.append("TICK")

    # Measure ancilla data in Z basis
    lines.append(f"MZ {' '.join(map(str, data(1)))}")
    lines.append("TICK")

    # for q in left_col(0):            # {17, 20, 23}
    #     lines.append(f"R_Z({-1 * physical_angle}) {q}")



    # Logical X observable on main: parity of top-row X measurements
    lines.append(f"MPP {'*'.join(f'X{q}' for q in top_row(0))}")
    lines.append("OBSERVABLE_INCLUDE(0) rec[-1]")

    return Circuit("\n".join(lines))

# ── Single-angle run (original behaviour) ────────────────────────────────────

# lines = [
#     f"RX 0",
#     f"R_Z({LOGICAL_ANGLE/D}) 0",
#     f"MX 0"
# ]
# newCirc = Circuit("\n".join(lines))
# perfCube = newCirc.compile_sampler(seed=42).sample(shots=SHOTS)

# p0_perf = np.mean(perfCube==0)
# p1_perf = np.mean(perfCube==1)
# print(f" perfcube P(logical X = 0):    {p0_perf:.4f}  (expect 1.0 for noiseless)")
# print(f" perfcube  P(logical X = 1):    {p1_perf:.4f}  (logical error rate)")

circuit = build_circuit(LOGICAL_ANGLE / D)
raw     = circuit.compile_sampler(seed=42).sample(shots=SHOTS)

anc_parity = np.bitwise_xor.reduce(raw[:, 0:N_DATA].astype(int), axis=1)
mpp_result = raw[:, N_DATA].astype(int)

mask         = anc_parity == 0
postselected = mpp_result[mask]

print(f"STAR gate teleportation  |  d={D} surface code  |  noiseless")
print(f"  Qubits: {2*N_BLOCK} total ({N_BLOCK} per block: {N_DATA} data + syndrome ancilla)")
print(f"  theta_logical  = {LOGICAL_ANGLE}*pi")
print(f"  theta_physical = {LOGICAL_ANGLE/D}*pi  (= theta_L / d)")
print()
print(f"  Total shots:         {SHOTS:,}")
print(f"  Postselected (p=0):  {mask.sum():,}  ({mask.mean():.1%}, expected ~50%)")
if len(postselected) > 0:
    p0 = np.mean(postselected == 0)
    p1 = np.mean(postselected == 1)
    print(f"  P(logical X = 0):    {p0:.4f}  (expect 1.0 for noiseless)")
    print(f"  P(logical X = 1):    {p1:.4f}  (logical error rate)")
    # print(f"overlap with perfect rotation = {np.abs(p0*p0_perf + p1*p1_perf)**2}")

# ── Sweep over logical angles ─────────────────────────────────────────────────
print("\nSweeping logical angles for plot...")

logical_angles = np.linspace(0.001, 1, 40)   # theta_L in units of pi
error_rates = []

for theta_L in logical_angles:
    theta_phys = theta_L / D
    circ = build_circuit(theta_phys)
    raw_s = circ.compile_sampler(seed=42).sample(shots=SHOTS)

    ap = np.bitwise_xor.reduce(raw_s[:, 0:N_DATA].astype(int), axis=1)
    mp = raw_s[:, N_DATA].astype(int)

    ps = mp[ap == 0]
    # print(ps)
    p0 = np.sum(ps == 0)
    p1 = np.sum(ps == 1)
    norm_factor = 1/np.sqrt(p0**2 + p1**2)
    p0 *= norm_factor
    p1 *= norm_factor



    # error_rates.append(np.mean(ps == 1) if len(ps) > 0 else np.nan)

    lines = [
        f"RX 0",
        f"R_Z({theta_L/D}) 0",
        f"MX 0"
    ]
    newCirc = Circuit("\n".join(lines))
    perfCube = newCirc.compile_sampler(seed=42).sample(shots=SHOTS)

    p0_perf = np.mean(perfCube==0) 
    p1_perf = np.mean(perfCube==1) 
    norm_factor = 1/np.sqrt(p0_perf**2 + p1_perf**2)
    p0_perf *= norm_factor
    p1_perf *= norm_factor
    # print(f"overlap with perfect rotation = {np.abs(p1*p0_perf + p0*p1_perf)**2}")
    overlap = np.abs(p0*p0_perf + p1*p1_perf)**2
    # print(overlap>1)
    error_rates.append(overlap)


error_rates = np.array(error_rates)

# ── Plot ──────────────────────────────────────────────────────────────────────
# fig, ax = plt.subplots(figsize=(8, 5))
plt.scatter(logical_angles, error_rates, s=40)
plt.xlabel("Logical angle (units of pi)", fontsize=11)
plt.ylabel("Logical error rate", fontsize=11)
plt.title(
    f"STAR Gate Teleportation  |  d={D} surface code  |  noiseless\n",
    fontsize=11
)
# plt.grid(True, alpha=0.3)
plt.yscale('log')
plt.show()

# plt.tight_layout()
# plt.savefig("star_graph_pt3.png", dpi=150, bbox_inches="tight")
# plt.show()