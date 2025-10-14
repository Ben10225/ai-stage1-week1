import math
import re
import urllib.request
from typing import TypedDict, List
from urllib.parse import urljoin


class Product(TypedDict):
    id: str
    name: str
    price: int
    star: int


# 找出所有分頁的網址
def get_urls(html: str, base_url: str, current_url: str) -> List[str]:
    array = [current_url]
    ul_match = re.search(
        r'<ul class="c-pagination__pagesBar">(.*?)</ul>', html, re.DOTALL
    )

    if ul_match:
        ul_content = ul_match.group(1)

        pattern = r'<a[^>]*class="[^"]*\bc-pagination__link\b(?![^"]*is-active)[^"]*"[^>]*href="([^"]+)"'
        matches = re.findall(pattern, ul_content)

        for href in matches:
            full_url = urljoin(base_url, href)
            array.append(full_url)
    else:
        print("找不到 pagination 區塊")

    return array


# 抓取商品評價
# def get_product_rating(product_id) -> float:
#     url = "https://24h.pchome.com.tw/prod/" + product_id

#     try:
#         response = urllib.request.urlopen(url)
#         html = response.read().decode("utf-8")
#     except Exception as e:
#         print("無法取得網頁內容：", e)
#         return 0.0

#     pattern = r'<div class="c-ratingIcon__textNumber[^"]*">([\d.]+)</div>'
#     match = re.search(pattern, html)
#     if match:
#         return float(match.group(1))
#     return 0.0


# 抓取每個分頁的商品
def get_products(html: str) -> List[Product]:
    array = []
    pattern = (
        r'<div[^>]*class="[^"]*c-prodInfoV2[^"]*"[^>]*>(.*?)</div></div></div></a>'
    )
    matches = re.findall(pattern, html, re.DOTALL)

    for block in matches:
        id_match = re.search(r'<a[^>]+href="/prod/([^"]+)"', block)
        name_match = re.search(
            r'<div class="c-prodInfoV2__title"[^>]*title="(.*?)"', block
        )
        price_match = re.search(r'priceValue--m">\$(.*?)</div>', block)
        stars = len(
            re.findall(
                r'<div class="c-ratingIcon__item c-ratingIcon__item--sm is-active(?![^"]*is-half)[^"]*">',
                block,
            )
        )

        item: Product = {
            "id": id_match.group(1) if id_match else "N/A",
            "name": name_match.group(1) if name_match else "N/A",
            "price": int(price_match.group(1).replace(",", "")) if price_match else 0,
            "star": stars,
        }

        array.append(item)

    return array


# Task1 -> product IDs .txt
def generate_product_ids_txt(products: List[Product]):
    product_ids = [product["id"] for product in products]
    with open("products.txt", "w") as f:
        f.write("\n".join(product_ids))


# Task2 -> Create a file named best-products.txt and print product IDs with at least 1 review where average rating greater than 4.9
def generate_best_products_txt(products: List[Product]) -> None:
    best_products = [product["id"] for product in products if product["star"] == 5]
    with open("best-products.txt", "w") as f:
        f.write("\n".join(best_products))


# Task3 -> Calculate the average price of ASUS PCs with Intel i5 processor. Just print it in the console.
def calculate_average_price(products: List[Product]) -> None:
    i5_prices = [p["price"] for p in products if "i5" in p["name"]]

    if i5_prices:
        average_price = sum(i5_prices) / len(i5_prices)
        print(f"Average price of ASUS PCs with Intel i5 processor: {average_price}")
    else:
        print("No ASUS PCs with Intel i5 processor found.")


# Task4 -> We want to use z-score to standardize the prices of ASUS PCs where you can treat parsed data in Task 1 as statistical population.
def generate_z_score_csv(products: List[Product]) -> None:
    prices = [p["price"] for p in products]

    mean_price = sum(prices) / len(prices)
    variance = sum((x - mean_price) ** 2 for x in prices) / len(
        prices
    )  # population variance
    std_dev = math.sqrt(variance)

    if std_dev == 0:
        z_scores = [0 for _ in products]
    else:
        z_scores = [(p["price"] - mean_price) / std_dev for p in products]

    lines = []

    for p, z in zip(products, z_scores):
        lines.append(f"{p['id']},{p['price']},{z:.2f}")

    csv_content = "\n".join(lines)

    with open("standardization.csv", "w") as f:
        f.write(csv_content)


# 主程式
def main() -> None:

    base_url = "https://24h.pchome.com.tw"

    url = "https://24h.pchome.com.tw/store/DSAA31"
    response = urllib.request.urlopen(url)
    html = response.read().decode("utf-8")

    urls: list[str] = []
    products: list[Product] = []

    # step 1. 取得所有分頁的網址
    urls = get_urls(html, base_url, url)

    # step 2. 抓取每個分頁的商品
    for url in urls:
        response = urllib.request.urlopen(url)
        html = response.read().decode("utf-8")

        products = products + get_products(html)

    # step 3. 生成 Task1 product IDs .txt
    generate_product_ids_txt(products)

    # step 4. 生成 Task2 best-products.txt
    generate_best_products_txt(products)

    # step 5. 計算 Task3
    calculate_average_price(products)

    # step 6. 生成 Task4 z-score.csv
    generate_z_score_csv(products)


if __name__ == "__main__":
    main()
