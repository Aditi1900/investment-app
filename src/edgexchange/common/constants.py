PRICE_REFRESH_INTERVAL = 3

# INPUT:
#   -user_count(int); number of users currently accessing the system
# OUTPUT: None
# PRECONDITION: None
# POSTCONDITION:
#   -PRICE_REFRESH_INTERVAL; system refresh time is dynamically set
# RAISES: None
def dynamic_system_refresh(user_count : int) -> None:
    global PRICE_REFRESH_INTERVAL

    if user_count < 50:
        PRICE_REFRESH_INTERVAL = 3
    elif user_count < 200:
        PRICE_REFRESH_INTERVAL = 4
    elif user_count < 500:
        PRICE_REFRESH_INTERVAL = 5
    else:
        PRICE_REFRESH_INTERVAL = 6


