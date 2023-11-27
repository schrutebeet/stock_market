import matplotlib.pyplot as plt
import numpy as np
#from tensorflow import keras

# from statsmodels.tsa.arima.model import ARIMA
# import arch


class Model:
    def __init__(self, stock_inst) -> None:
        self.stock_inst = stock_inst

    def lstm_nn(self, viz=True):
        self.model_name = "Long-Short Term Memory"
        model = keras.Sequential()
        model.add(
            keras.layers.LSTM(
                100,
                return_sequences=True,
                input_shape=(self.stock_inst.x_train.shape[1], 1),
            )
        )
        model.add(keras.layers.LSTM(100, return_sequences=False))
        model.add(keras.layers.Dense(25))
        model.add(keras.layers.Dense(1))
        print(model.summary())
        model.compile(optimizer="adam", loss="mean_squared_error")
        model.fit(
            self.stock_inst.x_train,
            self.stock_inst.y_train,
            batch_size=min(50, len(self.stock_inst.x_train)),
            epochs=3,
        )
        self.scaler_preds = model.predict(self.stock_inst.x_test)
        if self.stock_inst.scaler:
            self.real_preds = self.stock_inst.scaler.inverse_transform(self.scaler_preds)
        else:
            self.real_preds = self.scaler_preds
        rmse = np.sqrt(np.mean(self.real_preds - self.stock_inst.y_test) ** 2)
        accuracy = self._binary_pred()
        if viz:
            self._viz_predictions()
        return accuracy

    def _viz_predictions(self):
        data = self.stock_inst.data[["close"]]
        training_data_len = int(round(data.shape[0] * self.stock_inst.train_size, 0))
        train = data[:training_data_len].copy()
        test = data[training_data_len:].copy()
        test.loc[:, "preds"] = self.real_preds
        plt.figure(figsize=(16, 8))
        plt.title("Model")
        plt.xlabel("Date")
        plt.ylabel("Close Price USD ($)")
        plt.plot(train)
        plt.plot(test[["close", "preds"]])
        plt.legend(["Train", "Val", "Predictions"], loc="lower right")
        image_path = f"opt/{self.stock_inst.stock_symbol}_lstm_plot.png"
        plt.savefig(image_path)
        plt.close()

    def _binary_pred(self):
        hit_list = []
        total_iters = self.stock_inst.x_test.shape[0]
        for iter in range(total_iters):
            # Last known price in test
            val_i = self.stock_inst.x_test[iter][-1]
            pred_i = self.scaler_preds[iter]
            future_i = self.stock_inst.y_test[iter]
            # Decision taken based on prediction
            choice = pred_i - val_i > 0
            # Realization the next day
            realization = future_i - val_i > 0
            hit = self._XNOR(choice, realization)
            hit_list.append(hit)
        accuracy = sum(hit_list) / len(hit_list)
        print(f"\n\nAccuracy of the {self.model_name} model: {accuracy*100:.2f}%, from {total_iters} iterations\n")
        return accuracy

    @staticmethod
    def _XNOR(a, b):
        if a == b:
            return True
        else:
            return False
