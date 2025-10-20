# utils/constants.py

# --- Conversation States for Admin Panel ---
(
    SELECTING_ACTION, GET_NAME, GET_PHOTO, GET_YEAR,
    GET_CATEGORIES, 
    GET_TIMER, GET_CONTENT_VIDEOS, CONFIRM_DELETE, GET_SERIES_SEASON_COUNT,
    GET_SERIES_EPISODES, SELECT_RENAME_ITEM, GET_NEW_NAME,
    # --- NEW Edit Series States ---
    SELECT_EDIT_SERIES, SELECT_EDIT_SEASON, SELECT_EDIT_ACTION,
    ADD_SERIES_EPISODES, REMOVE_SERIES_EPISODES,
) = range(17)

# --- Callback Data Prefixes ---
CALLBACK_MOVIE_SELECT = "movie_select_"
CALLBACK_SERIES_SELECT = "series_select_"
CALLBACK_SEASON_SELECT = "season_select_"
CALLBACK_YEAR_PAGE = "year_page_"
CALLBACK_YEAR_SELECT = "year_select_"
CALLBACK_YEAR_CONTENT_TYPE = "year_content_"
CALLBACK_DELETE_MOVIE = "del_movie_"
CALLBACK_DELETE_SERIES = "del_series_"
CALLBACK_REGET_MOVIE = "reget_movie_"
CALLBACK_REGET_SERIES = "reget_series_"
CALLBACK_RENAME_MOVIE = "ren_movie_"
CALLBACK_RENAME_SERIES = "ren_series_"
CALLBACK_MOVIE_PAGE = "movie_page_"
CALLBACK_SERIES_PAGE = "series_page_"
CALLBACK_DEEPLINK_MOVIE = "deeplink_movie_"
CALLBACK_DEEPLINK_SERIES = "deeplink_series_"

# --- Category Callbacks ---
CALLBACK_CATEGORY_PAGE = "cat_page_"
CALLBACK_CATEGORY_SELECT = "cat_select_"
CALLBACK_CATEGORY_CONTENT_TYPE = "cat_content_"

# Admin Panel Actions
CALLBACK_ADMIN_ADD_MOVIE = "admin_add_movie"
CALLBACK_ADMIN_ADD_SERIES = "admin_add_series"
CALLBACK_ADMIN_DELETE_MOVIE = "admin_delete_movie"
CALLBACK_ADMIN_DELETE_SERIES = "admin_delete_series"
CALLBACK_ADMIN_RENAME_MOVIE = "admin_rename_movie"
CALLBACK_ADMIN_RENAME_SERIES = "admin_rename_series"
CALLBACK_ADMIN_EDIT_SERIES = "admin_edit_series"
CALLBACK_ADMIN_CANCEL = "admin_cancel"

# --- NEW Edit Series Callbacks ---
CALLBACK_EDIT_SERIES_PAGE = "edit_series_page_"
CALLBACK_EDIT_SERIES_SELECT = "edit_series_select_"
CALLBACK_EDIT_SEASON_SELECT = "edit_season_select_"
CALLBACK_EDIT_ACTION_ADD = "edit_action_add"
CALLBACK_EDIT_ACTION_REMOVE = "edit_action_remove"
CALLBACK_REMOVE_EPISODE = "remove_episode_"

# --- Message Templates & Stickers ---
# Find a valid File ID by sending a sticker to a bot like @JsonDumpBot
THANK_YOU_STICKER_ID = "CAACAgIAAxkBAAECHLlopW_Gd1s1_YHzl-PJ76xUOYa4NAACNDoAArR2CUgmpTx1tcQieDYE" # Replace if you have one, or set to None

DELETION_WARNING_TEXT = """
❗️❗️❗️ **အရေးကြီးပါတယ်** ❗️❗️❗️

ဤရုပ်ရှင်ဖိုင်များ/ဗီဒီယိုများကို   **{timer} မိနစ်** အတွင်း  (မူပိုင်ခွင့်ပြဿနာများကြောင့်) ဖျက်ပါမည်။

ကျေးဇူးပြု၍ ဤဖိုင်များ/ဗီဒီယိုများအားလုံးကို သင်၏ Save Messages သို့ Forward လုပ်ပြီး ထိုနေရာတွင် ဇာတ်ကားအားကြည့်ရှုပါ။

---

❗️❗️❗️ **IMPORTANT** ❗️️❗️❗️

These Movie Files/Videos will be deleted in **{timer} mins** (Due to Copyright Issues).

Please **forward** ALL Files/Videos to your **Saved Messages** and watch from there.
"""