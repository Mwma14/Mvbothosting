# Cineverse Bot - Telegram Movie & Series Bot

## Overview
Cineverse Bot is a Telegram bot that provides a platform for users to search, browse, and access movies and series. The bot is completely free and includes admin controls and content management capabilities.

## Current State
- **Status**: Bot is successfully running in Replit environment
- **Language**: Python 3.11
- **Framework**: python-telegram-bot library
- **Database**: JSON file-based storage (movies_db.json, series_db.json)
- **Access**: Free for all users - no premium membership required

## Recent Changes
- **2025-10-20**: Enhanced deep link experience with intermediate retrieval button
  - Added Burmese language intermediate message for deep links
  - Users now see "⚜️ ဇာတ်ကားရပါပြီ ⚜️" message with copyright notice first
  - Added "⚜️ ဒီကိုနှိပ်ပြီး ဇာတ်ကားရယူပါ ⚜️" button for content retrieval
  - Deep links (e.g., /start mv_MovieName) now require button click before showing content
  - Created new callback handlers: CALLBACK_DEEPLINK_MOVIE and CALLBACK_DEEPLINK_SERIES
  - Added deeplink_retrieval_keyboard function for button generation
  - Implemented deeplink_retrieval_callback to process button clicks
- **2025-10-20**: Removed all premium and payment features - bot is now completely free
  - Removed premium membership system - bot is now free for all users
  - Removed payment methods and pricing information from config
  - Removed @premium_only decorators from all handlers
  - Removed /myplan command and premium user management
  - Removed premium user database functionality (deleted db_premium.py, premium_users_db.json)
  - Updated help text to reflect free access
  - Removed admin panel premium user management features
  - Cleaned up premium-related constants and imports from utils/constants.py, utils/decorators.py, and middleware.py
- **2025-10-20**: Secure bot token configuration
  - Removed hardcoded bot token from config.py
  - Bot token now stored securely in environment variables
- **2025-10-05**: GitHub import completed and configured for Replit
  - Installed Python 3.11 and python-telegram-bot dependencies
  - Updated config.py to use environment variables for BOT_TOKEN
  - Created .gitignore for Python project
  - Configured workflow to run the bot
  - Cleaned up duplicate mvbotgit folder and zip files

## Project Architecture

### Directory Structure
```
.
├── bot.py                 # Main bot entry point
├── config.py             # Configuration (BOT_TOKEN, ADMIN_IDS, channels)
├── middleware.py         # Force join channel middleware
├── database/             # JSON-based database
│   ├── db_handler.py     # Movie/Series CRUD operations
│   ├── movies_db.json    # Movies storage
│   └── series_db.json    # Series storage
├── handlers/             # Message and command handlers
│   ├── admin/            # Admin panel handlers
│   └── user/             # User-facing handlers (search, browsing, start)
├── keyboards/            # Telegram keyboard layouts
│   ├── inline.py         # Inline keyboards
│   └── reply.py          # Reply keyboards
└── utils/                # Helper utilities
    ├── constants.py      # Constants and callback patterns
    ├── decorators.py     # @admin_only decorator
    └── helpers.py        # Auto-deletion scheduler
```

### Key Features
1. **Content Management**: Browse and search movies/series by name, year, or category
2. **Free Access**: All users can watch and download content for free
3. **Admin Panel**: Add/delete/rename content, manage series seasons and episodes
4. **Force Join**: Users must join a specified Telegram channel to access the bot
5. **Auto-Deletion**: Content files auto-delete after a configurable timer (copyright protection)
6. **Deep Linking**: Direct access to specific content via shareable links with intermediate retrieval button and Burmese copyright notice

### Configuration
The bot uses the following configuration (in `config.py`):
- `BOT_TOKEN`: Telegram bot token from @BotFather (stored in environment variable)
- `ADMIN_IDS`: List of admin user IDs
- `FORCE_JOIN_CHANNEL`: Channel users must join (e.g., "@TGBOTS_CODE")

### Workflow
- **Bot**: Runs `python bot.py` as a console application (Telegram bot polling)

## Environment Variables
- `BOT_TOKEN`: Your Telegram bot token (get from @BotFather)

## Dependencies
- python-telegram-bot[ext] - Telegram bot framework
- Additional dependencies: httpx, aiolimiter, apscheduler, cachetools, tornado

## User Preferences
- No specific user preferences documented yet

## Notes
- The bot uses JSON files for data storage (not a traditional database)
- All content is freely accessible to users who join the required channel
- Content can have auto-delete timers to handle copyright issues
- The bot requires admin privileges in the force join channel to function properly
