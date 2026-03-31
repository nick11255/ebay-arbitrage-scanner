"""Discord bot — scans eBay for arbitrage deals and posts to a channel."""

import asyncio
import logging
import sys

import discord
from discord.ext import commands, tasks

import config
from ebay_api import search_items, close_session
from scraper import scrape_sold_comps, get_median, close_browser
from analyzer import calculate_profit, score_deal
from products import PRODUCTS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info(f"Bot ready: {bot.user}")
    if not scan_loop.is_running():
        scan_loop.start()


@tasks.loop(minutes=config.SCAN_INTERVAL)
async def scan_loop():
    """Scan all products, post deals above the score threshold."""
    channel = bot.get_channel(config.DISCORD_CHANNEL_ID)
    if not channel:
        log.error("Deals channel not found")
        return

    for product in PRODUCTS:
        try:
            items = await search_items(
                product["query"], max_price=product["max_price"]
            )
            if not items:
                continue

            prices = await scrape_sold_comps(product["query"])
            median_price = get_median(prices)
            if median_price <= 0:
                continue

            for item in items:
                buy_price = float(item.get("price", {}).get("value", 0))
                if buy_price <= 0:
                    continue

                seller = item.get("seller", {})
                feedback = float(seller.get("feedbackPercentage", "0") or "0")

                score = score_deal(buy_price, median_price, len(prices), feedback)
                info = calculate_profit(buy_price, median_price)

                if score >= config.MIN_SCORE and info["profit"] >= config.MIN_PROFIT:
                    embed = discord.Embed(
                        title=item.get("title", "Deal Found"),
                        url=item.get("itemWebUrl", ""),
                        color=0x2ECC71,
                    )
                    embed.add_field(name="Buy Price", value=f"${buy_price:.2f}")
                    embed.add_field(name="Median Sold", value=f"${median_price:.2f}")
                    embed.add_field(name="Est. Profit", value=f"${info['profit']:.2f}")
                    embed.add_field(name="Margin", value=f"{info['margin']:.1f}%")
                    embed.add_field(name="Score", value=f"{score}/100")
                    embed.add_field(name="Comps", value=str(len(prices)))
                    embed.set_footer(text=f"Fees: ${info['fees']:.2f} | Ship: ${info['shipping']:.2f}")
                    await channel.send(embed=embed)

            await asyncio.sleep(2)

        except Exception as e:
            log.error(f"Error scanning {product['name']}: {e}")
            continue


@scan_loop.before_loop
async def before_scan():
    await bot.wait_until_ready()


@bot.command()
async def lookup(ctx, *, query: str):
    """Look up a product: search eBay and show median sold price + profit."""
    await ctx.send(f"Searching for **{query}**...")

    items = await search_items(query, limit=5)
    if not items:
        await ctx.send("No active listings found.")
        return

    prices = await scrape_sold_comps(query)
    median_price = get_median(prices)

    if median_price <= 0:
        await ctx.send("No sold comps found.")
        return

    buy_price = float(items[0].get("price", {}).get("value", 0))
    info = calculate_profit(buy_price, median_price)

    await ctx.send(
        f"**{query}**\n"
        f"Lowest active listing: ${buy_price:.2f}\n"
        f"Median sold price: ${median_price:.2f} ({len(prices)} comps)\n"
        f"Estimated profit: ${info['profit']:.2f} ({info['margin']:.1f}% margin)\n"
        f"eBay fees: ${info['fees']:.2f} | Shipping: ${info['shipping']:.2f}"
    )


def main():
    if not config.DISCORD_TOKEN:
        print("Set DISCORD_TOKEN in your .env file")
        sys.exit(1)
    if not config.EBAY_APP_ID:
        print("Warning: EBAY_APP_ID not set, API calls will fail")

    try:
        bot.run(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
