# eBay Arbitrage Scanner

A Discord bot that finds profitable eBay deals by comparing active listing prices against recent sold prices.

## How It Works

```
                         eBay API
                            |
                     Search active listings
                     (price, title, seller)
                            |
                      Playwright Scraper
                            |
                     Scrape sold listings
                     (recent sold prices)
                            |
                      Profit Calculator
                            |
                  sell price - buy price - fees
                  (13.25% eBay fee + shipping)
                            |
                       Deal Scorer
                            |
              Score 0-100 based on:
              - Profit margin (50 pts)
              - Number of comps (25 pts)
              - Seller feedback (25 pts)
                            |
                    Score >= 60?
                   /           \
                 Yes            No
                  |              |
            Post to Discord    Skip
```

## Files

| File | Purpose |
|------|---------|
| `config.py` | Environment variables and constants |
| `ebay_api.py` | OAuth2 authentication and eBay search |
| `scraper.py` | Playwright scraper for sold listing prices |
| `analyzer.py` | Profit calculation and deal scoring |
| `products.py` | List of 20 products to scan |
| `bot.py` | Discord bot with scan loop and `!lookup` command |

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Create a `.env` file:
   ```
   EBAY_APP_ID=your_app_id
   EBAY_CERT_ID=your_cert_id
   DISCORD_TOKEN=your_bot_token
   DISCORD_CHANNEL_ID=your_channel_id
   ```

3. Run the bot:
   ```
   python bot.py
   ```

The bot scans all 20 products every 30 minutes. Deals scoring 60+ are posted to your Discord channel. Use `!lookup [query]` to manually check any product.

## Key Concepts

- **Comps**: Recent sold listings used to estimate market value
- **Median sold price**: The middle value of all comp prices (more reliable than average)
- **eBay fees**: 13.25% final value fee + $0.30 per order
- **Margin**: profit / sell price as a percentage
- **Score**: Weighted score combining margin, comp count, and seller reputation
