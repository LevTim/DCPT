import pandas as pd
from sklearn.preprocessing import LabelEncoder

# Створюємо тестовий набір даних
data = {
    'Колір': ['Червоний', 'Зелений', 'Синій', 'Червоний', 'Зелений']
}

df = pd.DataFrame(data)

print("Оригінальні дані:")
print(df)

# ---------------- LABEL ENCODING ----------------
label_encoder = LabelEncoder()
df['Колір_Label'] = label_encoder.fit_transform(df['Колір'])

print("\nДані після Label Encoding:")
print(df)

# ---------------- ONE-HOT ENCODING ----------------
# Додано dtype=int для виводу 0 та 1 замість True/False
df_one_hot = pd.get_dummies(df[['Колір']], columns=['Колір'], dtype=int)

print("\nДані після One-Hot Encoding:")
print(df_one_hot)