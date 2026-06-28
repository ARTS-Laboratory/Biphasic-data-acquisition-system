import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import labellines

# set default fonts and plot colors
plt.rcParams.update({'text.usetex': True})
plt.rcParams.update({'image.cmap': 'viridis'})
plt.rcParams.update({'font.serif':['Times New Roman', 'Times', 'DejaVu Serif',
 'Bitstream Vera Serif', 'Computer Modern Roman', 'New Century Schoolbook',
 'Century Schoolbook L',  'Utopia', 'ITC Bookman', 'Bookman', 
 'Nimbus Roman No9 L', 'Palatino', 'Charter', 'serif']})
plt.rcParams.update({'font.family':'serif'})
plt.rcParams.update({'font.size': 9})
plt.rcParams.update({'mathtext.rm': 'serif'})
plt.rcParams.update({'mathtext.fontset': 'custom'}) # I don't think I need this as its set to 'stixsans' above.
cc = plt.rcParams['axes.prop_cycle'].by_key()['color']
plt.close('all')

file_names = ['1ohm.txt', '10ohm.txt', '100ohm.txt', '680ohm.txt', '3p3kohm.txt', '7p5kohm.txt', '15kohm.txt', '56kohm.txt',
              '100kohm.txt', '330kohm.txt', '680kohm.txt', '1p5Mohm.txt', '3p3Mohm.txt']
labels = ['1 $\Omega$', '10 $\Omega$', '100 $\Omega$', '680 $\Omega$', '3.3 k$\Omega$', '7.5 k$\Omega$', '15 k$\Omega$', '56 k$\Omega$',
        '100 k$\Omega$', '330 k$\Omega$', '680 k$\Omega$', '1.5 M$\Omega$', '3.3 M$\Omega$']

resistances = [1, 10, 100, 680, 3300, 7500, 15000, 56000, 100000, 330000, 680000, 1500000, 3300000]  # in ohms

drift_intensities = []

plt.figure(figsize=(10, 10))

ax = plt.axes()
ax.set_xlabel('time (ms)')
ax.set_ylabel('resistance (ohms)')

for i, file_name in enumerate(file_names):
    file_path = os.path.join('./data', file_name)
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                try:
                    data.append([float(part) for part in parts])
                except ValueError:
                    continue

    if data:
        data = np.array(data)
        time_ms = data[:, 0].reshape(-1, 1)
        resistance_ohms = -data[:, 1]

        poly = PolynomialFeatures(degree=2)
        time_poly = poly.fit_transform(time_ms)
        model = LinearRegression().fit(time_poly, resistance_ohms)
        trend = model.predict(time_poly)

        drift_intensity = model.coef_[1]  # coefficient of the linear term
        drift_intensities.append(drift_intensity)

        plt.plot(time_ms, resistance_ohms, label=f'{labels[i]}')
        plt.plot(time_ms, trend, linestyle='--', label=f'Trend {labels[i]}: a={model.coef_[2]:.2e}, b={model.coef_[1]:.2e}')

plt.title('Drift Tests - 120s - 5Hz')
plt.legend()
plt.tight_layout()
plt.savefig('./figs/drift_testing.png', dpi=300)
plt.show()

resistances = np.array(resistances).reshape(-1, 1)
drift_intensities = np.array(drift_intensities).reshape(-1, 1)

model_drift = LinearRegression().fit(resistances, drift_intensities)
predicted_drift = model_drift.predict(resistances)

plt.figure(figsize=(5, 5))
plt.scatter(resistances, drift_intensities, color='blue', label='observed drift intensities')
plt.plot(resistances, predicted_drift, color='red', linestyle='--', label=f'modeled drift intensity: a={model_drift.coef_[0][0]:.2e}, b={model_drift.intercept_[0]:.2e}')
plt.xscale('log')
plt.xlabel('resistance (ohms)')
plt.ylabel('drift intensity')
plt.legend()
plt.tight_layout()
plt.savefig('./figs/drift_intensity_model.png', dpi=300)
plt.show()

# drift intensity as a function of resistance using an exponential model
exp_resistances = np.array(resistances).reshape(-1, 1)
exp_drift_intensities = np.array(drift_intensities).reshape(-1, 1)

# transform to fit an exponential model
log_resistances = np.log(exp_resistances)

exp_model_drift = LinearRegression().fit(log_resistances, exp_drift_intensities)
exp_predicted_drift = exp_model_drift.predict(log_resistances)

exp_a = np.exp(exp_model_drift.intercept_[0])
exp_b = exp_model_drift.coef_[0][0]

plt.figure(figsize=(5, 5))
plt.scatter(exp_resistances, exp_drift_intensities, color='blue', label='obsered drift intensities')
plt.plot(exp_resistances, exp_predicted_drift, color='red', linestyle='--', label=f'modeled drift intensity: a={exp_a:.2e}, b={exp_b:.2e}')
plt.xscale('log')
plt.xlabel('resistance (ohms)')
plt.ylabel('drift Intensity')
plt.legend()
plt.tight_layout()
plt.savefig('./figs/exp_drift_intensity_model.png', dpi=300)
plt.show()


print("Model parameters:")
print(f"a = {exp_a}")
print(f"b = {exp_b}")
