from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt

# Load IBM Quantum account
service = QiskitRuntimeService()

# Choose least busy *real* backend or fallback to simulator
try:
    backend = service.least_busy(operational=True, simulator=False)
except Exception as e:
    print(f"Error finding least busy backend: {e}")
    backend = service.get_backend('ibmq_qasm_simulator')

# Define the 3-qubit quantum circuit
qc = QuantumCircuit(3, 3)
qc.x(2)
qc.h(0)
qc.h(1)
qc.cx(0, 1)
qc.x(1)
qc.ccx(0, 1, 2)
qc.x(1)
qc.measure([0, 1, 2], [0, 1, 2])

# Transpile the circuit
qc_transpiled = transpile(qc, backend=backend)

# Create a session and run the sampler
with Session(backend=backend) as session:
    sampler = Sampler()  # Instantiate Sampler without session
    job = sampler.run([qc_transpiled], shots=8192)  # No session needed in `run()`
    print(f"Job ID: {job.job_id()}")
    result = job.result()

# Print counts for each public result
for idx, pub_result in enumerate(result):
    # Access counts in a more general way (depending on how it's structured)
    try:
        # If it's a 'Sampler' result, we access 'counts' directly
        counts = pub_result.data.c.get_counts()  # Adjust this based on how the data is structured
        print(f" > Counts for pub {idx}: {counts}")
    except KeyError as e:
        print(f" > Error accessing counts for pub {idx}: {e}")

# Optionally, if you want to visualize the overall counts of all public results:
all_counts = {}
for pub_result in result:
    try:
        counts = pub_result.data.c.get_counts()  # Accessing counts directly
        for bitstring, count in counts.items():
            if bitstring in all_counts:
                all_counts[bitstring] += count
            else:
                all_counts[bitstring] = count
    except KeyError as e:
        print(f" > Error merging counts for pub result: {e}")

# Plot a histogram of the combined counts
plot_histogram(all_counts, title="Combined Quantum Circuit Output Counts")
plt.xlabel("Bitstrings (q₂ q₁ q₀)")
plt.ylabel("Count")
plt.show()
