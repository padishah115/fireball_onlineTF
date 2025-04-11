import numpy as np
import matplotlib.pyplot as plt

# Define the decay constant tau based on half-life
tau = np.log(2) * 5.4  # 5.4 is the half-life in hours

# Time vector from 1 to 24 hours
hours = np.arange(0, 24, 1)

# Number of doses administered every 4 hours
doses = 5
dose_interval = 5.5  # hours

# Initialize the total concentration array with zeros
y = np.zeros_like(hours, dtype=np.float64)

# Define exponential decay function
def decay(x, tau):
    return np.exp(-x / tau)

# Superimpose decayed contributions of each dose over time
for dose in range(doses):
    dose_time = dose * dose_interval
    time_since_dose = hours - dose_time

    # Apply decay only where time_since_dose is positive
    mask = time_since_dose >= 0
    y[mask] += decay(time_since_dose[mask], tau)

# Plot the resulting dose accumulation
plt.plot(hours, y, marker='o')
plt.ylabel("Total concentration in system (arbitrary units)")
plt.xlabel("Hours")
plt.title("Exponential Decay of Repeated Doses Every 4 Hours")
plt.grid(True)
plt.show()
