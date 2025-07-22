import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# Fruits with emoji tickers
FRUITS = ['🍎', '🍌', '🍊', '🍇', '🍓']  # Apple, Banana, Orange, Grape, Strawberry
NUM_FRUITS = len(FRUITS)
INITIAL_SUPPLY_PER_FRUIT = 1000  # Total units per fruit distributed to traders
INITIAL_CASH = 1000  # Starting cash per trader
NUM_TRADERS = 100
NUM_STEPS = 200  # Simulation steps

# Trader types
TYPE_RANDOM = 'random'  # 70
TYPE_TREND = 'trend'    # 20
TYPE_WHALE = 'whale'    # 10

class Trader:
    def __init__(self, id, type):
        self.id = id
        self.type = type
        self.cash = INITIAL_CASH
        self.inventory = {fruit: 0 for fruit in FRUITS}

    def decide_order(self, current_prices, price_history):
        if self.type == TYPE_RANDOM:
            # Random buy/sell
            if random.random() < 0.5:
                action = 'buy'
            else:
                action = 'sell'
            fruit = random.choice(FRUITS)
            current_price = current_prices[fruit]
            if random.random() < 0.1:  # Rare big move
                deviation = random.uniform(-0.2, 0.2)
            else:
                deviation = random.uniform(-0.05, 0.05)
            price = current_price * (1 + deviation)
            quantity = random.randint(1, 10)
        elif self.type == TYPE_TREND:
            # Trend follower
            fruit = random.choice(FRUITS)
            history = price_history[fruit][-5:]  # Last 5 steps
            if len(history) < 2:
                return None  # Not enough data
            delta = (history[-1] - history[0]) / len(history)
            if delta > 0:
                action = 'buy'
                price = current_prices[fruit] * 1.02  # Slightly above
            else:
                action = 'sell'
                price = current_prices[fruit] * 0.98  # Slightly below
            quantity = random.randint(5, 15)
        elif self.type == TYPE_WHALE:
            # Rare action
            if random.random() > 0.05:
                return None
            if random.random() < 0.5:
                action = 'buy'
            else:
                action = 'sell'
            fruit = random.choice(FRUITS)
            current_price = current_prices[fruit]
            deviation = random.uniform(-0.1, 0.1)
            price = current_price * (1 + deviation)
            quantity = random.randint(50, 100)
        else:
            return None

        # Check feasibility
        if action == 'sell' and self.inventory[fruit] < quantity:
            return None  # Can't sell what you don't have
        if action == 'buy' and self.cash < price * quantity:
            return None  # Not enough cash

        return {'action': action, 'fruit': fruit, 'price': price, 'quantity': quantity, 'trader': self}

# Initialize traders
traders = []
for i in range(NUM_TRADERS):
    if i < 70:
        type = TYPE_RANDOM
    elif i < 90:
        type = TYPE_TREND
    else:
        type = TYPE_WHALE
    traders.append(Trader(i, type))

# Distribute initial inventory
for fruit in FRUITS:
    remaining = INITIAL_SUPPLY_PER_FRUIT
    random.shuffle(traders)
    for trader in traders:
        if remaining <= 0:
            break
        alloc = random.randint(0, min(10, remaining))
        trader.inventory[fruit] += alloc
        remaining -= alloc

# Initialize prices and history
current_prices = {fruit: random.uniform(10, 20) for fruit in FRUITS}
price_history = {fruit: [current_prices[fruit]] for fruit in FRUITS}

# Function to match orders for a fruit
def match_orders(buy_orders, sell_orders, current_price):
    buy_orders.sort(key=lambda o: o['price'], reverse=True)  # Highest buy first
    sell_orders.sort(key=lambda o: o['price'])  # Lowest sell first
    trades = []
    i, j = 0, 0
    while i < len(buy_orders) and j < len(sell_orders):
        buy = buy_orders[i]
        sell = sell_orders[j]
        if buy['price'] >= sell['price']:
            trade_qty = min(buy['quantity'], sell['quantity'])
            trade_price = (buy['price'] + sell['price']) / 2  # Midpoint for simplicity
            # Execute trade
            buyer = buy['trader']
            seller = sell['trader']
            buyer.cash -= trade_price * trade_qty
            seller.cash += trade_price * trade_qty
            buyer.inventory[buy['fruit']] += trade_qty
            seller.inventory[sell['fruit']] -= trade_qty
            trades.append(trade_price)
            # Update quantities
            buy['quantity'] -= trade_qty
            sell['quantity'] -= trade_qty
            if buy['quantity'] == 0:
                i += 1
            if sell['quantity'] == 0:
                j += 1
        else:
            break  # No more matches
    # New price: average of trades or unchanged
    if trades:
        return sum(trades) / len(trades)
    return current_price

# Simulation and visualization setup
fig, axs = plt.subplots(NUM_FRUITS, 1, figsize=(10, 8))
lines = {}
for idx, fruit in enumerate(FRUITS):
    lines[fruit], = axs[idx].plot([], [], label=fruit)
    axs[idx].set_xlim(0, NUM_STEPS)
    axs[idx].set_ylim(0, 50)  # Adjust based on expected price range
    axs[idx].set_title(f"{fruit} Price")
    axs[idx].legend()

def update(frame):
    global current_prices
    # Collect orders
    orders = [trader.decide_order(current_prices, price_history) for trader in traders]
    orders = [o for o in orders if o]  # Filter None

    # Group by fruit
    for fruit in FRUITS:
        buy_orders = [o for o in orders if o['fruit'] == fruit and o['action'] == 'buy']
        sell_orders = [o for o in orders if o['fruit'] == fruit and o['action'] == 'sell']
        new_price = match_orders(buy_orders, sell_orders, current_prices[fruit])
        current_prices[fruit] = new_price
        price_history[fruit].append(new_price)

    # Update plots
    for fruit in FRUITS:
        lines[fruit].set_data(range(len(price_history[fruit])), price_history[fruit])
    return list(lines.values())

# Run animation
ani = FuncAnimation(fig, update, frames=range(NUM_STEPS), interval=100, blit=True)  # 0.1s per frame
plt.tight_layout()
plt.show()
