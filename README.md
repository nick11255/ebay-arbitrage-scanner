# eBay Arbitrage Scanner

A bot that finds profitable eBay arbitrage opportunities by comparing live listing prices against historical sold data. It scans 185 products across gaming, Apple, PC components, and collectibles — then scores deals and posts them to Discord.

## How It Works

1. **Search** — Queries the eBay Browse API for active listings across 8 rotating product groups
2. **Compare** — Scrapes eBay sold/completed listings with Playwright to get real market values
3. **Score** — Rates each deal 0–100 based on profit margin, sell-through rate, comp confidence, seller trust, and listing red flags
4. **Alert** — Posts qualifying deals to Discord with full profit breakdowns

## Quick Start

```bash
# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Configure
cp .env.example .env
# Edit .env with your eBay API and Discord credentials
```

## Configuration

Copy `.env.example` and fill in:

| Variable | Description |
|----------|-------------|
| `EBAY_APP_ID` | eBay developer app ID |
| `EBAY_CERT_ID` | eBay developer cert ID |
| `EBAY_MARKETPLACE` | Marketplace (default: `EBAY_US`) |
| `DISCORD_TOKEN` | Discord bot token |
| `DISCORD_DEALS_CHANNEL` | Channel ID for standard deals |
| `DISCORD_HOT_DEALS_CHANNEL` | Channel ID for hot deals (score 80+) |
| `DISCORD_LOG_CHANNEL` | Channel ID for scan logs |
| `DAILY_API_LIMIT` | eBay API call limit (default: `5000`) |
| `SCAN_INTERVAL_MINUTES` | Minutes between scans (default: `30`) |
| `MIN_PROFIT` | Minimum profit in dollars (default: `10.00`) |
| `MIN_MARGIN` | Minimum margin percentage (default: `15.0`) |

## Usage

### Discord Bot (continuous monitoring)

```bash
python bot.py
```

Runs a scan loop on the configured interval and posts deals to Discord automatically.

### Standalone Scanner

```bash
# Single scan
python scanner.py

# Continuous mode
python scanner.py --continuous
```

### Docker

```bash
docker-compose up
```

Launches the bot with a Redis instance for caching. Data is persisted via a Docker volume.

## Architecture

```
bot.py / scanner.py     Entry points
├── ebay_api.py         eBay Browse API client (OAuth2, rate limiting)
├── scraper.py          Playwright sold-price scraper
├── analyzer.py         Deal scoring engine (0–100)
├── products.py         185 products in 8 rotation groups
├── rotation.py         Group rotation to stay within API budget
├── cache.py            Redis cache with in-memory fallback
├── seller.py           Seller trust scoring
├── description.py      Red flag detection (31+ keywords)
├── tracker.py          Product health & analytics
├── config.py           Environment-based configuration
├── types_.py           TypedDict definitions
├── discord_commands.py Slash commands (stats, claims, trades)
└── discord_ui.py       Discord embeds and UI
```

## Deal Scoring

Each deal is scored on five factors:

| Factor | Weight | What it measures |
|--------|--------|------------------|
| Profit margin | 35 pts | How much you stand to make after fees |
| Sell-through rate | 25 pts | How quickly similar items sell |
| Comp confidence | 15 pts | Number and quality of comparable sales |
| Seller trust | 15 pts | Feedback score, top-rated status, return policy |
| Listing quality | 10 pts | Absence of red flags (as-is, for parts, etc.) |

**Grades:** A+ (90+), A (80+), B (70+), C (60+), D (50+), F (<50)

Fees are calculated as 13.25% + $0.30 per order, plus estimated shipping.

## Testing

```bash
python -m pytest tests/ -v
```

Tests cover deal scoring, fee calculation, web scraping, caching, and analytics.

## CI

GitHub Actions runs on every push and PR to `main`:

1. Python syntax check
2. Lint with flake8
3. Unit tests with pytest

## Tech Stack

- **Python 3.11**
- **discord.py** — Bot framework
- **aiohttp** — Async HTTP
- **Playwright** — Browser automation for scraping
- **Redis** — Caching (with in-memory fallback)
- **pytest** — Testing
- **Docker** — Containerization
