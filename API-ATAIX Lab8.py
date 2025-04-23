import json
import requests

API_KEY = ""
API_BASE_URL = "https://api.ataix.kz/api/orders"
ORDERS_FILE = "orders_data.json"


def load_orders():
    with open(ORDERS_FILE, "r") as f:
        return json.load(f)


def save_orders(order_list):
    with open(ORDERS_FILE, "w") as f:
        json.dump(order_list, f, indent=4)


def get_order_status(order_id):
    url = f"{API_BASE_URL}/{order_id}"
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY
    }
    response = requests.get(url, headers=headers, timeout=20)

    if response.status_code == 200:
        return response.json().get("result", {}).get("status")

    print(f"❌ Ошибка получения статуса ордера {order_id}: {response.status_code}")
    return None


def process_orders():
    orders = load_orders()

    for i in range(0, len(orders), 2):  # предполагаем, что ордера идут попарно (покупка, продажа)
        buy_order = orders[i]
        sell_order = orders[i + 1]

        if buy_order["status"].lower() != "filled" or sell_order["status"].lower() != "filled":
            continue

        buy_price = float(buy_order["price"])
        sell_price = float(sell_order["price"])
        quantity = float(buy_order["quantity"])  # предполагаем, что количество одинаковое для покупки и продажи

        # Рассчитываем чистую прибыль и процент прибыли
        profit = (sell_price - buy_price) * quantity
        profit_percentage = (profit / (buy_price * quantity)) * 100

        # Выводим информацию о прибыли
        print(f"\n🔍 Проверка ордера {buy_order['orderID']} и {sell_order['orderID']}...")
        print(f"✅ Ордер {buy_order['orderID']} выполнен.")
        print(f"✅ Ордер {sell_order['orderID']} выполнен.")
        print(f"💰 Чистая прибыль: {profit} USDT, что составляет {profit_percentage:.2f}%")

        # Обновляем статус ордера в файле
        buy_order["status"] = "completed"
        sell_order["status"] = "completed"

    save_orders(orders)
    print("\n📁 Обработка завершена. Файл orders_data.json обновлён.")


if __name__ == "__main__":
    process_orders()
