import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf

class TechnicalAnalyzer:
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.model = self._build_model()

    def _build_model(self):
        model = tf.keras.Sequential([
            tf.keras.layers.LSTM(50, return_sequences=True, input_shape=(30, 5)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.LSTM(30),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')
        return model

    def calculate_indicators(self, df):
        # Moving Averages
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA50'] = df['close'].rolling(window=50).mean()
        df['MA200'] = df['close'].rolling(window=200).mean()

        # Bollinger Bands
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        df['BB_upper'] = df['BB_middle'] + 2*df['close'].rolling(window=20).std()
        df['BB_lower'] = df['BB_middle'] - 2*df['close'].rolling(window=20).std()

        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        return df

    def generate_signals(self, df):
        signals = pd.DataFrame(index=df.index)
        
        # Generate signals based on multiple indicators
        signals['MA_Signal'] = np.where(
            df['close'] > df['MA50'], 1, 
            np.where(df['close'] < df['MA50'], -1, 0)
        )
        
        signals['RSI_Signal'] = np.where(
            df['RSI'] < 30, 1,
            np.where(df['RSI'] > 70, -1, 0)
        )
        
        signals['MACD_Signal'] = np.where(
            df['MACD'] > df['MACD_Signal'], 1,
            np.where(df['MACD'] < df['MACD_Signal'], -1, 0)
        )
        
        # Calculate signal strength and confidence
        signals['Signal_Strength'] = (
            signals['MA_Signal'] + 
            signals['RSI_Signal'] + 
            signals['MACD_Signal']
        ).abs()
        
        signals['Confidence'] = signals['Signal_Strength'] / 3 * 100
        
        # Generate final signal
        signals['Final_Signal'] = np.where(
            signals['Signal_Strength'] >= 2, 'BUY',
            np.where(signals['Signal_Strength'] <= -2, 'SELL', 'HOLD')
        )
        
        # Generate prediction
        prediction = self._generate_prediction(df)
        
        return signals, prediction

    def _generate_prediction(self, df):
        try:
            # Prepare features for prediction
            features = np.column_stack((
                df['close'].values,
                df['RSI'].values,
                df['MACD'].values,
                df['volume'].values,
                df['Price_Change'].values
            ))
            
            # Scale features
            scaled_features = self.scaler.fit_transform(features)
            
            # Make prediction
            current_price = df['close'].iloc[-1]
            predicted_change = self.model.predict(
                scaled_features[-30:].reshape(1, 30, 5)
            )[0][0]
            
            pattern_confidence = min(abs(predicted_change) * 100, 100)
            
            return {
                'current_price': current_price,
                'predicted_change': predicted_change,
                'pattern_confidence': pattern_confidence
            }
            
        except Exception as e:
            logging.error(f"Prediction error: {str(e)}")
            return None

    def get_entry_exit_points(self, df, signals):
        entry_points = []
        exit_points = []
        
        for idx, row in signals.iterrows():
            if row['Final_Signal'] == 'BUY':
                entry_points.append({
                    'timestamp': idx,
                    'price': df.loc[idx, 'close'],
                    'strength': row['Confidence']
                })
            elif row['Final_Signal'] == 'SELL':
                exit_points.append({
                    'timestamp': idx,
                    'price': df.loc[idx, 'close'],
                    'strength': row['Confidence']
                })
                
        return entry_points, exit_points
