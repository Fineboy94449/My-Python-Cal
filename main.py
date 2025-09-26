import math
import requests
import json
import time
from typing import Dict, List, Optional

# CAL94449
print('CAL94449')

print()
print('FINANCIAL CALCULATOR WITH REAL-TIME EXCHANGE RATES')
print('=' * 50)

class CoinGeckoAPI:
    def __init__(self, cache_duration=300):  # 5 minutes cache
        self.base_url = "https://api.coingecko.com/api/v3"
        self.cache_duration = cache_duration
        self.cached_rates = {}
        self.cached_currencies = {}
        self.last_update = 0
        self.last_currency_update = 0
        
    def get_all_supported_currencies(self) -> Dict[str, List[str]]:
        """Get all supported currencies from CoinGecko"""
        current_time = time.time()
        
        # Cache currency list for 1 hour (3600 seconds)
        if current_time - self.last_currency_update < 3600 and self.cached_currencies:
            return self.cached_currencies
            
        print("🔍 Fetching all supported currencies from CoinGecko...")
        
        try:
            # Get all cryptocurrencies
            crypto_url = f"{self.base_url}/coins/list"
            crypto_response = requests.get(crypto_url, timeout=15)
            crypto_response.raise_for_status()
            crypto_data = crypto_response.json()
            
            # Get supported fiat currencies
            fiat_url = f"{self.base_url}/simple/supported_vs_currencies"
            fiat_response = requests.get(fiat_url, timeout=15)
            fiat_response.raise_for_status()
            fiat_data = fiat_response.json()
            
            # Organize currencies
            cryptocurrencies = []
            stablecoins = []
            
            # Common stablecoin keywords
            stablecoin_keywords = ['usd', 'usdt', 'usdc', 'busd', 'dai', 'tusd', 'pax', 'gusd', 'ust', 'frax', 'lusd', 'ousd']
            
            for coin in crypto_data[:500]:  # Limit to top 500 for performance
                symbol = coin['symbol'].upper()
                name = coin['name'].lower()
                
                # Check if it's a stablecoin
                is_stablecoin = any(keyword in name or keyword in symbol.lower() for keyword in stablecoin_keywords)
                
                if is_stablecoin:
                    stablecoins.append(symbol)
                else:
                    cryptocurrencies.append(symbol)
            
            # Organize fiat currencies  
            fiat_currencies = [curr.upper() for curr in fiat_data]
            
            result = {
                'fiat': sorted(fiat_currencies),
                'crypto': sorted(cryptocurrencies),
                'stablecoins': sorted(stablecoins)
            }
            
            self.cached_currencies = result
            self.last_currency_update = current_time
            
            print(f"✅ Found {len(fiat_currencies)} fiat, {len(cryptocurrencies)} crypto, {len(stablecoins)} stablecoins")
            return result
            
        except Exception as e:
            print(f"❌ Error fetching currencies: {e}")
            # Return basic fallback
            return {
                'fiat': ['USD', 'EUR', 'GBP', 'ZAR', 'AUD', 'NGN', 'JPY', 'CAD', 'CHF'],
                'crypto': ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'AVAX', 'LINK', 'UNI'],
                'stablecoins': ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD']
            }
    
    def get_exchange_rates(self, vs_currency='usd') -> Dict[str, float]:
        """Get current exchange rates with caching"""
        current_time = time.time()
        
        if current_time - self.last_update < self.cache_duration and self.cached_rates:
            return self.cached_rates
        
        print(f"🔄 Fetching fresh exchange rates (vs {vs_currency.upper()})...")
        
        try:
            rates = {vs_currency.upper(): 1.0}  # Base currency
            
            # Get top cryptocurrencies (by market cap)
            crypto_url = f"{self.base_url}/coins/markets"
            crypto_params = {
                'vs_currency': vs_currency,
                'order': 'market_cap_desc',
                'per_page': 100,  # Top 100 cryptos
                'page': 1
            }
            
            crypto_response = requests.get(crypto_url, params=crypto_params, timeout=15)
            crypto_response.raise_for_status()
            crypto_data = crypto_response.json()
            
            for coin in crypto_data:
                symbol = coin['symbol'].upper()
                price = coin['current_price']
                if price and price > 0:
                    rates[symbol] = 1 / price  # Convert to "units per base currency"
            
            # Get fiat exchange rates
            try:
                exchange_url = f"{self.base_url}/exchange_rates"
                exchange_response = requests.get(exchange_url, timeout=10)
                exchange_response.raise_for_status()
                exchange_data = exchange_response.json()
                
                if 'rates' in exchange_data:
                    btc_rate = exchange_data['rates']['btc']['value']
                    
                    for curr_code, curr_data in exchange_data['rates'].items():
                        if curr_code != 'btc':
                            symbol = curr_code.upper()
                            rate = curr_data['value'] / btc_rate  # Convert via BTC
                            if rate > 0:
                                rates[symbol] = rate
                                
            except Exception as e:
                print(f"Warning: Fiat rates unavailable: {e}")
            
            self.cached_rates = rates
            self.last_update = current_time
            
            print(f"✅ Fetched {len(rates)} exchange rates")
            return rates
            
        except Exception as e:
            print(f"❌ Error fetching rates: {e}")
            return self.cached_rates if self.cached_rates else {'USD': 1.0}

# Initialize CoinGecko API
api = CoinGeckoAPI()

print("🌐 Loading currency data...")
currencies = api.get_all_supported_currencies()
exchange_rates = api.get_exchange_rates()

