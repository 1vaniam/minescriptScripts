import random
import minescript
from minescript import EventType, player_name

import config
from logger import debug_log
from utils import safe_sleep, strip_minecraft_formatting, normalize_quotes
from handlers import (
    handle_ignore,
    handle_math,
    handle_unscramble,
    handle_unreverse,
    handle_fill_gaps,
    handle_trivia,
    handle_underscore_word,
    handle_quoted_word,
    handle_keyword,
    handle_type_letters,
)


minescript.echo("Hello ☻", player_name(), "!!")

from words import WORDS
if not WORDS:
    minescript.echo("[ChatGames] WARNING: words.txt not loaded")
    debug_log("words.txt missing or empty")



def process_message(msg: str):
    debug_log(f"[Process] Received: '{msg}'")

    # 1. Ignore patterns
    if handle_ignore(msg):
        debug_log("[Process] Ignored")
        return

    # list of handlers
    handlers = [
        handle_math,
        handle_unscramble,
        handle_unreverse,
        handle_fill_gaps,
        handle_trivia,
        handle_underscore_word,
        handle_quoted_word,
        handle_keyword,
        handle_type_letters,
    ]

    for handler in handlers:
        result = handler(msg)

        if result is None:
            continue

        # debug
        if result == "":
            debug_log(f"[Process] {handler.__name__} triggered (no output)")
            return

        # valid answer
        debug_log(f"[Process] {handler.__name__} result: {result}")

        delay = config.BASE_DELAY + len(result) * config.PER_LETTER_DELAY
        safe_sleep(delay)
        minescript.chat(result)
        return

    debug_log("[Process] No handler matched")


# event loop
with minescript.EventQueue() as event_queue:
    event_queue.register_chat_listener()

    while True:
        event = event_queue.get()

        if event.type != EventType.CHAT:
            continue

        raw = event.message or ""

        msg = strip_minecraft_formatting(
            normalize_quotes(raw)
        )

        # human like delay
        safe_sleep(random.uniform(0.4, 0.5))

        process_message(msg)
