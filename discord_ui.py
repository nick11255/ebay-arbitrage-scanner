"""Discord UI components: deal embeds, claim system, onboarding DMs."""

import logging
import discord
from discord.ext import commands

from analyzer import calculate_profit
from tracker import record_claim
import config

logger = logging.getLogger(__name__)

# Claim reaction emoji
CLAIM_EMOJI = "\U0001f4b0"  # money bag
PASS_EMOJI = "\u274c"  # red X

# Track active claims: message_id -> deal info
active_claims: dict[int, dict] = {}


def get_score_color(score: int) -> discord.Color:
    """Get embed color based on deal score."""
    if score >= 80:
        return discord.Color.gold()
    elif score >= 60:
        return discord.Color.green()
    elif score >= 40:
        return discord.Color.orange()
    else:
        return discord.Color.red()


def create_deal_embed(item: dict, deal: dict, product_name: str = "") -> discord.Embed:
    """Create a rich embed for a deal alert.

    Args:
        item: eBay item dict from search results
        deal: Deal score result from analyzer
        product_name: Display name from product database
    """
    profit = deal["profit_info"]
    score = deal["score"]
    grade = deal["grade"]

    title = item.get("title", "Unknown Item")[:100]
    url = item.get("itemWebUrl", "")
    image = item.get("image", {}).get("imageUrl", "")

    embed = discord.Embed(
        title=f"[{grade}] {title}",
        url=url if url else None,
        color=get_score_color(score),
    )

    if product_name:
        embed.set_author(name=product_name)

    if image:
        embed.set_thumbnail(url=image)

    # Price info
    embed.add_field(
        name="Buy Now",
        value=f"**${profit['buy_price']:.2f}**",
        inline=True,
    )
    embed.add_field(
        name="Est. Sell",
        value=f"${profit['sell_price']:.2f}",
        inline=True,
    )
    embed.add_field(
        name="Profit",
        value=f"**${profit['profit']:.2f}** ({profit['margin']:.1f}%)",
        inline=True,
    )

    # Score breakdown
    breakdown = deal.get("breakdown", {})
    score_text = (
        f"Margin: {breakdown.get('margin', 0)}/35 | "
        f"Sell-Through: {breakdown.get('sell_through', 0)}/25\n"
        f"Comps: {breakdown.get('comp_confidence', 0)}/15 | "
        f"Seller: {breakdown.get('seller_trust', 0)}/15 | "
        f"Desc: {breakdown.get('description', 0)}/10"
    )
    embed.add_field(
        name=f"Score: {score}/100",
        value=score_text,
        inline=False,
    )

    # Fees
    embed.add_field(
        name="Fees",
        value=f"eBay: ${profit['ebay_fee']:.2f} | Ship: ${profit['shipping']:.2f}",
        inline=True,
    )
    embed.add_field(
        name="ROI",
        value=f"{profit['roi']:.1f}%",
        inline=True,
    )

    # Condition and seller
    condition = item.get("condition", "N/A")
    seller = item.get("seller", {})
    seller_name = seller.get("username", "Unknown")
    feedback = seller.get("feedbackPercentage", "N/A")

    embed.add_field(
        name="Details",
        value=f"Condition: {condition} | Seller: {seller_name} ({feedback}%)",
        inline=False,
    )

    embed.set_footer(text=f"React {CLAIM_EMOJI} to claim this deal")

    return embed


async def post_deal(
    bot: commands.Bot,
    item: dict,
    deal: dict,
    product_name: str = "",
):
    """Post a deal to the appropriate Discord channel with claim reactions.

    Args:
        bot: Discord bot instance
        item: eBay item dict
        deal: Scored deal dict from analyzer
        product_name: Product database name
    """
    channel_id = (
        config.DISCORD_HOT_DEALS_CHANNEL
        if deal["channel"] == "hot_deals"
        else config.DISCORD_DEALS_CHANNEL
    )

    if channel_id == 0:
        logger.warning("No deals channel configured")
        return

    channel = bot.get_channel(channel_id)
    if not channel:
        logger.error(f"Could not find channel {channel_id}")
        return

    embed = create_deal_embed(item, deal, product_name)
    message = await channel.send(embed=embed)

    # Add claim reactions
    await message.add_reaction(CLAIM_EMOJI)
    await message.add_reaction(PASS_EMOJI)

    # Track the claim
    active_claims[message.id] = {
        "item": item,
        "deal": deal,
        "product_name": product_name,
        "claimed_by": None,
    }

    logger.info(
        f"Posted deal: {item.get('title', '')[:50]} "
        f"(Score: {deal['score']}, Channel: {deal['channel']})"
    )


def setup_claim_handler(bot: commands.Bot):
    """Set up the reaction-based claim system."""

    @bot.event
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        if payload.user_id == bot.user.id:
            return

        if payload.message_id not in active_claims:
            return

        claim = active_claims[payload.message_id]
        emoji = str(payload.emoji)

        if emoji == CLAIM_EMOJI and claim["claimed_by"] is None:
            claim["claimed_by"] = payload.user_id

            channel = bot.get_channel(payload.channel_id)
            if channel:
                user = bot.get_user(payload.user_id)
                username = user.display_name if user else f"User {payload.user_id}"

                await channel.send(
                    f"**CLAIMED** by {username}! "
                    f"Deal: {claim['item'].get('title', '')[:60]}"
                )

                # Record the claim for product health
                if claim["product_name"]:
                    record_claim(claim["product_name"])

                logger.info(f"Deal claimed by {username}")


def setup_onboarding(bot: commands.Bot):
    """Set up new member onboarding DMs."""

    @bot.event
    async def on_member_join(member: discord.Member):
        try:
            embed = discord.Embed(
                title="Welcome to the eBay Arbitrage Scanner!",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Getting Started",
                value=(
                    "This bot scans eBay for profitable arbitrage deals. "
                    "Here's how to use it:"
                ),
                inline=False,
            )
            embed.add_field(
                name="Key Commands",
                value=(
                    "`!lookup <query>` - Search eBay listings\n"
                    "`!comps <query>` - Check sold prices\n"
                    "`!calc <buy> <sell>` - Calculate profit\n"
                    "`!risk <query>` - Risk assessment\n"
                    "`!stats` - Your P&L stats\n"
                    "`!settings` - View bot settings"
                ),
                inline=False,
            )
            embed.add_field(
                name="Deal Claims",
                value=(
                    f"When a deal is posted, react with {CLAIM_EMOJI} to claim it. "
                    f"First come, first served!"
                ),
                inline=False,
            )
            embed.add_field(
                name="Tracking Trades",
                value=(
                    "`!bought <price> <item>` - Log a purchase\n"
                    "`!sold <price> <item>` - Log a sale\n"
                    "The bot will match trades and track your P&L."
                ),
                inline=False,
            )

            await member.send(embed=embed)
            logger.info(f"Sent onboarding DM to {member.display_name}")
        except discord.Forbidden:
            logger.warning(
                f"Could not DM {member.display_name} (DMs disabled)"
            )
