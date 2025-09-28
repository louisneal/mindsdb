### 1. 在 MindsDB 中先初始化此模型
由于 TimesFS 模型的特殊性，无需训练直接预测，该模型的创建主要为了形成动态参数，即：

* ```data_col``` 预测目标列
* ```timestamp_cole``` 时间序列，用于对预测目标列数值进行排序和预测日期构建，TimesFS 本身并不关心此数据
* ```horizon``` 预测期，即预测未来时间数据点的数量，最大值不超过 256

```sql
CREATE PREDICTOR timesfm
FROM mindsdb (SELECT 0.0 AS nil, 0.0 AS data_col, '2025-01-01' AS timestamp_col, 12 AS horizon)
PREDICT nil
GROUP BY data_col, timestamp_col, horizon
USING engine = 'timesfm'
```

### 2. 使用 TimesFM 模型进行预测
此 SQL 片段可以作为模板来使用，其中 JOIN 部分为 TimesFS 预测所需的参考数据，要求包含时间列和数值列

* ```tf.data_col=``` 用于指定参考数据中数值列的名称
* ```tf.timestamp_col =``` 用于指定参考数据中时间列的名称
* ```tf.horizon =``` 用于设定 TimesFS 模型预测数据的数量

```sql
SELECT tf.* 
FROM timesfm as tf 
JOIN files.sales_data
WHERE tf.data_col='sales' AND tf.timestamp_col = 'date' AND tf.horizon = 12
```

### TimesFM 模型预测返回的结果样例
| forecast_timestamp | forecast_value | confidence_level | prediction_interval_lower_bound | prediction_interval_upper_bound |
| ------------------ | -------------- | ---------------- | ------------------------------- | ------------------------------- |
| 2018-01-15 00:00:00.000000 | 52186.92578125 | 0.8 | 44882.734375 | 58594.67578125 |
| 2018-02-15 00:00:00.000000 | 48747.578125 | 0.8 | 40600.171875 | 56093.44140625 |