# Your original currency lists (now expanded)
fiat = currencies['fiat'][:20]  # Top 20 fiat currencies for display
crypto = currencies['crypto'][:30]  # Top 30 cryptocurrencies for display  
crypto_stable_coin = currencies['stablecoins'][:15]  # Top 15 stablecoins for display

print()
print('SIMPLE_INTEREST CALCULATOR')

# Show available options (limited for readability)
print(f"\n📊 Available Currencies ({len(fiat + crypto + crypto_stable_coin)} shown):")
print(f"💵 Fiat ({len(fiat)}): {', '.join(fiat[:10])}{'...' if len(fiat) > 10 else ''}")
print(f"₿ Crypto ({len(crypto)}): {', '.join(crypto[:10])}{'...' if len(crypto) > 10 else ''}")  
print(f"🔒 Stable ({len(crypto_stable_coin)}): {', '.join(crypto_stable_coin[:8])}{'...' if len(crypto_stable_coin) > 8 else ''}")

print(f"\n💡 Tip: You can use ANY of the {len(currencies['fiat']) + len(currencies['crypto']) + len(currencies['stablecoins'])} supported currencies!")
print("Common ones: USD, EUR, BTC, ETH, USDT, ZAR, GBP, JPY")

# Select currency with enhanced validation
while True:
    currency = input('\nSelect your currency: ').upper()
    
    all_currencies = currencies['fiat'] + currencies['crypto'] + currencies['stablecoins']
    if currency in all_currencies:
        print(f"✅ You selected: {currency}")
        
        # Show current rate if available
        if currency in exchange_rates and currency != 'USD':
            rate = exchange_rates[currency]
            if rate < 1:
                print(f"💱 Current rate: 1 USD = {rate:.8f} {currency}")
            else:
                print(f"💱 Current rate: 1 USD = {rate:.4f} {currency}")
        break
    else:
        print(f"❌ Currency '{currency}' not found.")
        search_results = [curr for curr in all_currencies if currency.lower() in curr.lower()]
        if search_results:
            print(f"💡 Did you mean: {', '.join(search_results[:5])}")

def simple_interest(P, r, t):
    A = P * (r / 100) * t
    total_amount = P + A
    return A, total_amount

def compound_interest(P, r, t, n):
    A = P * (1 + (r / 100) / n) ** (n * t)
    interest = A - P
    return interest, A

# Choose investment type (loop until correct)
while True:
    investment_type = input("\nChoose investment type (simple / compound): ").lower()
    if investment_type in ["simple", "compound"]:
        break
    else:
        print("❌ Invalid choice. Please type 'simple' or 'compound'.")

# Get inputs from user
P = float(input(f"\nEnter Principal amount ({currency}): "))
r = float(input("Enter Annual Interest Rate (%): "))
t = float(input("Enter Time (in years): "))

if investment_type == "simple":
    A, total = simple_interest(P, r, t)
    print(f"\n✅ Simple Interest: {A:.8f} {currency}")
    print(f"💰 Total Amount: {total:.8f} {currency}")

else:  # compound
    n = int(input("Enter number of times interest is compounded per year: "))
    interest, total = compound_interest(P, r, t, n)
    print(f"\n✅ Compound Interest: {interest:.8f} {currency}")
    print(f"💰 Total Amount: {total:.8f} {currency}")

def convert(amount, from_currency, to_currency):
    """Convert between currencies using real-time rates"""
    if from_currency not in exchange_rates or to_currency not in exchange_rates:
        return f"❌ Exchange rate not available for {from_currency} or {to_currency}"
    
    try:
        # Both rates are relative to USD
        if from_currency == 'USD':
            return amount * exchange_rates[to_currency]
        elif to_currency == 'USD':
            return amount / exchange_rates[from_currency]
        else:
            # Convert: from_currency → USD → to_currency
            usd_amount = amount / exchange_rates[from_currency]
            return usd_amount * exchange_rates[to_currency]
    except (ZeroDivisionError, KeyError):
        return "❌ Conversion error - invalid exchange rate"

print(f"\n{'='*50}")
print("💱 CURRENCY CONVERTER")
print(f"Available rates for {len(exchange_rates)} currencies")

amount = float(input("Enter amount: "))
from_currency = input("From currency: ").upper()
to_currency = input("To currency: ").upper()

result = convert(amount, from_currency, to_currency)

if isinstance(result, str):  # error message
    print(result)
    
    # Suggest available currencies if not found
    all_available = list(exchange_rates.keys())
    if from_currency not in all_available:
        similar = [curr for curr in all_available if from_currency.lower() in curr.lower() or curr.lower() in from_currency.lower()]
        if similar:
            print(f"💡 Similar to '{from_currency}': {', '.join(similar[:3])}")
    
    if to_currency not in all_available:
        similar = [curr for curr in all_available if to_currency.lower() in curr.lower() or curr.lower() in to_currency.lower()]
        if similar:
            print(f"💡 Similar to '{to_currency}': {', '.join(similar[:3])}")
            
else:
    # Format output based on currency type and value
    if result < 0.0001:
        print(f"💰 {amount} {from_currency} = {result:.8f} {to_currency}")
    elif result < 1:
        print(f"💰 {amount} {from_currency} = {result:.6f} {to_currency}")
    else:
        print(f"💰 {amount} {from_currency} = {result:.4f} {to_currency}")

print(f"\n📊 Exchange rates last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(api.last_update))}")
print("🌐 Data provided by CoinGecko API")
print("="*50)