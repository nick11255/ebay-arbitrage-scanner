"""Discord bot commands for eBay arbitrage scanner."""

import logging
import discord
from discord.ext import commands

from ebay_api import EbayAPI
from scraper import scrape_sold_comps, analyze_comps
from analyzer import calculate_profit, score_deal, refine_comps
from seller import score_seller, format_seller_report
from description import check_red_flags, verify_listing, format_risk_report
from tracker import (
    log_purchase, log_sale, get_user_stats, format_user_stats,
    format_product_health, format_autopurge,
)
from rotation import format_rotation_status, estimate_daily_calls
from products import get_product_by_name, get_group_summary, PRODUCTS
import config

logger = logging.getLogger(__name__)


def setup_commands(bot: commands.Bot, ebay: EbayAPI):
    """Register all bot commands."""

    @bot.command(name="lookup")
    async def lookup(ctx, *, query: str):
        """Search eBay for active listings."""
        if not ebay.can_make_call():
            await ctx.send("Daily API limit reached. Try again tomorrow.")
            return

        async with ctx.typing():
            items = await ebay.search_items(query, limit=10)

        if not items:
            await ctx.send(f"No results found for: **{query}**")
            return

        embed = discord.Embed(
            title=f"eBay Search: {query}",
            color=discord.Color.blue(),
        )

        for item in items[:8]:
            price = item.get("price", {})
            price_str = f"${float(price.get('value', 0)):.2f}" if price else "N/A"
            condition = item.get("condition", "Unknown")
            link = item.get("itemWebUrl", "")

            embed.add_field(
                name=item.get("title", "Unknown")[:60],
                value=f"{price_str} | {condition}\n[View]({link})",
                inline=False,
            )

        usage = ebay.get_api_usage()
        embed.set_footer(text=f"API: {usage['used']}/{usage['limit']} today")
        await ctx.send(embed=embed)

    @bot.command(name="comps")
    async def comps(ctx, *, query: str):
        """Get sold comp data for a product."""
        async with ctx.typing():
            raw_comps = await scrape_sold_comps(query, max_results=20)
            stats = analyze_comps(raw_comps)

        if not raw_comps:
            await ctx.send(f"No sold comps found for: **{query}**")
            return

        embed = discord.Embed(
            title=f"Sold Comps: {query}",
            color=discord.Color.green(),
        )
        embed.add_field(name="Avg Price", value=f"${stats['avg_price']:.2f}", inline=True)
        embed.add_field(name="Median", value=f"${stats['median_price']:.2f}", inline=True)
        embed.add_field(name="Range", value=f"${stats['min_price']:.2f} - ${stats['max_price']:.2f}", inline=True)
        embed.add_field(name="Comps Found", value=str(stats['num_comps']), inline=True)
        embed.add_field(name="Sell-Through", value=stats['sell_through'].upper(), inline=True)

        # Show recent comps
        recent = raw_comps[:5]
        if recent:
            comp_lines = []
            for c in recent:
                date_str = f" ({c['date']})" if c.get("date") else ""
                comp_lines.append(f"${c['price']:.2f}{date_str} - {c['title'][:50]}")
            embed.add_field(
                name="Recent Sales",
                value="\n".join(comp_lines),
                inline=False,
            )

        await ctx.send(embed=embed)

    @bot.command(name="seller")
    async def seller_cmd(ctx, *, seller_id: str):
        """Check seller trust score."""
        if not ebay.can_make_call():
            await ctx.send("Daily API limit reached.")
            return

        # Note: Browse API doesn't have a direct seller endpoint,
        # but we can get seller info from item details
        await ctx.send(
            f"**Seller Lookup: {seller_id}**\n"
            f"Tip: Use `!risk <item_url>` to check seller info from a specific listing. "
            f"The Browse API requires an item context to pull seller data."
        )

    @bot.command(name="calc")
    async def calc(ctx, buy_price: float, sell_price: float):
        """Calculate profit for a potential deal."""
        result = calculate_profit(buy_price, sell_price)

        color = discord.Color.green() if result["profit"] > 0 else discord.Color.red()
        embed = discord.Embed(title="Profit Calculator", color=color)
        embed.add_field(name="Buy Price", value=f"${result['buy_price']:.2f}", inline=True)
        embed.add_field(name="Sell Price", value=f"${result['sell_price']:.2f}", inline=True)
        embed.add_field(name="Profit", value=f"${result['profit']:.2f}", inline=True)
        embed.add_field(name="Margin", value=f"{result['margin']:.1f}%", inline=True)
        embed.add_field(name="ROI", value=f"{result['roi']:.1f}%", inline=True)
        embed.add_field(name="eBay Fee", value=f"${result['ebay_fee']:.2f}", inline=True)
        embed.add_field(name="Shipping Est", value=f"${result['shipping']:.2f}", inline=True)

        await ctx.send(embed=embed)

    @bot.command(name="settings")
    async def settings(ctx):
        """Show current bot settings."""
        estimate = estimate_daily_calls()

        embed = discord.Embed(title="Scanner Settings", color=discord.Color.gold())
        embed.add_field(name="Min Profit", value=f"${config.MIN_PROFIT:.2f}", inline=True)
        embed.add_field(name="Min Margin", value=f"{config.MIN_MARGIN:.1f}%", inline=True)
        embed.add_field(name="Location", value=config.DEFAULT_LOCATION, inline=True)
        embed.add_field(name="API Limit", value=f"{config.DAILY_API_LIMIT}/day", inline=True)
        embed.add_field(name="Scan Interval", value=f"{config.SCAN_INTERVAL_MINUTES} min", inline=True)
        embed.add_field(name="Scan Groups", value=str(config.NUM_GROUPS), inline=True)
        embed.add_field(name="Total Products", value=str(len(PRODUCTS)), inline=True)
        embed.add_field(
            name="Est. Daily Calls",
            value=f"~{estimate['estimated_daily_calls']}",
            inline=True,
        )
        embed.add_field(
            name="eBay Fee",
            value=f"{config.EBAY_FEE_PERCENT}% + ${config.EBAY_FEE_FIXED}",
            inline=True,
        )

        await ctx.send(embed=embed)

    @bot.command(name="setlocation")
    async def setlocation(ctx, zipcode: str):
        """Set default location for shipping estimates."""
        if not zipcode.isdigit() or len(zipcode) != 5:
            await ctx.send("Please provide a valid 5-digit ZIP code.")
            return
        config.DEFAULT_LOCATION = zipcode
        await ctx.send(f"Location updated to: **{zipcode}**")

    @bot.command(name="setminprofit")
    async def setminprofit(ctx, amount: float):
        """Set minimum profit threshold."""
        if amount < 0:
            await ctx.send("Minimum profit must be positive.")
            return
        config.MIN_PROFIT = amount
        await ctx.send(f"Minimum profit set to: **${amount:.2f}**")

    @bot.command(name="setminmargin")
    async def setminmargin(ctx, percent: float):
        """Set minimum margin threshold."""
        if percent < 0 or percent > 100:
            await ctx.send("Margin must be between 0 and 100.")
            return
        config.MIN_MARGIN = percent
        await ctx.send(f"Minimum margin set to: **{percent:.1f}%**")

    @bot.command(name="risk")
    async def risk(ctx, *, item_query: str):
        """Risk assessment for a listing."""
        async with ctx.typing():
            # Search for the item
            if not ebay.can_make_call():
                await ctx.send("Daily API limit reached.")
                return

            items = await ebay.search_items(item_query, limit=1)
            if not items:
                await ctx.send(f"No listing found for: **{item_query}**")
                return

            item = items[0]
            title = item.get("title", "")
            condition = item.get("condition", "Unknown")

            # Check red flags in title (description requires item detail call)
            red_flags = check_red_flags(title)

            # Seller info from search results
            seller_info = item.get("seller", {})
            seller_result = score_seller(seller_info) if seller_info else None

        embed = discord.Embed(
            title=f"Risk Assessment",
            description=title[:100],
            color=(
                discord.Color.green() if red_flags["count"] == 0
                else discord.Color.orange() if red_flags["count"] <= 2
                else discord.Color.red()
            ),
        )

        embed.add_field(
            name="Red Flags",
            value=f"{red_flags['count']} found ({red_flags['risk_level'].upper()})",
            inline=True,
        )
        embed.add_field(name="Condition", value=condition, inline=True)

        if red_flags["flags"]:
            flag_text = "\n".join(
                f"- {f['keyword']}" for f in red_flags["flags"][:5]
            )
            embed.add_field(name="Flags Found", value=flag_text, inline=False)

        if seller_result:
            embed.add_field(
                name="Seller Score",
                value=f"{seller_result['score']}/100 ({seller_result['grade']})",
                inline=True,
            )
            embed.add_field(
                name="Seller Risk",
                value=seller_result["risk_level"].upper(),
                inline=True,
            )

        await ctx.send(embed=embed)

    @bot.command(name="bought")
    async def bought(ctx, price: float, *, item: str):
        """Log a purchase. Usage: !bought <price> <item name>"""
        entry = log_purchase(str(ctx.author.id), item, price)
        await ctx.send(
            f"Logged purchase: **{item}** for **${price:.2f}**\n"
            f"Use `!sold {price} {item}` when you sell it."
        )

    @bot.command(name="sold")
    async def sold(ctx, price: float, *, item: str):
        """Log a sale. Usage: !sold <price> <item name>"""
        entry = log_sale(str(ctx.author.id), item, price)
        await ctx.send(f"Logged sale: **{item}** for **${price:.2f}**")

    @bot.command(name="stats")
    async def stats(ctx):
        """Show your trading P&L stats."""
        report = format_user_stats(str(ctx.author.id), ctx.author.display_name)
        await ctx.send(report)

    @bot.command(name="producthealth")
    async def producthealth(ctx):
        """Show product performance report."""
        report = format_product_health()
        # Split if too long
        if len(report) > 2000:
            chunks = [report[i:i+1900] for i in range(0, len(report), 1900)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(report)

    @bot.command(name="autopurge")
    async def autopurge(ctx):
        """Suggest underperforming products to remove."""
        report = format_autopurge()
        await ctx.send(report)

    @bot.command(name="suggest")
    async def suggest(ctx):
        """Suggest new products to add based on trends."""
        embed = discord.Embed(
            title="Product Suggestions",
            description="Based on current market trends and category gaps:",
            color=discord.Color.purple(),
        )

        # Analyze current category distribution
        categories = {}
        for p in PRODUCTS:
            cat = p["category"]
            categories[cat] = categories.get(cat, 0) + 1

        cat_text = "\n".join(
            f"**{cat}**: {count} products"
            for cat, count in sorted(categories.items(), key=lambda x: -x[1])
        )
        embed.add_field(name="Current Distribution", value=cat_text, inline=False)

        suggestions = [
            "Consider adding more **tools** (Dyson, Milwaukee, DeWalt)",
            "**Vintage electronics** (Walkman, retro audio) trending up",
            "**Limited edition collaborations** in streetwear",
            "**Board games** — sealed out-of-print titles have strong margins",
            "**Vinyl records** — limited pressings, colored vinyl",
        ]
        embed.add_field(
            name="Suggestions",
            value="\n".join(f"- {s}" for s in suggestions),
            inline=False,
        )

        await ctx.send(embed=embed)

    @bot.command(name="apistatus")
    async def apistatus(ctx):
        """Show API usage and rate limit status."""
        usage = ebay.get_api_usage()
        rotation = format_rotation_status()

        embed = discord.Embed(
            title="API Status",
            color=(
                discord.Color.green() if usage["percent"] < 75
                else discord.Color.orange() if usage["percent"] < 90
                else discord.Color.red()
            ),
        )
        embed.add_field(name="Calls Today", value=str(usage["used"]), inline=True)
        embed.add_field(name="Remaining", value=str(usage["remaining"]), inline=True)
        embed.add_field(name="Usage", value=f"{usage['percent']}%", inline=True)
        embed.add_field(name="Daily Limit", value=str(usage["limit"]), inline=True)

        await ctx.send(embed=embed)
        await ctx.send(f"```\n{rotation}\n```")
