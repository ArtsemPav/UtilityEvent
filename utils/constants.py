# ---------- Значения по умолчанию для событий ----------
DEFAULT_EVENT_ID = "MyEvent"
DEFAULT_ASSET_BUNDLE = "_events/MyEvent"
DEFAULT_BLOCKER_PREFAB = "Dialogs/MyEvent_Dialog"
DEFAULT_ROUNDEL_PREFAB = "Roundels/MyEvent_Roundel"
DEFAULT_EVENT_CARD_PREFAB = ""
DEFAULT_NODE_COMPLETION_PREFAB = "Dialogs/MyEvent_Dialog"
DEFAULT_CONTENT_KEY = "MyEvent"
DEFAULT_MIN_LEVEL = 1
DEFAULT_REPEATS = -1
DEFAULT_SEGMENT = "Default"

# ---------- Значения по умолчанию для сегментов ----------
DEFAULT_VIP_RANGE = "1-10+"

# Типы PossibleSegmentInfo и их метки для UI
SEGMENT_INFO_TYPES = {
    "VIPRange":          "VIP Range",
    "AverageWagerRange": "Average Wager Range",
    "SpinpadRange":      "Spinpad Range",
    "LevelRange":        "Level Range",
}
# Ключ для сегмента без PossibleSegmentInfo
SEGMENT_INFO_NONE = ""

# ---------- Значения по умолчанию для узлов ----------
DEFAULT_GAME_LIST = ["AllGames"]
DEFAULT_BUTTON_TEXT = "PLAY NOW!"
DEFAULT_MINIGAME = "FlatReward"
DEFAULT_CONTRIBUTION_LEVEL = "Node"

# ---------- Типы наград ----------
REWARD_TYPES = [
    "Chips",
    "VariableChips",
    "MLM",
    "Loyalty Point",
    "Vip Points",
    "Sweepstakes",
    "FreePlays",
    "Packs",
    "MagicPacks",
    "BoardGameDices",
    "BoardGameBuilds",
    "BoardGameRareBuilds",
]

# ---------- Типы целей ----------
GOAL_TYPES = [
    "Spins",
    "Coins",
    "Wins",
    "ConsecutiveWins",
    "TotalCoinsPerDay",
]

# ---------- Валюты для фиксированных наград ----------
CURRENCY_TYPES = [
    "Chips",
    "Tickets",
    "Loyalty",
    "VipPoints",
    "Entries_Name",
    "BoardGameDices",
    "BoardGameBuilds",
    "BoardGameRareBuilds",
]

# ---------- Имена файлов ----------
DEFAULT_OUTPUT_FILENAME = "LiveEventData.json"
DEFAULT_SCHEMA_FILENAME = "schema.json"

# ---------- Прочие константы ----------
MAX_NODE_ID = 999999
MIN_BET_MIN_VALUE = 0.0
MIN_BET_MAX_VALUE = 1_000_000_000.0