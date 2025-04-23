import json
import requests

API_KEY = ""
API_BASE_URL = "https://api.ataix.kz"
ORDERS_FILE = "orders_data.json"

def get_request(endpoint: str, method: str):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "accept": "application/json",
        "X-API-Key": API_KEY
    }
    try:
        response = requests.request(method.upper(), url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса к {url}: {e}")
        return None

def print_order_status(Order_ID, Side, Price, Quantity, Cum_Quantity, Cum_Quote, Commission, Symbol, Status):
    print("\n📋 Список ордеров:")
    for i in range(len(Order_ID)):
        print(f"- [{Status[i]}] {Side[i].upper()} {Symbol[i]} | Цена: {Price[i]} | Кол-во: {Quantity[i]} | Исполнено: {Cum_Quantity[i]} | Сумма: {Cum_Quote[i]} | Комиссия: {Commission[i]}")

def sum_orders_sell_buy(side_status: str, info_orders: list):
    cumQuoteQuantity = 0
    Commission = 0
    for side in info_orders:
        if side and side.get("result", {}).get("side") == side_status:
            cumQuoteQuantity += float(side["result"].get("cumQuoteQuantity", 0))
            Commission += float(side["result"].get("cumCommission", 0))
    return cumQuoteQuantity, Commission

def main():
    with open(ORDERS_FILE, "r") as f:
        data = json.load(f)

    order_ids = [item["orderID"] for item in data if "orderID" in item]

    info_orders = []
    for order_id in order_ids:
        response = get_request(f"/api/orders/{order_id}", "get")
        info_orders.append(response)

    orderID_list = []
    side_list = []
    price_list = []
    quantity_list = []
    cumQuantity_list = []
    cumQuoteQuantity_list = []
    cumCommission_list = []
    symbol_list = []
    status_list = []

    for order in info_orders:
        if not order or "result" not in order:
            continue
        result = order["result"]
        orderID_list.append(result.get("orderID"))
        side_list.append(result.get("side"))
        price_list.append(result.get("price"))
        quantity_list.append(result.get("quantity"))
        cumQuantity_list.append(result.get("cumQuantity"))
        cumQuoteQuantity_list.append(result.get("cumQuoteQuantity"))
        cumCommission_list.append(result.get("cumCommission"))
        symbol_list.append(result.get("symbol"))
        status_list.append(result.get("status"))

    print_order_status(orderID_list, side_list, price_list, quantity_list,
                       cumQuantity_list, cumQuoteQuantity_list,
                       cumCommission_list, symbol_list, status_list)

    cumQuoteQuantity_sell, Commission_sell = sum_orders_sell_buy("sell", info_orders)
    cumQuoteQuantity_buy, Commission_buy = sum_orders_sell_buy("buy", info_orders)

    revenue = cumQuoteQuantity_sell - Commission_sell
    cost = cumQuoteQuantity_buy + Commission_buy
    total = round(revenue - cost, 4)

    if cost != 0:
        total_percent = round((total / cost) * 100, 2)
    else:
        total_percent = 0.0

    print(f"\nОбщая сумма по продаже: {cumQuoteQuantity_sell}$ (включая комиссию: {Commission_sell}$)")
    print(f"Общая сумма по покупке: {cumQuoteQuantity_buy}$ (включая комиссию: {Commission_buy}$)")

    if total > 0:
        print(f"✅ Прибыль: {total}$ (+{total_percent}%)")
    elif total < 0:
        print(f"🔻 Убыток: {total}$ ({total_percent}%)")
    else:
        print(f"➖ Ни прибыли, ни убытка: {total}$ (0%)")

if __name__ == "__main__":
    main()
