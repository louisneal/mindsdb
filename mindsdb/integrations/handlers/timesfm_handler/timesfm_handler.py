from typing import Optional, Dict
from dateutil.relativedelta import relativedelta
import pandas as pd
import timesfm

from mindsdb.integrations.libs.base import BaseMLEngine
from mindsdb.utilities.config import config
from mindsdb.utilities import log

logger = log.getLogger("mindsdb")

# 初始化模型对象
model = timesfm.TimesFM_2p5_200M_torch()

# 直接加载本地 checkpoint
model_path = config.paths['root'] / "models" / "timesfm-2.5-200m" / "model.safetensors"
model.load_checkpoint(path=model_path)

# 编译配置
model.compile(timesfm.ForecastConfig(max_context=1024, max_horizon=256))


class TimesfmHandler(BaseMLEngine):
    name = "timesfm"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create(self, target: str, df: Optional[pd.DataFrame] = None, args: Optional[Dict] = None) -> None:
        """Create and train model on given data"""
        # parse args
        if 'using' not in args:
            raise Exception("TimesFM engine requires a USING clause! Refer to its documentation for more details.")

        using = args['using']
        if df is None:
            raise Exception("TimesFM engine requires a some data to initialize!")

        self.model_storage.json_set('saved_args', {
            **args['using']
        })

    def predict(self, df: Optional[pd.DataFrame] = None, args: Optional[Dict] = None) -> pd.DataFrame:
        saved_args = self.model_storage.json_get('saved_args')
        return self._forecast(df, saved_args)

    @staticmethod
    def infer_and_generate_dates(ts: pd.Series, horizon: int):
        """
        根据历史时间序列推断频率，并生成未来日期，保持原始 anchor 日期
        支持：日度/月度/季度/年度
        """
        ts = pd.Series(pd.to_datetime(ts).dropna()).sort_values()
        last_date = ts.iloc[-1]

        inferred = pd.infer_freq(ts)

        # 日度
        if inferred == "D" or (inferred is None and ts.diff().mode()[0].days == 1):
            return pd.date_range(start=last_date + pd.Timedelta(days=1), periods=horizon, freq="D")

        # 计算时间间隔
        deltas = ts.diff().dropna()
        most_common_delta = deltas.mode()[0]
        days = most_common_delta.days

        future_dates = []
        if 28 <= days <= 31:  # 月度
            for i in range(1, horizon + 1):
                future_dates.append(last_date + relativedelta(months=i))
        elif 89 <= days <= 92:  # 季度
            for i in range(1, horizon + 1):
                future_dates.append(last_date + relativedelta(months=3 * i))
        elif 364 <= days <= 366:  # 年度
            for i in range(1, horizon + 1):
                future_dates.append(last_date + relativedelta(years=i))
        else:  # fallback，按 timedelta
            for i in range(1, horizon + 1):
                future_dates.append(last_date + most_common_delta * i)

        return pd.to_datetime(future_dates)

    def _forecast(self, df: Optional[pd.DataFrame] = None, saved_args: Optional[Dict] = None) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()

        data_col_name = df["data_col"][0]
        timestamp_col_name = df["timestamp_col"][0]
        horizon = df["horizon"][0]

        # 确保timestamp列是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col_name]):
            df = df.copy()
            df[timestamp_col_name] = pd.to_datetime(df[timestamp_col_name])
        # 按时间升序排列（最早的在前面）
        df_sorted = df.sort_values(timestamp_col_name).reset_index(drop=True)
        # 单个时间序列
        inputs = df_sorted[data_col_name].dropna().values

        point_forecast, quantile_forecast = model.forecast(horizon=horizon, inputs=[inputs])

        result_data = {
            'forecast_value': point_forecast[0],  # 点预测
            'confidence_level' : '0.8',
            'prediction_interval_lower_bound': quantile_forecast[0, :, 1],  # 10%分位数
            'prediction_interval_upper_bound': quantile_forecast[0, :, -1],  # 90%分位数
        }

        # 生成未来日期
        future_dates = self.infer_and_generate_dates(df_sorted[timestamp_col_name], horizon)

        # 拼接结果
        result_df = pd.DataFrame(result_data)
        result_df.insert(0, 'forecast_timestamp', future_dates)

        return result_df