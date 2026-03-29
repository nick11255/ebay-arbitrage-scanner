"""Discord bot commands for eBay arbitrage scanner."""

from __future__ import annotations

import csv
import io
import logging
import os
import tempfile
from typing import Optional

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
    get_dashboard_stats, get_posted_deals,
)
from rotation import (
    format_rotation_status, estimate_daily_calls,
    get_current_group, get_time_until_full_rotation,
)
from products import get_product_by_name, get_group_summary, PRODUCTS
from types_ import CompStats, DealScore, ProfitInfo, UserStats
import config

logger = logging.getLogger(__name__)


def setup_commands(bot: commands.Bot, ebay: EbayAPI) -> None:
    """Register all bot commands."""

    @bot.command(name="lookup")
    async def lookup(ctx: commands.Context, *, query: str) -> None:
        """Search eBay for active listings."""
        if not ebay.can_make_call():
            await ctx.send("Daily API limit reached. Try again tomorrow.")
            return

        async with ctx.typing():
            items: list[dict] = await ebay.search_items(query, limit=10)

        if not items:
            await ctx.send(f"No results found for: **{query}**")
            return

        embed = discord.Embed(
            title=f"eBay Search: {query}",
            color=discord.Color.blue(),
        )

        for item in items[:8]:
            price: dict = item.get("price", {})
            price_str: str = f"${float(price.get('value', 0)):.2f}" if price else "N/A"
            condition: str = item.get("condition", "Unknown")
            link: str = item.get("itemWebUrl", "")

            embed.add_field(
                name=item.get("title", "Unknown")[:60],
                value=f"{price_str} | {condition}\n[View]({link})",
                inline=False,
            )

        usage: dict = ebay.get_api_usage()
        embed.set_footer(text=f"API: {usage['used']}/{usage['limit']} today")
        await ctx.send(embed=embed)

    @bot.command(name="comps")
    async def comps(ctx: commands.Context, *, query: str) -> None:
        """Get sold comp data for a product."""
        async with ctx.typing():
            raw_comps: list[dict] = await scrape_sold_comps(query, max_results=20)
            stats: CompStats = analyze_comps(raw_comps)

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
        recent: list[dict] = raw_comps[:5]
        if recent:
            comp_lines: list[str] = []
            for c in recent:
                date_str: str = f" ({c['date']})" if c.get("date") else ""
                comp_lines.append(f"${c['price']:.2f}{date_str} - {c['title'][:50]}")
            embed.add_field(
                name="Recent Sales",
                value="\n".join(comp_lines),
                inline=False,
            )

        await ctx.send(embed=embed)

    @bot.command(name="seller")
    async def seller_cmd(ctx: commands.Context, *, seller_id: str) -> None:
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
    async def calc(ctx: commands.Context, buy_price: float, sell_price: float) -> None:
        """Calculate profit for a potential deal."""
        result: ProfitInfo = calculate_profit(buy_price, sell_price)

        color: discord.Color = discord.Color.green() if result["profit"] > 0 else discord.Color.red()
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
    async def settings(ctx: commands.Context) -> None:
        """Show current bot settings."""
        estimate: dict = estimate_daily_calls()

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
    async def setlocation(ctx: commands.Context, zipcode: str) -> None:
        """Set default location for shipping estimates."""
        if not zipcode.isdigit() or len(zipcode) != 5:
            await ctx.send("Please provide a valid 5-digit ZIP code.")
            return
        config.DEFAULT_LOCATION = zipcode
        await ctx.send(f"Location updated to: **{zipcode}**")

    @bot.command(name="setminprofit")
    async def setminprofit(ctx: commands.Context, amount: float) -> None:
        """Set minimum profit threshold."""
        if amount < 0:
            await ctx.send("Minimum profit must be positive.")
            return
        config.MIN_PROFIT = amount
        await ctx.send(f"Minimum profit set to: **${amount:.2f}**")

    @bot.command(name="setminmargin")
    async def setminmargin(ctx: commands.Context, percent: float) -> None:
        """Set minimum margin threshold."""
        if percent < 0 or percent > 100:
            await ctx.send("Margin must be between 0 and 100.")
            return
        config.MIN_MARGIN = percent
        await ctx.send(f"Minimum margin set to: **{percent:.1f}%**")

    @bot.command(name="risk")
    async def risk(ctx: commands.Context, *, item_query: str) -> None:
        """Risk assessment for a listing."""
        async with ctx.typing():
            # Search for the item
            if not ebay.can_make_call():
                await ctx.send("Daily API limit reached.")
                return

            items: list[dict] = await ebay.search_items(item_query, limit=1)
            if not items:
                await ctx.send(f"No listing found for: **{item_query}**")
                return

            item: dict = items[0]
            title: str = item.get("title", "")
            condition: str = item.get("condition", "Unknown")

            # Check red flags in title (description requires item detail call)
            red_flags = check_red_flags(title)

            # Seller info from search results
            seller_info: dict = item.get("seller", {})
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
            flag_text: str = "\n".join(
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
    async def bought(ctx: commands.Context, price: float, *, item: str) -> None:
        """Log a purchase. Usage: !bought <price> <item name>"""
        entry = log_purchase(str(ctx.author.id), item, price)
        await ctx.send(
            f"Logged purchase: **{item}** for **${price:.2f}**\n"
            f"Use `!sold {price} {item}` when you sell it."
        )

    @bot.command(name="sold")
    async def sold(ctx: commands.Context, price: float, *, item: str) -> None:
        """Log a sale. Usage: !sold <price> <item name>"""
        entry = log_sale(str(ctx.author.id), item, price)
        await ctx.send(f"Logged sale: **{item}** for **${price:.2f}**")

    @bot.command(name="stats")
    async def stats(ctx: commands.Context) -> None:
        """Show your trading P&L stats."""
        report: str = format_user_stats(str(ctx.author.id), ctx.author.display_name)
        await ctx.send(report)

    @bot.command(name="producthealth")
    async def producthealth(ctx: commands.Context) -> None:
        """Show product performance report."""
        report: str = format_product_health()
        # Split if too long
        if len(report) > 2000:
            chunks: list[str] = [report[i:i+1900] for i in range(0, len(report), 1900)]
            for chunk in chunks:
                await ctx.send(chunk)
        else:
            await ctx.send(report)

    @bot.command(name="autopurge")
    async def autopurge(ctx: commands.Context) -> None:
        """Suggest underperforming products to remove."""
        report: str = format_autopurge()
        await ctx.send(report)

    @bot.command(name="suggest")
    async def suggest(ctx: commands.Context) -> None:
        """Suggest new products to add based on trends."""
        embed = discord.Embed(
            title="Product Suggestions",
            description="Based on current market trends and category gaps:",
            color=discord.Color.purple(),
        )

        # Analyze current category distribution
        categories: dict[str, int] = {}
        for p in PRODUCTS:
            cat: str = p["category"]
            categories[cat] = categories.get(cat, 0) + 1

        cat_text: str = "\n".join(
            f"**{cat}**: {count} products"
            for cat, count in sorted(categories.items(), key=lambda x: -x[1])
        )
        embed.add_field(name="Current Distribution", value=cat_text, inline=False)

        suggestions: list[str] = [
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
    async def apistatus(ctx: commands.Context) -> None:
        """Show API usage and rate limit status."""
        usage: dict = ebay.get_api_usage()
        rotation: str = format_rotation_status()

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

    # ==================== NEW COMMANDS ====================

    @bot.command(name="dashboard")
    async def dashboard(ctx: commands.Context) -> None:
        """Analytics dashboard with scan/deal/category stats."""
        async with ctx.typing():
            stats: dict = get_dashboard_stats()
            usage: dict = ebay.get_api_usage()
            current_group: int = get_current_group()
            time_left: str = get_time_until_full_rotation()

        embed = discord.Embed(
            title="Analytics Dashboard",
            color=discord.Color.blurple(),
        )

        # Deals scanned
        embed.add_field(
            name="Deals Scanned",
            value=(
                f"Today: **{stats['scanned_today']:,}**\n"
                f"This week: **{stats['scanned_week']:,}**\n"
                f"All time: **{stats['scanned_all']:,}**"
            ),
            inline=True,
        )

        # Deals posted
        embed.add_field(
            name="Deals Posted",
            value=(
                f"Today: **{stats['posted_today']}**\n"
                f"This week: **{stats['posted_week']}**\n"
                f"All time: **{stats['posted_all']}**"
            ),
            inline=True,
        )

        # Average score
        embed.add_field(
            name="Avg Deal Score",
            value=f"**{stats['avg_score']:.1f}**/100" if stats['posted_all'] > 0 else "N/A",
            inline=True,
        )

        # Category breakdown
        if stats["categories"]:
            sorted_cats: list[tuple[str, int]] = sorted(
                stats["categories"].items(), key=lambda x: -x[1]
            )[:10]
            cat_text = "\n".join(
                f"{name}: **{count}**" for name, count in sorted_cats
            )
            embed.add_field(
                name="Deals by Product",
                value=cat_text or "No data",
                inline=False,
            )

        # Top 5 by hit rate
        if stats["top_5"]:
            top_text: str = "\n".join(
                f"{name}: **{ratio:.1f}%** ({deals} deals)"
                for name, ratio, deals in stats["top_5"]
            )
            embed.add_field(
                name="Top 5 (Hit Rate)",
                value=top_text,
                inline=True,
            )

        # Bottom 5 by hit rate (autopurge candidates)
        if stats["bottom_5"]:
            bottom_text: str = "\n".join(
                f"{name}: **{ratio:.1f}%** ({deals} deals)"
                for name, ratio, deals in stats["bottom_5"]
            )
            embed.add_field(
                name="Bottom 5 (Purge Candidates)",
                value=bottom_text,
                inline=True,
            )

        # API usage
        pct: float = usage["percent"]
        bar_filled: int = int(pct / 10)
        bar: str = "\u2588" * bar_filled + "\u2591" * (10 - bar_filled)
        embed.add_field(
            name="API Usage",
            value=f"{bar} {usage['used']}/{usage['limit']} ({pct:.1f}%)",
            inline=False,
        )

        # Rotation
        embed.add_field(
            name="Scan Rotation",
            value=f"Group **{current_group}** of {config.NUM_GROUPS} | Full rotation in **{time_left}**",
            inline=False,
        )

        await ctx.send(embed=embed)

    @bot.command(name="trend")
    async def trend(ctx: commands.Context, *, product_name: str) -> None:
        """Show price trend for a product from cached comp data."""
        async with ctx.typing():
            raw_comps: list[dict] = await scrape_sold_comps(
                product_name, max_results=20
            )
            current_stats: CompStats = analyze_comps(raw_comps)

        if not raw_comps:
            await ctx.send(f"No sold comp data found for: **{product_name}**")
            return

        # Split comps by condition
        new_comps: list[dict] = [
            c for c in raw_comps
            if "new" in c.get("condition", "").lower()
        ]
        used_comps: list[dict] = [
            c for c in raw_comps
            if any(
                t in c.get("condition", "").lower()
                for t in ("used", "pre-owned")
            )
        ]

        new_stats: CompStats = analyze_comps(new_comps) if new_comps else None
        used_stats: CompStats = analyze_comps(used_comps) if used_comps else None

        # Determine trend: compare first half vs second half of comps by date
        trend_emoji: str = "\u27a1\ufe0f"  # stable default
        if len(raw_comps) >= 6:
            mid: int = len(raw_comps) // 2
            older_prices: list[float] = [c["price"] for c in raw_comps[mid:]]
            newer_prices: list[float] = [c["price"] for c in raw_comps[:mid]]
            older_avg: float = sum(older_prices) / len(older_prices) if older_prices else 0
            newer_avg: float = sum(newer_prices) / len(newer_prices) if newer_prices else 0
            if newer_avg > older_avg * 1.05:
                trend_emoji = "\U0001f4c8"  # chart increasing
            elif newer_avg < older_avg * 0.95:
                trend_emoji = "\U0001f4c9"  # chart decreasing

        embed = discord.Embed(
            title=f"{trend_emoji} Trend: {product_name}",
            color=discord.Color.teal(),
        )

        # Overall median
        embed.add_field(
            name="Overall Median",
            value=f"**${current_stats['median_price']:.2f}**",
            inline=True,
        )
        embed.add_field(
            name="Comp Count",
            value=str(current_stats["num_comps"]),
            inline=True,
        )
        embed.add_field(
            name="Trend",
            value=f"{trend_emoji} {'Up' if '\U0001f4c8' in trend_emoji else 'Down' if '\U0001f4c9' in trend_emoji else 'Stable'}",
            inline=True,
        )

        # By condition
        if new_stats:
            embed.add_field(
                name="New Condition",
                value=(
                    f"Median: **${new_stats['median_price']:.2f}**\n"
                    f"Range: ${new_stats['min_price']:.2f} - ${new_stats['max_price']:.2f}\n"
                    f"Comps: {new_stats['num_comps']}"
                ),
                inline=True,
            )

        if used_stats:
            embed.add_field(
                name="Used/Pre-Owned",
                value=(
                    f"Median: **${used_stats['median_price']:.2f}**\n"
                    f"Range: ${used_stats['min_price']:.2f} - ${used_stats['max_price']:.2f}\n"
                    f"Comps: {used_stats['num_comps']}"
                ),
                inline=True,
            )

        embed.add_field(
            name="Price Range",
            value=f"${current_stats['min_price']:.2f} - ${current_stats['max_price']:.2f}",
            inline=True,
        )

        # Show last updated (most recent comp date)
        latest_date: str = "Unknown"
        for c in raw_comps:
            if c.get("date"):
                latest_date = c["date"]
                break
        embed.set_footer(text=f"Last updated: {latest_date}")

        await ctx.send(embed=embed)

    @bot.command(name="export")
    async def export(ctx: commands.Context) -> None:
        """Export all posted deals as a CSV file via DM."""
        deals: list[dict] = get_posted_deals()

        if not deals:
            await ctx.send("No posted deals to export yet.")
            return

        # Build CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "date", "product", "buy_price", "sold_median",
            "estimated_profit", "margin", "deal_score",
            "seller_rating", "url",
        ])

        for d in deals:
            writer.writerow([
                d.get("date", ""),
                d.get("product", ""),
                d.get("buy_price", ""),
                d.get("sold_median", ""),
                d.get("estimated_profit", ""),
                d.get("margin", ""),
                d.get("deal_score", ""),
                d.get("seller_rating", ""),
                d.get("url", ""),
            ])

        csv_bytes: bytes = output.getvalue().encode("utf-8")
        output.close()

        # Write to temp file
        tmp_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", suffix=".csv", prefix="deals_export_", delete=False
            ) as tmp:
                tmp.write(csv_bytes)
                tmp_path = tmp.name

            # DM the file to the user
            file = discord.File(tmp_path, filename="deals_export.csv")
            try:
                await ctx.author.send(
                    "Here's your deals export:", file=file
                )
                await ctx.send("Deals export sent to your DMs!")
            except discord.Forbidden:
                await ctx.send(
                    "I couldn't DM you. Please enable DMs from server members."
                )
        finally:
            # Clean up temp file
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)
