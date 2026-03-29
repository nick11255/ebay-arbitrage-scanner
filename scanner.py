"""eBay Arbitrage Scanner - Standalone CLI Entry Point.

Run with: python scanner.py
Can also be run via cron for automated scanning.
"""

import asyncio
import logging
import sys

import config
from ebay_api import EbayAPI
from scraper import scrape_sold_comps, analyze_comps, close_browser
from analyzer import score_deal, refine_comps, format_deal_summary
from description import check_red_flags
from seller import score_seller
from tracker import record_scan
from rotation import (
    get_next_scan_group, advance_group,
    format_rotation_status, estimate_daily_calls,
)
from products import get_group_summary

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def print_header():
    print("=" * 60)
    print("  eBay Arbitrage Scanner")
    print("=" * 60)
    print()
    print(get_group_summary())
    print()
    estimate = estimate_daily_calls()
    print(f"API Budget: ~{estimate['estimated_daily_calls']}/{config.DAILY_API_LIMIT} calls/day")
    print(f"Min Profit: ${config.MIN_PROFIT:.2f} | Min Margin: {config.MIN_MARGIN:.1f}%")
    print()


async def run_scan_cycle(ebay: EbayAPI):
    """Run one scan cycle on the next group."""
    group_num, products = get_next_scan_group()
    print(f"\n{'='*60}")
    print(f"  Scanning Group {group_num} ({len(products)} products)")
    print(f"{'='*60}\n")

    deals = []

    for i, product in enumerate(products, 1):
        if not ebay.can_make_call():
            print("\n[!] Daily API limit reached, stopping scan")
            break

        print(f"[{i}/{len(products)}] Scanning: {product['name']}...", end=" ")

        try:
            # Search active listings
            items = await ebay.search_with_exclusions(
                query=product["query"],
                exclude_keywords=product.get("exclude", []),
                min_price=product.get("min_price"),
                max_price=product.get("max_price"),
                limit=20,
            )

            if not items:
                print(f"0 listings")
                record_scan(product["name"], 0, 0)
                continue

            print(f"{len(items)} listings", end=" ")

            # Get sold comps
            comps = await scrape_sold_comps(
                product["query"],
                model_keywords=product.get("model_keywords"),
                min_price=product.get("min_price"),
                max_price=product.get("max_price"),
                max_results=15,
            )
            comps = refine_comps(comps, product)
            comp_stats = analyze_comps(comps)

            print(f"| {comp_stats['num_comps']} comps (avg ${comp_stats['avg_price']:.2f})")

            product_deals = 0

            for item in items:
                price_info = item.get("price", {})
                buy_price = float(price_info.get("value", 0))
                if buy_price <= 0:
                    continue

                red_flags = check_red_flags(item.get("title", ""))
                seller_info = item.get("seller", {})
                seller_result = score_seller(seller_info) if seller_info else {"score": 50}

                deal = score_deal(
                    buy_price=buy_price,
                    comp_stats=comp_stats,
                    seller_score=seller_result["score"],
                    red_flags=red_flags["count"],
                )

                profit = deal["profit_info"].get("profit", 0)
                margin = deal["profit_info"].get("margin", 0)

                if (
                    profit >= config.MIN_PROFIT
                    and margin >= config.MIN_MARGIN
                    and deal["channel"] != "skip"
                ):
                    deals.append((item, deal, product["name"]))
                    product_deals += 1

            if product_deals > 0:
                print(f"    -> {product_deals} deal(s) found!")

            record_scan(product["name"], len(items), product_deals)
            await asyncio.sleep(2)

        except Exception as e:
            print(f"ERROR: {e}")
            logger.error(f"Error scanning {product['name']}: {e}")
            continue

    advance_group()

    # Print deal summary
    print(f"\n{'='*60}")
    print(f"  Scan Complete: {len(deals)} Deals Found")
    print(f"{'='*60}\n")

    if deals:
        for item, deal, name in sorted(deals, key=lambda x: -x[1]["score"]):
            channel = deal["channel"].upper()
            print(f"[{channel}] {format_deal_summary(item, deal)}")
            print(f"  Link: {item.get('itemWebUrl', 'N/A')}")
            print()
    else:
        print("No deals met the minimum profit/margin thresholds this cycle.")

    # Print API usage
    usage = ebay.get_api_usage()
    print(f"\nAPI Usage: {usage['used']}/{usage['limit']} ({usage['percent']}%)")

    return deals


async def main():
    if not config.EBAY_APP_ID:
        print("ERROR: EBAY_APP_ID not set in .env file")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    print_header()

    ebay = EbayAPI()
    try:
        if "--continuous" in sys.argv:
            print("Running in continuous mode (Ctrl+C to stop)\n")
            while True:
                await run_scan_cycle(ebay)
                print(
                    f"\nNext scan in {config.SCAN_INTERVAL_MINUTES} minutes...\n"
                )
                await asyncio.sleep(config.SCAN_INTERVAL_MINUTES * 60)
        else:
            await run_scan_cycle(ebay)
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
    finally:
        await ebay.close()
        await close_browser()


if __name__ == "__main__":
    asyncio.run(main())
