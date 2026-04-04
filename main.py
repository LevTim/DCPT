import pandas as pd
import numpy as np
import time

# Генеруємо тестовий набір (1 млн записів)
np.random.seed(42)
rows = 1_000_000

df = pd.DataFrame({
    'solar_kwh': np.random.uniform(10, 100, rows),
    'wind_kwh': np.random.uniform(20, 150, rows),
    'fossil_kwh': np.random.uniform(50, 300, rows),
    'loss_factor': np.random.uniform(0.01, 0.05, rows)
})

# Кількість повторів для точності
runs = 5

# =========================
# 1. Стандартний метод
# =========================
standard_times = []

for _ in range(runs):
    start = time.time()

    df['net_energy_standard'] = (
        (df['solar_kwh'] * 1.1 +
         df['wind_kwh'] * 0.9 +
         df['fossil_kwh'] * 0.8)
        - (df['loss_factor'] * df['fossil_kwh'])
    ) / (1 + df['loss_factor'])

    standard_times.append(time.time() - start)

# =========================
# 2. eval() + numexpr
# =========================
eval_times = []

for _ in range(runs):
    start = time.time()

    df.eval(
        'net_energy_eval = ((solar_kwh * 1.1 + wind_kwh * 0.9 + fossil_kwh * 0.8) - (loss_factor * fossil_kwh)) / (1 + loss_factor)',
        engine='numexpr',
        inplace=True
    )

    eval_times.append(time.time() - start)

# =========================
# Результати
# =========================
avg_standard = sum(standard_times) / runs
avg_eval = sum(eval_times) / runs

print(f"Середній час (стандартний метод): {avg_standard:.5f} секунд")
print(f"Середній час (eval + numexpr): {avg_eval:.5f} секунд")

# =========================
# Перевірка правильності
# =========================
difference = np.abs(df['net_energy_standard'] - df['net_energy_eval']).max()
print(f"Максимальна різниця між методами: {difference:.10f}")