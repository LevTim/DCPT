import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# =========================================================
# 1. ПІДГОТОВКА ДАНИХ
# =========================================================

# Створюємо часовий ряд (24 години, виміри кожні 10 хв)
hours = np.linspace(0, 24, 144)

# Функція генерації шуму
def generate_noise(base_level, noise_amplitude, spikes=False):
    data = base_level + noise_amplitude * np.random.randn(len(hours))

    # Імітація випадкових піків шуму
    if spikes:
        data += np.random.choice(
            [0, 25],
            size=len(hours),
            p=[0.9, 0.1]
        )

    return data

# Створення датасету
df = pd.DataFrame({
    'Time_Hours': hours,
    'Center_City': generate_noise(75, 5, spikes=True),
    'Residential_Area': generate_noise(50, 4),
    'Park_Zone': generate_noise(40, 2)
})

# =========================================================
# 2. МОДЕЛЮВАННЯ НІЧНОГО ЗНИЖЕННЯ ШУМУ
# =========================================================

night_mask = (
    (df['Time_Hours'] >= 22) |
    (df['Time_Hours'] <= 6)
)

# Вночі рівень шуму зменшується
df.loc[night_mask,
       ['Center_City', 'Residential_Area', 'Park_Zone']] -= 20

# =========================================================
# 3. ОБРОБКА ДАНИХ (ЗГЛАДЖУВАННЯ)
# =========================================================

df['Center_Smooth'] = (
    df['Center_City']
    .rolling(window=5, min_periods=1)
    .mean()
)

df['Residential_Smooth'] = (
    df['Residential_Area']
    .rolling(window=5, min_periods=1)
    .mean()
)

df['Park_Smooth'] = (
    df['Park_Zone']
    .rolling(window=5, min_periods=1)
    .mean()
)

# =========================================================
# 4. АНАЛІЗ ДАНИХ
# =========================================================

# Середні значення день/ніч
avg_day = df.loc[
    ~night_mask,
    ['Center_City', 'Residential_Area', 'Park_Zone']
].mean()

avg_night = df.loc[
    night_mask,
    ['Center_City', 'Residential_Area', 'Park_Zone']
].mean()

# Стандартне відхилення
std_values = df[
    ['Center_City', 'Residential_Area', 'Park_Zone']
].std()

# Максимальні значення
max_values = df[
    ['Center_City', 'Residential_Area', 'Park_Zone']
].max()

# Мінімальні значення
min_values = df[
    ['Center_City', 'Residential_Area', 'Park_Zone']
].min()

# =========================================================
# 5. ВИВЕДЕННЯ РЕЗУЛЬТАТІВ
# =========================================================

print("\n--- СЕРЕДНІ РІВНІ ШУМУ (дБ) ---")

print(f"\nЦентр міста:")
print(f"День: {avg_day['Center_City']:.1f} дБ")
print(f"Ніч: {avg_night['Center_City']:.1f} дБ")

print(f"\nСпальний район:")
print(f"День: {avg_day['Residential_Area']:.1f} дБ")
print(f"Ніч: {avg_night['Residential_Area']:.1f} дБ")

print(f"\nПарк:")
print(f"День: {avg_day['Park_Zone']:.1f} дБ")
print(f"Ніч: {avg_night['Park_Zone']:.1f} дБ")

print("\n--- СТАТИСТИКА ---")

print("\nСтандартне відхилення:")
print(std_values)

print("\nМаксимальні значення:")
print(max_values)

print("\nМінімальні значення:")
print(min_values)

# =========================================================
# 6. ВІЗУАЛІЗАЦІЯ ЧАСОВИХ РЯДІВ
# =========================================================

plt.figure(figsize=(14, 7))

# Сирі дані
plt.plot(
    df['Time_Hours'],
    df['Center_City'],
    alpha=0.25,
    label='Центр (сирі дані)'
)

# Згладжені дані
plt.plot(
    df['Time_Hours'],
    df['Center_Smooth'],
    linewidth=2,
    label='Центр (згладжено)'
)

plt.plot(
    df['Time_Hours'],
    df['Residential_Smooth'],
    linewidth=2,
    label='Спальний район'
)

plt.plot(
    df['Time_Hours'],
    df['Park_Smooth'],
    linewidth=2,
    label='Парк'
)

# Норма шуму для сну
plt.axhline(
    y=45,
    linestyle='--',
    label='Норма для сну (45 дБ)'
)

plt.title('Рівень шуму в різних локаціях протягом доби')
plt.xlabel('Час (години)')
plt.ylabel('Рівень шуму (дБ)')
plt.grid(True, alpha=0.3)
plt.legend()

plt.show()

# =========================================================
# 7. BOXPLOT ДЛЯ ПОРІВНЯННЯ ЛОКАЦІЙ
# =========================================================

plt.figure(figsize=(10, 6))

df[
    ['Center_City',
     'Residential_Area',
     'Park_Zone']
].boxplot()

plt.title('Порівняння розподілу рівня шуму')
plt.ylabel('Рівень шуму (дБ)')
plt.grid(True, alpha=0.3)

plt.show()

# =========================================================
# 8. ВИСНОВОК
# =========================================================

print("\n--- ВИСНОВОК ---")

print("""
1. Найвищий рівень шуму спостерігається
   у центральній частині міста.

2. Найнижчий рівень шуму характерний
   для паркової зони.

3. У нічний час рівень шуму суттєво
   знижується в усіх локаціях.

4. Центр міста має найбільшу
   нестабільність шуму через транспорт
   та випадкові пікові навантаження.

5. Паркова зона демонструє найбільш
   стабільний та комфортний рівень шуму.
""")