import numpy as np


class SelectivityEstimation:
    def __init__(self, act, est, e):
        self.act = act
        self.est = est
        self.e = e
    

    def mean_absolute_error(self):
        mae = np.mean(np.abs(np.log(self.act) - np.log(self.est)))
        mae_log = np.mean(np.abs(np.log(self.act / self.est)))
        mae_log_e = np.mean(np.abs(np.log(self.e)))
        return mae, mae_log, mae_log_e
    

    def mean_squared_error(self):
        mse = np.mean((np.log(self.act) - np.log(self.est))**2)
        mse_log = np.mean((np.log(self.act / self.est))**2)
        mse_log_e = np.mean((np.log(self.e))**2)
        return mse, mse_log, mse_log_e


# act = np.array([0.1, 0.5, 0.8, 0.2, 0.6])
# est = np.array([0.12, 0.48, 0.75, 0.18, 0.58])
# e = np.array([0.05, 0.52, 0.78, 0.22, 0.65])

# sel_est = SelectivityEstimation(act, est, e)
# mae, mae_log, mae_log_e = sel_est.mean_absolute_error()
# mse, mse_log, mse_log_e = sel_est.mean_squared_error()

# print("Mean Absolute Error:", mae)
# print("Mean Absolute Error for Log-transformed labels:", mae_log)
# print("Mean Absolute Error for Log-transformed labels using e:", mae_log_e)
# print("Mean Squared Error:", mse)
# print("Mean Squared Error for Log-transformed labels:", mse_log)
# print("Mean Squared Error for Log-transformed labels using e:", mse_log_e)
