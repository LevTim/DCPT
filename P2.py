import pandas as pd

# 1. Створюємо DataFrame "Замовлення"
# Додамо товари з ID 104 та 105, яких немає в довіднику товарів
orders_data = {
    'order_id': [1, 2, 3, 4, 5],
    'product_id': [101, 102, 104, 101, 105],
    'quantity': [2, 1, 4, 1, 3]
}
orders_df = pd.DataFrame(orders_data)

# 2. Створюємо DataFrame "Довідник товарів" (категорія та собівартість)
products_data = {
    'product_id': [101, 102, 103],
    'category': ['Електроніка', 'Одяг', 'Книги'],
    'cost': [500, 200, 150]
}
products_df = pd.DataFrame(products_data)

# 3. Виконуємо merge
# Використовуємо how='left', щоб зберегти всі замовлення.
# indicator=True створює колонку '_merge', яка показує, звідки взялися дані.
merged_df = pd.merge(orders_df, products_df, on='product_id', how='left', indicator=True)

# 4. Знаходимо рядки без відповідників
# Це ті рядки, які присутні лише в лівій таблиці (замовленнях)
unmatched_rows = merged_df[merged_df['_merge'] == 'left_only']

# 5. Оцінюємо їхню частку
total_orders = len(orders_df)
unmatched_count = len(unmatched_rows)
unmatched_percentage = (unmatched_count / total_orders) * 100

# Виведення результатів
print("--- Всі замовлення після об'єднання ---")
print(merged_df[['order_id', 'product_id', 'quantity', 'category', 'cost']])

print("\n--- Рядки без відповідників у довіднику ---")
print(unmatched_rows[['order_id', 'product_id', 'quantity', 'category', 'cost']])

print(f"\nЧастка рядків без відповідників: {unmatched_percentage:.1f}% ({unmatched_count} з {total_orders} замовлень)")