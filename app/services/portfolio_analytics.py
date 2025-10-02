from typing import List, Dict, Optional
from datetime import datetime, date
import pandas as pd
import numpy as np
from scipy.optimize import minimize
from decimal import Decimal


class PortfolioAnalytics:
    @staticmethod
    def calculate_ttwrr(
        transactions: List[Dict],
        prices: List[Dict],
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Výpočet Time-Weighted Rate of Return (TWRR)
        """
        # Převod na DataFrame
        df_trans = pd.DataFrame(transactions)
        df_prices = pd.DataFrame(prices)
        
        # Seřazení podle data
        df_trans = df_trans.sort_values('trade_time')
        df_prices = df_prices.sort_values('date')
        
        # Výpočet denních hodnot portfolia
        daily_values = []
        current_date = start_date
        
        while current_date <= end_date:
            # Hodnota portfolia k danému dni
            portfolio_value = 0
            
            # Procházení transakcí do aktuálního dne
            day_transactions = df_trans[df_trans['trade_time'].dt.date <= current_date]
            
            for asset_id in day_transactions['asset_id'].unique():
                asset_trans = day_transactions[day_transactions['asset_id'] == asset_id]
                quantity = asset_trans['quantity'].sum()
                
                if quantity > 0:
                    # Získání poslední ceny pro dané aktivum
                    last_price = df_prices[
                        (df_prices['asset_id'] == asset_id) &
                        (df_prices['date'].dt.date <= current_date)
                    ]['close'].iloc[-1]
                    
                    portfolio_value += quantity * last_price
            
            daily_values.append({
                'date': current_date,
                'value': portfolio_value
            })
            
            current_date += pd.Timedelta(days=1)
        
        # Výpočet TWRR
        df_values = pd.DataFrame(daily_values)
        daily_returns = df_values['value'].pct_change()
        
        cumulative_return = (1 + daily_returns).prod() - 1
        annualized_return = (1 + cumulative_return) ** (365 / len(daily_returns)) - 1
        
        return {
            'daily_values': daily_values,
            'cumulative_return': float(cumulative_return),
            'annualized_return': float(annualized_return)
        }

    @staticmethod
    def calculate_xirr(
        transactions: List[Dict],
        current_value: float
    ) -> float:
        """
        Výpočet XIRR (Extended Internal Rate of Return)
        """
        # Převod na DataFrame
        df = pd.DataFrame(transactions)
        
        # Přidání současné hodnoty jako poslední cashflow
        last_row = pd.DataFrame([{
            'date': pd.Timestamp.now(),
            'cashflow': -current_value
        }])
        df = pd.concat([df, last_row])
        
        # Seřazení podle data
        df = df.sort_values('date')
        
        # Výpočet počtu dní od první transakce
        df['days'] = (df['date'] - df['date'].min()).dt.days
        
        def xirr_objective(rate):
            """Pomocná funkce pro výpočet XIRR"""
            return np.sum(
                df['cashflow'] / (1 + rate) ** (df['days'] / 365)
            )
        
        # Nalezení XIRR pomocí optimalizace
        try:
            result = minimize(
                lambda x: xirr_objective(x[0]) ** 2,
                [0.1],
                method='Nelder-Mead'
            )
            return float(result.x[0])
        except:
            return None

    @staticmethod
    def calculate_risk_metrics(
        daily_returns: List[float],
        risk_free_rate: float = 0.02
    ) -> Dict:
        """
        Výpočet rizikových metrik (volatilita, Sharpe ratio, max drawdown)
        """
        returns = pd.Series(daily_returns)
        
        # Volatilita (annualizovaná)
        volatility = returns.std() * np.sqrt(252)
        
        # Sharpe ratio
        excess_returns = returns - risk_free_rate / 252
        sharpe = np.sqrt(252) * excess_returns.mean() / returns.std()
        
        # Maximum drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdowns = cumulative / rolling_max - 1
        max_drawdown = drawdowns.min()
        
        return {
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_drawdown)
        }

    @staticmethod
    def calculate_benchmark_comparison(
        portfolio_values: List[Dict],
        benchmark_values: List[Dict]
    ) -> Dict:
        """
        Porovnání s benchmarkem (tracking error, beta)
        """
        # Převod na DataFrame
        df_portfolio = pd.DataFrame(portfolio_values)
        df_benchmark = pd.DataFrame(benchmark_values)
        
        # Výpočet denních výnosů
        portfolio_returns = df_portfolio['value'].pct_change().dropna()
        benchmark_returns = df_benchmark['value'].pct_change().dropna()
        
        # Tracking error
        tracking_error = np.std(portfolio_returns - benchmark_returns) * np.sqrt(252)
        
        # Beta
        covariance = np.cov(portfolio_returns, benchmark_returns)[0][1]
        benchmark_variance = np.var(benchmark_returns)
        beta = covariance / benchmark_variance
        
        return {
            'tracking_error': float(tracking_error),
            'beta': float(beta)
        }

    @staticmethod
    def calculate_asset_allocation(
        holdings: List[Dict]
    ) -> Dict:
        """
        Výpočet alokace portfolia podle různých kritérií
        """
        df = pd.DataFrame(holdings)
        
        # Alokace podle typu aktiva
        asset_type_alloc = df.groupby('type')['market_value'].sum().to_dict()
        
        # Alokace podle regionu
        region_alloc = df.groupby('region')['market_value'].sum().to_dict()
        
        # Alokace podle sektoru
        sector_alloc = df.groupby('sector')['market_value'].sum().to_dict()
        
        # Alokace podle měny
        currency_alloc = df.groupby('currency')['market_value'].sum().to_dict()
        
        # Top 10 pozic
        top_holdings = df.nlargest(10, 'market_value')[
            ['symbol', 'name', 'market_value', 'weight']
        ].to_dict('records')
        
        return {
            'by_type': asset_type_alloc,
            'by_region': region_alloc,
            'by_sector': sector_alloc,
            'by_currency': currency_alloc,
            'top_holdings': top_holdings
        }