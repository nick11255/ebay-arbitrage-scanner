"""eBay Arbitrage Scanner - Discord Bot Entry Point.

Run with: python bot.py
"""

import asyncio
import logging
import sys

import discord
from discord.ext import commands, tasks

import config
from ebay_api import EbayAPI
from scraper import scrape_sold_comps, analyze_comps, close_browser
from analyzer import score_deal, refine_comps
from description import check_red_flags
from seller import score_seller
from tracker import record_scan
from rotation import get_next_scan_group, advance_group
from discord_commands import setup_commands
from discord_ui import setup_claim_handler, setup_onboarding, post_deal

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)
ebay = EbayAPI()


@bot.event
async def on_ready():
    logger.info(f"Bot connected as {bot.user} (ID: {bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} server(s)")

    if not scan_loop.is_running():
        scan_loop.start()
        logger.info("Scan loop started")


@tasks.loop(minutes=config.SCAN_INTERVAL_MINUTES)
async def scan_loop():
    """Main scan rotation loop."""
    if not ebay.can_make_call():
        logger.warning("Daily API limit reached, skipping scan cycle")
        return

    group_num, products = get_next_scan_group()
    logger.info(f"Starting scan cycle: Group {group_num} ({len(products)} products)")

    deals_found = 0

    for product in products:
        if not ebay.can_make_call():
            logger.warning("API limit reached mid-scan, stopping")
            break

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
                record_scan(product["name"], 0, 0)
                continue

            # Get sold comps for price comparison
            comps = await scrape_sold_comps(
                product["query"],
                model_keywords=product.get("model_keywords"),
                min_price=product.get("min_price"),
                max_price=product.get("max_price"),
                max_results=15,
            )

            # Refine comps to match model
            comps = refine_comps(comps, product)
            comp_stats = analyze_comps(comps)

            product_deals = 0

            for item in items:
                price_info = item.get("price", {})
                buy_price = float(price_info.get("value", 0))
                if buy_price <= 0:
                    continue

                # Check description red flags
                title = item.get("title", "")
                red_flags = check_red_flags(title)

                # Score seller
                seller_info = item.get("seller", {})
                seller_result = score_seller(seller_info) if seller_info else {"score": 50}

                # Score the deal
                deal = score_deal(
                    buy_price=buy_price,
                    comp_stats=comp_stats,
                    seller_score=seller_result["score"],
                    red_flags=red_flags["count"],
                )

                # Filter by minimum thresholds
                profit = deal["profit_info"].get("profit", 0)
                margin = deal["profit_info"].get("margin", 0)

                if (
                    profit >= config.MIN_PROFIT
                    and margin >= config.MIN_MARGIN
                    and deal["channel"] != "skip"
                ):
                    await post_deal(bot, item, deal, product["name"])
                    product_deals += 1
                    deals_found += 1

                    # Small delay between posts
                    await asyncio.sleep(1)

            record_scan(product["name"], len(items), product_deals)

            # Rate limit between products
            await asyncio.sleep(2)

        except Exception as e:
            logger.error(f"Error scanning {product['name']}: {e}")
            continue

    advance_group()
    logger.info(
        f"Scan cycle complete: Group {group_num}, "
        f"{deals_found} deals found"
    )


@scan_loop.before_loop
async def before_scan():
    await bot.wait_until_ready()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: `{error.param.name}`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Invalid argument. Check your command syntax.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        logger.error(f"Command error: {error}")
        await ctx.send("An error occurred. Check the logs.")


# Register all components
setup_commands(bot, ebay)
setup_claim_handler(bot)
setup_onboarding(bot)


async def shutdown():
    """Clean shutdown."""
    logger.info("Shutting down...")
    await ebay.close()
    await close_browser()
    await bot.close()


def main():
    if not config.DISCORD_TOKEN:
        print("ERROR: DISCORD_TOKEN not set in .env file")
        print("Copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    if not config.EBAY_APP_ID:
        print("WARNING: EBAY_APP_ID not set. API calls will fail.")

    logger.info("Starting eBay Arbitrage Scanner Bot...")
    try:
        bot.run(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise


if __name__ == "__main__":
    main()
