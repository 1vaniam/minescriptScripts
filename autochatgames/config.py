# constants, delays
BASE_DELAY = 0.6
PER_LETTER_DELAY = 0.08
STATE_TIMEOUT = 3.0

# runtime states
STATE = {
    "mode": None,
    "armed_at": 0,
    "data": None
}

WAITING_MATH = False
MATH_TIME = 0

WAITING_UNSCRAMBLE = False
UNSCRAMBLE_TIME = 0

WAITING_UNREVERSE = False
UNREVERSE_TIME = 0

WAITING_FILL_GAPS = False
FILL_GAPS_TIME = 0
