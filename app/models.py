from django.db import models
from django.utils.timezone import now
import datetime

# Define choices for market modes
BEARISH_STRONG = 'BES'
BEARISH = 'BE'
IDLE = 'ID'
BULLISH = 'BU'
BULLISH_STRONG = 'BUS'
market_modes = [
    (BEARISH_STRONG, 'bearish_strong'),
    (BEARISH, 'bearish'),
    (IDLE, 'idle'),
    (BULLISH, 'bullish'),
    (BULLISH_STRONG, 'bullish_strong'),
]

# Define choices for event type
ADDITION = '1'
MULTIPLICATION = '2'
MODE = '3'
types = [
    (ADDITION, 'addition'),
    (MULTIPLICATION, 'multiplication'),
    (MODE, 'mode'),
]

# Define the other ressources that can be affected by the event, beside a category or an investment
CAPITAL = '1'
other = [
    (CAPITAL, 'capital'),
]

# Define choices for moral type

MORAL_HOUSING = '1'
MORAL_HEALTH = '2'
MORAL_FREETIME = '3'
moral_types = [
    (MORAL_HOUSING, 'housing'),
    (MORAL_HEALTH, 'health'),
    (MORAL_FREETIME, 'freetime')
]

# Define choices for moral event type
MORAL_CAPITAL_ADDITION = '1'
MORAL_MAX_VALUE_ADDITION = '2'
MORAL_MAX_VALUE_MULTIPLICATION = '3'
moral_operation_types = [
    (MORAL_CAPITAL_ADDITION, 'moral_capital_addition'),
    (MORAL_MAX_VALUE_ADDITION, 'moral_max_value_addition'),
    (MORAL_MAX_VALUE_MULTIPLICATION, 'moral_max_value_multiplication')
]


class Gamemode(models.Model):
    end_round = models.IntegerField(default=20)
    round_salary = models.IntegerField(default=5000)
    probability_event = models.FloatField(default=0.2)
    win_threshold = models.IntegerField(default=100000)
    inflation = models.FloatField(default=0.01)
    rounds_to_win = models.IntegerField(default=1)
    start_capital = models.IntegerField(default=20000)
    created_at = models.IntegerField(default=0)


class Lobby(models.Model):
    access_key = models.CharField(blank=True, null=True, max_length=20, unique=True)
    number_of_players = models.IntegerField(default=0)
    private = models.BooleanField(default=False)


class Game(models.Model):
    access_token = models.CharField(blank=True, null=True, max_length=20, unique=True)
    current_capital = models.IntegerField(blank=True, null=True)
    current_investment = models.IntegerField(blank=True, null=True)
    current_round = models.IntegerField(default=1)
    gamemode = models.ForeignKey(Gamemode, on_delete=models.CASCADE)
    health_punishment_counter = models.IntegerField(default=0)
    lobby = models.ForeignKey(Lobby, null=True, on_delete=models.CASCADE)
    player_name = models.CharField(blank=True, null=True, max_length=20)
    previous_capital = models.IntegerField(blank=True, null=True)
    previous_investment = models.IntegerField(blank=True, null=True)
    round_salary_multiplier = models.FloatField(default=1)
    winning_rounds = models.IntegerField(default=0)
    won = models.BooleanField(blank=True, null=True, default=None)
    won_description = models.CharField(blank=True, null=True, max_length=200)
    game_started_at = models.IntegerField(default=0)

class Morals(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="morals")
    housing_investment = models.IntegerField(default=0)
    housing_max = models.IntegerField(default=900)
    health_investment = models.IntegerField(default=0)
    health_max = models.IntegerField(default=300)
    freetime_investment = models.IntegerField(default=0)
    freetime_max = models.IntegerField(default=200)


class Category(models.Model):
    name = models.CharField(blank=True, null=True, max_length=20, unique=True)
    volatility = models.FloatField(default=0.1)


class Investment(models.Model):
    name = models.CharField(max_length=200, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='investments')
    asset_value = models.FloatField(default=0)
    market_probabilities = models.CharField(max_length=20, blank=False, default="0/40/20/40/0", unique=False)


class Round(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="rounds")
    start_capital = models.IntegerField(blank=True, null=True)
    end_capital = models.IntegerField(blank=True, null=True, default=None)
    start_investment = models.IntegerField(blank=True, null=True, default=0)
    end_investment = models.IntegerField(blank=True, null=True, default=None)
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True, default=None)
    round_number = models.IntegerField(default=-5)
    event = models.ForeignKey('Event', on_delete=models.CASCADE, null=True, default=None)
    moralEvent = models.ForeignKey('MoralEvent', on_delete=models.CASCADE, null=True, default=None)


class MoralEvent(models.Model):
    name = models.CharField(max_length=200, unique=True)
    text = models.CharField(max_length=200, blank=True, null=True, default=None)
    positive_event = models.BooleanField(default=False)
    moral_type = models.CharField(max_length=3, choices=moral_types, default=MORAL_HOUSING, blank=True, null=True)
    moral_operation_type = models.CharField(max_length=3, choices=moral_operation_types, default=MORAL_CAPITAL_ADDITION,
                                            blank=True, null=True)
    value = models.IntegerField(blank=True, null=True, default=0)
    moral_max_reset = models.BooleanField(default=False)
    target_moral = models.CharField(max_length=3, choices=moral_types, default=MORAL_HOUSING, blank=True, null=True)
    change_round_salary = models.BooleanField(default=False)


class RoundCategoryInvestment(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name="category_investments")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    category_overall_amount = models.IntegerField(blank=True, null=True, default=0)
    category_difference_amount = models.IntegerField(blank=True, null=True, default=0)
    category_difference_percent = models.FloatField(blank=True, null=True, default=0)


class RoundInvestment(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    overall_amount = models.IntegerField(blank=True, null=True, default=0)
    difference_amount = models.IntegerField(blank=True, null=True, default=0)
    difference_percent = models.FloatField(blank=True, null=True, default=0)
    category_investment = models.ForeignKey(RoundCategoryInvestment, related_name='investments',
                                            on_delete=models.CASCADE)
    asset_value = models.FloatField(default=0)
    market_mode = models.CharField(max_length=3, choices=market_modes, default=IDLE, blank=True, null=True)
    market_years = models.IntegerField(blank=False, default=0)
    market_probabilities = models.CharField(max_length=20, blank=False, default="0/30/10/60/0", unique=False)
    market_reset = models.BooleanField(default=False)


class Event(models.Model):
    name = models.CharField(max_length=200, unique=True)
    # Only one of the next three fields at a time should be used for one event 
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, null=True, blank=True)
    other = models.CharField(max_length=3, choices=other, default=CAPITAL, blank=True, null=True)
    # The type defines how the affected ressource should be manipulated
    type = models.CharField(max_length=3, choices=types, default=ADDITION)
    # If the type is MODE, the market mode of the ressource is set to the given $mode for $market_years rounds
    # This works only for the ressources category or investment
    mode = models.CharField(max_length=3, choices=market_modes, default=IDLE, blank=True, null=True)
    market_years = models.IntegerField(blank=False, default=0)
    market_probabilities = models.CharField(max_length=20, blank=False, default="0/30/10/60/0", unique=False)
    market_reset = models.BooleanField(default=False)
    # For the types where a ressource is changed by applying a mathematical funtion, the $value is used
    value = models.FloatField(blank=True, null=True, default=1)
    text = models.CharField(max_length=200, blank=True, null=True, default=None)
