# keyboards/inline.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import db_handler
from utils import constants as const
from typing import List, Dict, Any

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("➕ Add Movie", callback_data=const.CALLBACK_ADMIN_ADD_MOVIE),
            InlineKeyboardButton("➕ Add Series", callback_data=const.CALLBACK_ADMIN_ADD_SERIES),
        ],
        [
            InlineKeyboardButton("❌ Delete Movie", callback_data=const.CALLBACK_ADMIN_DELETE_MOVIE),
            InlineKeyboardButton("❌ Delete Series", callback_data=const.CALLBACK_ADMIN_DELETE_SERIES),
        ],
        [
            InlineKeyboardButton("✏️ Rename Movie", callback_data=const.CALLBACK_ADMIN_RENAME_MOVIE),
            InlineKeyboardButton("✏️ Rename Series", callback_data=const.CALLBACK_ADMIN_RENAME_SERIES),
        ],
        [
            InlineKeyboardButton("📝 Edit Series", callback_data=const.CALLBACK_ADMIN_EDIT_SERIES)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def category_selection_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Generates a paginated keyboard for browsing content by category."""
    categories = db_handler.get_all_unique_categories()
    if not categories:
        keyboard = [
            [InlineKeyboardButton("No categories available yet.", callback_data="no_op")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    per_page = 10
    start, end = page * per_page, (page + 1) * per_page
    paginated_categories = categories[start:end]

    keyboard = []
    # Create 2 columns
    for i in range(0, len(paginated_categories), 2):
        row = [
            InlineKeyboardButton(cat, callback_data=f"{const.CALLBACK_CATEGORY_SELECT}{cat}")
            for cat in paginated_categories[i:i+2]
        ]
        keyboard.append(row)
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{const.CALLBACK_CATEGORY_PAGE}{page-1}"))
    if end < len(categories):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{const.CALLBACK_CATEGORY_PAGE}{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu")])
    return InlineKeyboardMarkup(keyboard)

def category_content_type_keyboard(category: str) -> InlineKeyboardMarkup:
    """Asks the user to choose between Movies or Series for a specific category."""
    keyboard = [
        [
            InlineKeyboardButton("🎬 Movies", callback_data=f"{const.CALLBACK_CATEGORY_CONTENT_TYPE}{category}_movies"),
            InlineKeyboardButton("📺 Series", callback_data=f"{const.CALLBACK_CATEGORY_CONTENT_TYPE}{category}_series"),
        ],
        [InlineKeyboardButton("🔙 Back to Category Selection", callback_data="browse_category_from_callback")]
    ]
    return InlineKeyboardMarkup(keyboard)

def year_selection_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    years = db_handler.get_all_unique_years()
    if not years:
        keyboard = [
            [InlineKeyboardButton("No content available yet.", callback_data="no_op")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    per_page = 10
    start, end = page * per_page, (page + 1) * per_page
    paginated_years = years[start:end]
    keyboard = []
    for i in range(0, len(paginated_years), 2):
        row = [
            InlineKeyboardButton(str(year), callback_data=f"{const.CALLBACK_YEAR_SELECT}{year}")
            for year in paginated_years[i:i+2]
        ]
        keyboard.append(row)
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{const.CALLBACK_YEAR_PAGE}{page-1}"))
    if end < len(years):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{const.CALLBACK_YEAR_PAGE}{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu")])
    return InlineKeyboardMarkup(keyboard)

def year_content_type_keyboard(year: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("🎬 Movies", callback_data=f"{const.CALLBACK_YEAR_CONTENT_TYPE}{year}_movies"),
            InlineKeyboardButton("📺 Series", callback_data=f"{const.CALLBACK_YEAR_CONTENT_TYPE}{year}_series"),
        ],
        [InlineKeyboardButton("🔙 Back to Year Selection", callback_data="browse_year_from_callback")]
    ]
    return InlineKeyboardMarkup(keyboard)

def movie_list_keyboard(movies: List[Dict[str, Any]], page: int = 0) -> InlineKeyboardMarkup:
    per_page = 10
    start, end = page * per_page, (page + 1) * per_page
    paginated_movies = movies[start:end]
    keyboard = [
        [InlineKeyboardButton(f"🎬 {movie['name']} ({movie['year']})", callback_data=f"{const.CALLBACK_MOVIE_SELECT}{movie['id']}")]
        for movie in paginated_movies
    ]
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{const.CALLBACK_MOVIE_PAGE}{page-1}"))
    if end < len(movies):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{const.CALLBACK_MOVIE_PAGE}{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu")])
    return InlineKeyboardMarkup(keyboard)

def series_list_keyboard(series_list: List[Dict[str, Any]], page: int = 0) -> InlineKeyboardMarkup:
    per_page = 10
    start, end = page * per_page, (page + 1) * per_page
    paginated_series = series_list[start:end]
    keyboard = [
        [InlineKeyboardButton(f"📺 {series['name']} ({series['year']})", callback_data=f"{const.CALLBACK_SERIES_SELECT}{series['id']}")]
        for series in paginated_series
    ]
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{const.CALLBACK_SERIES_PAGE}{page-1}"))
    if end < len(series_list):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{const.CALLBACK_SERIES_PAGE}{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu")])
    return InlineKeyboardMarkup(keyboard)
    
def series_season_keyboard(series: Dict[str, Any]) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(f"Season {season_num}", callback_data=f"{const.CALLBACK_SEASON_SELECT}{series['id']}_{season_num}")]
        for season_num in sorted(series['seasons'].keys(), key=int)
    ]
    return InlineKeyboardMarkup(keyboard)

def get_file_again_keyboard(content_type: str, content_id: str) -> InlineKeyboardMarkup:
    callback_data = f"{const.CALLBACK_REGET_MOVIE}{content_id}" if content_type == 'movie' else f"{const.CALLBACK_REGET_SERIES}{content_id}"
    keyboard = [[InlineKeyboardButton("🔁 GET FILE AGAIN!", callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)

def cancel_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data=const.CALLBACK_ADMIN_CANCEL)]]
    return InlineKeyboardMarkup(keyboard)

def edit_series_list_keyboard(series_list: List[Dict[str, Any]], page: int = 0) -> InlineKeyboardMarkup:
    """Paginated keyboard for selecting a series to edit."""
    per_page = 10
    start, end = page * per_page, (page + 1) * per_page
    paginated_series = series_list[start:end]
    keyboard = [
        [InlineKeyboardButton(f"📝 {series['name']} ({series['year']})", callback_data=f"{const.CALLBACK_EDIT_SERIES_SELECT}{series['id']}")]
        for series in paginated_series
    ]
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{const.CALLBACK_EDIT_SERIES_PAGE}{page-1}"))
    if end < len(series_list):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"{const.CALLBACK_EDIT_SERIES_PAGE}{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("🔙 Back to Admin Panel", callback_data=const.CALLBACK_ADMIN_CANCEL)])
    return InlineKeyboardMarkup(keyboard)

def edit_season_selection_keyboard(series: Dict[str, Any]) -> InlineKeyboardMarkup:
    """Keyboard for selecting a season to edit."""
    keyboard = [
        [InlineKeyboardButton(f"Season {season_num} ({len(episodes)} episodes)", callback_data=f"{const.CALLBACK_EDIT_SEASON_SELECT}{series['id']}_{season_num}")]
        for season_num, episodes in sorted(series['seasons'].items(), key=lambda x: int(x[0]))
    ]
    keyboard.append([InlineKeyboardButton("🔙 Back to Series List", callback_data=const.CALLBACK_ADMIN_EDIT_SERIES)])
    return InlineKeyboardMarkup(keyboard)

def edit_action_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for choosing to add or remove episodes."""
    keyboard = [
        [InlineKeyboardButton("➕ Add Episodes", callback_data=const.CALLBACK_EDIT_ACTION_ADD)],
        [InlineKeyboardButton("❌ Remove Episodes", callback_data=const.CALLBACK_EDIT_ACTION_REMOVE)],
        [InlineKeyboardButton("🔙 Back", callback_data=const.CALLBACK_ADMIN_EDIT_SERIES)]
    ]
    return InlineKeyboardMarkup(keyboard)

def remove_episode_keyboard(series_id: str, season_num: str, episodes: List[str]) -> InlineKeyboardMarkup:
    """Keyboard for selecting episodes to remove."""
    keyboard = [
        [InlineKeyboardButton(f"❌ Episode {i+1}", callback_data=f"{const.CALLBACK_REMOVE_EPISODE}{series_id}_{season_num}_{i}")]
        for i in range(len(episodes))
    ]
    keyboard.append([InlineKeyboardButton("✅ Done", callback_data=const.CALLBACK_ADMIN_EDIT_SERIES)])
    return InlineKeyboardMarkup(keyboard)