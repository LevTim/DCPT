import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split

from scipy.optimize import minimize


class LoadOptimizationAgent:

    def __init__(self):
        self.ml_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )

        # Максимально допустиме зміщення навантаження
        self.flexible_load_ratio = 0.20

    # =========================================================
    # ГЕНЕРАЦІЯ ДАНИХ
    # =========================================================
    def generate_synthetic_data(self, days=60):

        np.random.seed(42)

        data = []

        for day in range(days):

            hours = np.arange(24)

            # День тижня
            day_of_week = day % 7

            # Вихідні
            is_weekend = 1 if day_of_week in [5, 6] else 0

            # Температура
            temperature = np.random.normal(5, 10)

            # Базовий профіль
            base_load = (
                    35
                    + 15 * np.sin(np.pi * (hours - 5) / 10)
                    + 25 * np.exp(-0.5 * ((hours - 19) / 2) ** 2)
            )

            # Взимку навантаження вище
            if temperature < 0:
                base_load += 10

            # Вихідні — трохи менше навантаження
            if is_weekend:
                base_load *= 0.85

            noise = np.random.normal(0, 3, 24)

            actual_load = np.maximum(base_load + noise, 10)

            tariffs = np.where(
                (hours >= 17) & (hours <= 23),
                5.0,
                2.0
            )

            day_data = pd.DataFrame({
                'day': day,
                'hour': hours,
                'day_of_week': day_of_week,
                'is_weekend': is_weekend,
                'temperature': temperature,
                'load_kw': actual_load,
                'tariff': tariffs
            })

            data.append(day_data)

        return pd.concat(data, ignore_index=True)

    # =========================================================
    # ПІДГОТОВКА ДАНИХ
    # =========================================================
    def preprocess_data(self, df):

        X = df[
            [
                'hour',
                'day_of_week',
                'is_weekend',
                'temperature'
            ]
        ]

        y = df['load_kw']

        return X, y

    # =========================================================
    # НАВЧАННЯ МОДЕЛІ
    # =========================================================
    def train(self, historical_data):

        X, y = self.preprocess_data(historical_data)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        self.ml_model.fit(X_train, y_train)

        predictions = self.ml_model.predict(X_test)

        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, predictions)

        print("\n===== ОЦІНКА ML МОДЕЛІ =====")
        print(f"MSE  : {mse:.2f}")
        print(f"RMSE : {rmse:.2f}")
        print(f"MAE  : {mae:.2f}")

    # =========================================================
    # ПРОГНОЗ НАВАНТАЖЕННЯ
    # =========================================================
    def predict_base_load(
            self,
            day_of_week=1,
            is_weekend=0,
            temperature=5
    ):

        hours_df = pd.DataFrame({
            'hour': np.arange(24),
            'day_of_week': [day_of_week] * 24,
            'is_weekend': [is_weekend] * 24,
            'temperature': [temperature] * 24
        })

        predictions = self.ml_model.predict(hours_df)

        return predictions

    # =========================================================
    # ОПТИМІЗАЦІЯ НАВАНТАЖЕННЯ
    # =========================================================
    def optimize_load(self, forecast_df):

        predicted_load = forecast_df['predicted_load'].values
        tariffs = forecast_df['tariff'].values

        original_cost = np.sum(predicted_load * tariffs)

        # Максимальна кількість енергії,
        # яку можна переносити
        max_shift = predicted_load * self.flexible_load_ratio

        # -----------------------------------------------------
        # ЦІЛЬОВА ФУНКЦІЯ
        # -----------------------------------------------------
        def objective(x):
            return np.sum(x * tariffs)

        # -----------------------------------------------------
        # ОБМЕЖЕННЯ
        # -----------------------------------------------------

        constraints = [

            # Загальне навантаження повинно залишитись однаковим
            {
                'type': 'eq',
                'fun': lambda x: np.sum(x) - np.sum(predicted_load)
            }
        ]

        # Межі для кожної години
        bounds = []

        for i in range(len(predicted_load)):

            lower = predicted_load[i] - max_shift[i]
            upper = predicted_load[i] + max_shift[i]

            bounds.append((lower, upper))

        # -----------------------------------------------------
        # ОПТИМІЗАЦІЯ
        # -----------------------------------------------------
        result = minimize(
            objective,
            predicted_load,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        optimized_load = result.x

        optimized_cost = np.sum(optimized_load * tariffs)

        savings = original_cost - optimized_cost

        savings_pct = (savings / original_cost) * 100

        # -----------------------------------------------------
        # РЕКОМЕНДАЦІЇ
        # -----------------------------------------------------
        recommendations = []

        for hour in range(24):

            diff = predicted_load[hour] - optimized_load[hour]

            if diff > 1:

                target_hour = int(np.argmin(optimized_load))

                recommendations.append(
                    f"Перенести {diff:.2f} кВт "
                    f"з {hour}:00 на {target_hour}:00"
                )

        optimized_df = forecast_df.copy()

        optimized_df['optimized_load'] = optimized_load

        return (
            optimized_df,
            recommendations,
            original_cost,
            optimized_cost,
            savings_pct
        )

    # =========================================================
    # ВІЗУАЛІЗАЦІЯ
    # =========================================================
    def plot_all_results(self, test_results):

        fig, axes = plt.subplots(3, 1, figsize=(14, 15))

        for i, res in enumerate(test_results):

            ax = axes[i]

            df = res['data']

            ax.plot(
                df['hour'],
                df['predicted_load'],
                label='До оптимізації',
                linestyle='--',
                marker='o'
            )

            ax.plot(
                df['hour'],
                df['optimized_load'],
                label='Після оптимізації',
                linewidth=2,
                marker='s'
            )

            # Виділення дорогих годин
            max_tariff = df['tariff'].max()

            for hour in df[df['tariff'] == max_tariff]['hour']:

                ax.axvspan(
                    hour - 0.5,
                    hour + 0.5,
                    alpha=0.2
                )

            ax.set_title(
                f"{res['name']} | "
                f"Економія: {res['savings']:.2f}%"
            )

            ax.set_ylabel('Навантаження (кВт)')
            ax.set_xticks(np.arange(0, 24, 1))
            ax.grid(True)
            ax.legend()

        axes[-1].set_xlabel('Година доби')

        plt.tight_layout()

        plt.show()

    # =========================================================
    # CLI
    # =========================================================
    def run_cli(self):

        print("Навчання моделі...")

        historical_data = self.generate_synthetic_data(days=60)

        self.train(historical_data)

        hours = np.arange(24)

        # -----------------------------------------------------
        # 3 ТЕСТОВІ СЦЕНАРІЇ
        # -----------------------------------------------------
        test_cases = [

            {
                "name": "Робочий день",
                "predicted_load": self.predict_base_load(
                    day_of_week=2,
                    is_weekend=0,
                    temperature=8
                ),
                "tariffs": np.where(
                    (hours >= 17) & (hours <= 23),
                    5.0,
                    2.0
                )
            },

            {
                "name": "Холодний зимовий день",
                "predicted_load": self.predict_base_load(
                    day_of_week=1,
                    is_weekend=0,
                    temperature=-10
                ),
                "tariffs": np.where(
                    ((hours >= 8) & (hours <= 10))
                    |
                    ((hours >= 17) & (hours <= 23)),
                    6.0,
                    2.0
                )
            },

            {
                "name": "Вихідний день",
                "predicted_load": self.predict_base_load(
                    day_of_week=6,
                    is_weekend=1,
                    temperature=15
                ),
                "tariffs": np.full(24, 2.5)
            }
        ]

        results_for_plot = []

        # -----------------------------------------------------
        # ОБРОБКА СЦЕНАРІЇВ
        # -----------------------------------------------------
        for case in test_cases:

            print("\n" + "=" * 60)
            print(case["name"].upper())
            print("=" * 60)

            forecast_df = pd.DataFrame({

                'hour': hours,

                'predicted_load': case['predicted_load'],

                'tariff': case['tariffs']
            })

            (
                opt_df,
                recs,
                orig_cost,
                opt_cost,
                sav_pct

            ) = self.optimize_load(forecast_df)

            for rec in recs:
                print(" -", rec)

            print(
                f"\nВитрати ДО: {orig_cost:.2f}"
            )

            print(
                f"Витрати ПІСЛЯ: {opt_cost:.2f}"
            )

            print(
                f"Економія: {sav_pct:.2f}%"
            )

            results_for_plot.append({

                "name": case["name"],

                "data": opt_df,

                "savings": sav_pct
            })

        print("\nВідображення графіків...")

        self.plot_all_results(results_for_plot)


# =============================================================
# MAIN
# =============================================================
if __name__ == "__main__":

    agent = LoadOptimizationAgent()

    agent.run_cli()