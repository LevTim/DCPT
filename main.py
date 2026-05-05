import numpy as np
import matplotlib.pyplot as plt
import pywt
from scipy.fft import fft, fftfreq

# =========================
# 1. Генерація даних
# =========================
t = np.linspace(0, 24 * 14, 1000)  # 14 днів

daily_cycle = np.sin(2 * np.pi * t / 24)
weekly_cycle = 0.5 * np.sin(2 * np.pi * t / (24 * 7))
noise = 0.2 * np.random.normal(size=len(t))

energy = 5 + daily_cycle + weekly_cycle + noise

# =========================
# 2. Фур'є аналіз
# =========================
n = len(t)
dt = t[1] - t[0]

yf = fft(energy)
xf = fftfreq(n, dt)

xf_pos = xf[:n // 2]
yf_pos = 2.0 / n * np.abs(yf[:n // 2])

# =========================
# 3. DWT (дискретний вейвлет)
# =========================
wavelet = 'db4'
levels = 4

coeffs = pywt.wavedec(energy, wavelet, level=levels)

# =========================
# 4. CWT (безперервний вейвлет)
# =========================
scales = np.arange(1, 128)
cwt_coeffs, freqs = pywt.cwt(energy, scales, 'morl')

# =========================
# 5. Візуалізація
# =========================
plt.figure(figsize=(14, 12))

# --- 1. Сигнал ---
plt.subplot(5, 1, 1)
plt.plot(t, energy, color='black')
plt.title("Часовий ряд споживання енергії")
plt.ylabel("Потужність")

# --- 2. FFT ---
plt.subplot(5, 1, 2)
plt.plot(xf_pos, yf_pos, color='red')
plt.title("Фур'є спектр (частоти)")
plt.xlim(0, 0.1)
plt.ylabel("Амплітуда")

# --- 3. DWT рівні ---
plt.subplot(5, 1, 3)
for i, coeff in enumerate(coeffs):
    plt.plot(coeff, label=f"L{i}")
plt.title("DWT: розклад на рівні")
plt.legend()

# --- 4. Апроксимація vs сигнал ---
reconstructed = pywt.waverec(coeffs, wavelet)

plt.subplot(5, 1, 4)
plt.plot(t, energy, label="Оригінал", alpha=0.5)
plt.plot(t, reconstructed[:len(t)], label="Відновлений")
plt.title("Перевірка реконструкції сигналу")
plt.legend()

# --- 5. CWT (time-frequency) ---
plt.subplot(5, 1, 5)
plt.imshow(
    cwt_coeffs,
    extent=[t.min(), t.max(), freqs.min(), freqs.max()],
    cmap='jet',
    aspect='auto'
)
plt.title("CWT: час-частота")
plt.ylabel("Частота")
plt.xlabel("Час")

plt.tight_layout()
plt.show()