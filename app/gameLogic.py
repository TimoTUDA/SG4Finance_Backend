from app.models import *
import random
import string
from django.utils import timezone
from app.AppEnums import *
from scipy import stats
import numpy as np
from app.utils import *
import datetime

end_round = 10
round_salary = 5000
probability_event = 0.2
win_threshold = 100000
inflation = 0.01
rounds_to_win = 5


#This function deletes all games that are older than 7 days
def delete_old_games():
    one_week_ago = int((datetime.datetime.now() - datetime.timedelta(days=7)).timestamp())
    
    games_to_delete = Game.objects.filter(id__gt=12, game_started_at__lt=one_week_ago)
   
    for game in games_to_delete:
        #print("deleted", game.pk)
        game.delete()

#This function deletes all sandbox modes that are older than 30 minutes
def delete_old_gamemodes():
    thirty_minutes_ago = int((datetime.datetime.now() - datetime.timedelta(days=1)).timestamp())
    gamemodes_to_delete = Gamemode.objects.filter(id__gt=10, created_at__lt=thirty_minutes_ago)
    for gamemode in gamemodes_to_delete:
        #print("deleted", gamemode.pk)
        gamemode.delete()

#This function creates a sandbox mode from the settings
def create_sandbox(gamemode_id,end_round, round_salary, probability_event, win_threshold, inflation, rounds_to_win, start_capital):
    #we dont want to have a lot of old gamemodes in the DB that is why we delete the old Sandbox mode after 1 day
    delete_old_gamemodes()
    #print(gamemode_id)
    try:
        gamemode = Gamemode.objects.get(pk=gamemode_id)
        # This way we create Sandbox modes from 10 ongoing with an autoIncrement
        gamemode = Gamemode.objects.create()
        #print("Gamemode created or retrieved")
    except Gamemode.DoesNotExist:
        gamemode = Gamemode.objects.create(pk=gamemode_id)
        #print("Gamemode created")
    
    #Alter the table-Data
    gamemode.end_round = end_round
    gamemode.round_salary = round_salary
    gamemode.probability_event = probability_event
    gamemode.win_threshold = win_threshold
    gamemode.inflation = inflation
    gamemode.rounds_to_win = rounds_to_win
    gamemode.start_capital = start_capital
    gamemode.created_at = int(datetime.datetime.now().timestamp())
    #save it to the DB
    gamemode.save()
    #print("game was saved")

def create_game(player_name, gamemode_id, multiplayer, multiplayer_key):
    
    #Delete all games that are older than 1 week
    delete_old_games()

    #use the last created sandbox mode to play the game
    if(gamemode_id == 10):
        gamemode = Gamemode.objects.last()
        #print("gamemode", gamemode)
    else:
        gamemode = Gamemode.objects.get(pk=gamemode_id)
    
    lobby = Lobby.objects.filter(access_key=multiplayer_key).first()

    if multiplayer == True:
        if lobby is None:
            lobby = Lobby.objects.create(access_key=''.join(
                random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(5)), 
                number_of_players=1)
        else:
            lobby.number_of_players += 1
        lobby.save()

    game = Game.objects.create(access_token=''.join(
        random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(20)),
        current_capital=gamemode.start_capital,
        previous_capital=gamemode.start_capital,
        current_investment=0,
        previous_investment=0,
        gamemode=gamemode,
        player_name=player_name,
        lobby=lobby)
    
    #This is necessary for the check for deleting old games
    game.game_started_at = int(datetime.datetime.now().timestamp())
    game.save()

    if game is not None:

        round_obj = Round.objects.create(game=game, start_capital=gamemode.start_capital)
        morals_obj = Morals.objects.create(game=game)

        categories = Category.objects.all()
        for category in categories:
            tmp = RoundCategoryInvestment.objects.create(round=round_obj, category=category)
            investments = Investment.objects.filter(category=category)
            for investment in investments:
                RoundInvestment.objects.create(round=round_obj, investment=investment, category_investment=tmp,
                                               asset_value=investment.asset_value)

        current_round = round_obj
        # History generation
        # synchronize values for multiplayer?
        if lobby is not None and lobby.number_of_players > 1:
            games_in_lobby = Game.objects.filter(lobby=game.lobby)
            for j in range(lobby.number_of_players):
                if games_in_lobby[j] != game:
                    for i in range(6):
                        new_round = Round.objects.create(game=game, start_capital=current_round.start_capital,
                                                         round_number=current_round.round_number + 1,
                                                         event=None)
                        for category in categories:
                            tmp = RoundCategoryInvestment.objects.create(round=new_round, category=category)
                            investments = Investment.objects.filter(category=category)
                            for investment in investments:
                                round_investment = RoundInvestment.objects.create(round=new_round, investment=investment,
                                                                                  category_investment=tmp)
                                other_round_investment = RoundInvestment.objects.get(round=Round.objects.filter(game=games_in_lobby[j],round_number=current_round.round_number+1).first(), investment=investment)
                                round_investment.difference_percent = other_round_investment.difference_percent
                                round_investment.asset_value = other_round_investment.asset_value
                                if round_investment.overall_amount <= 0:
                                    round_investment.overall_amount = 0
                                round_investment.market_mode = other_round_investment.market_mode
                                round_investment.market_years = other_round_investment.market_years
                                round_investment.market_probabilities = other_round_investment.market_probabilities
                                round_investment.market_reset = other_round_investment.market_reset
                                round_investment.save()

                        new_round.start_investment = 0
                        new_round.save()
                        current_round = new_round
                    return current_round

        for i in range(6):
            new_round = Round.objects.create(game=game, start_capital=current_round.start_capital,
                                             round_number=current_round.round_number + 1,
                                             event=None)
            for category in categories:
                ###category_difference = 0
                tmp = RoundCategoryInvestment.objects.create(round=new_round, category=category)
                investments = Investment.objects.filter(category=category)
                for investment in investments:
                    round_investment = RoundInvestment.objects.create(round=new_round, investment=investment,
                                                                      category_investment=tmp)
                    old_round_investment = RoundInvestment.objects.filter(round=current_round,
                                                                          investment=investment).first()

                    (market_mode, market_probabilities, market_years, market_reset) = calculate_market(
                        old_round_investment)
                    # print(market_mode, market_probabilities, market_years)
                    percentage = getPercentage(game, category, investment, market_mode)

                    round_investment.difference_percent = percentage
                    round_investment.asset_value = round(old_round_investment.asset_value * (1 + percentage), 2)
                    difference = old_round_investment.overall_amount * percentage
                    ###round_investment.overall_amount = old_round_investment.overall_amount + difference
                    # check if after a potential event the overall amount is negative
                    if round_investment.overall_amount <= 0:
                        round_investment.overall_amount = 0
                    ###round_investment.difference_amount = difference
                    round_investment.market_mode = market_mode
                    round_investment.market_years = market_years
                    round_investment.market_probabilities = market_probabilities
                    round_investment.market_reset = market_reset
                    round_investment.save()

            new_round.start_investment = 0
            new_round.save()
            current_round = new_round
        return current_round
    else:
        raise Exception('Could not create a game.')


def calculate_morals_event(morals):
    # the function which calculates the probability if an event gets triggered
    event_probability_function = lambda x: x ** 2

    event_list = []
    # moral percentage for negative [-1..0] for positive [0..1]
    # the sign indicates if a negative or positive event should be chosen
    moral_perc_house = moral_percentage(morals.housing_investment, morals.housing_max)
    moral_perc_health = moral_percentage(morals.health_investment, morals.health_max)
    moral_perc_freetime = moral_percentage(morals.freetime_investment, morals.freetime_max)

    # region calc housing event
    if moral_perc_house > 0:
        probability = event_probability_function(moral_perc_house)
        if random.random() < probability:
            ids = MoralEvent.objects.filter(moral_type=1, positive_event=True).values_list('pk', flat=True)
            random_id = random.choice(ids)
            event_list.append(MoralEvent.objects.get(pk=random_id))
    else:
        probability = event_probability_function(moral_perc_house * -1)
        if random.random() < probability:
            ids = MoralEvent.objects.filter(moral_type=1, positive_event=False).values_list('pk', flat=True)
            random_id = random.choice(ids)
            event_list.append(MoralEvent.objects.get(pk=random_id))  #
    # endregion
    # region calc health event
    if moral_perc_health > 0:
        probability = event_probability_function(moral_perc_health)
        if random.random() < probability:
            ids = MoralEvent.objects.filter(moral_type=2, positive_event=True).values_list('pk', flat=True)
            random_id = random.choice(ids)
            event_list.append(MoralEvent.objects.get(pk=random_id))
    else:
        probability = event_probability_function(moral_perc_health * -1)
        if random.random() < probability:
            ids = MoralEvent.objects.filter(moral_type=2, positive_event=False).values_list('pk', flat=True)
            random_id = random.choice(ids)
            event_list.append(MoralEvent.objects.get(pk=random_id))
    # endregion
    # region calc freetime event
    if moral_perc_freetime > 0:
        probability = event_probability_function(moral_perc_freetime)
        if random.random() < probability:
            ids = MoralEvent.objects.filter(moral_type=3, positive_event=True).values_list('pk', flat=True)
            random_id = random.choice(ids)
            event_list.append(MoralEvent.objects.get(pk=random_id))
    else:
        probability = event_probability_function(moral_perc_freetime * -1)
        if random.random() < probability:
            ids = MoralEvent.objects.filter(moral_type=3, positive_event=False).values_list('pk', flat=True)
            random_id = random.choice(ids)
            event_list.append(MoralEvent.objects.get(pk=random_id))
    # endregion
    if len(event_list) > 1:
        return random.choice(event_list)
    if len(event_list) == 0:
        return None
    else:
        return event_list[0]


def reset_morals_max_value(morals, moral_event):
    if moral_event.moral_type == '1':
        morals.housing_max /= moral_event.value
    if moral_event.moral_type == '2':
        morals.health_max /= moral_event.value
    if moral_event.moral_type == '3':
        morals.freetime_max /= moral_event.value


def updateGame(request_json, game, round_obj):
    
    #gamemodes
    end_round = game.gamemode.end_round
    round_salary = game.gamemode.round_salary
    probability_event = game.gamemode.probability_event
    win_threshold = game.gamemode.win_threshold
    inflation = game.gamemode.inflation
    rounds_to_win = game.gamemode.rounds_to_win
    
    # game information
    round_number = game.current_round
    current_capital = game.current_capital
    current_investment = game.current_investment
    round_salary_multiplier = game.round_salary_multiplier

    games_in_lobby = Game.objects.filter(lobby=game.lobby)

    if round_number > end_round:
        return False

    # if user already won or loose, the game is already over 
    if game.won is not None:
        return False

    # update current round information
    current_round = Round.objects.filter(game=game, round_number=round_number).first()

    response_investment_list = {investment["investment"]["name"]: investment["overall_amount"] for item in
                                request_json["category_investments"] for investment in item['investments']}
    differenceInvestment = sum(response_investment_list.values()) - current_round.start_investment
    current_round.end_investment = current_round.start_investment + differenceInvestment
    sumMoral = request_json['game']['morals'][0]['housing_investment'] + request_json['game']['morals'][0]['health_investment'] + request_json['game']['morals'][0]['freetime_investment']
    current_round.end_capital = current_round.start_capital - differenceInvestment + round_salary * round_salary_multiplier - sumMoral
    current_round.end_time = timezone.now()

    # region insert the given investments made for current round into the database
    categories = Category.objects.all()
    for category in categories:
        tmp = RoundCategoryInvestment.objects.filter(round=current_round, category=category).first()
        response_category_list = {investment["investment"]["name"]: investment["overall_amount"] for item in
                                  request_json["category_investments"] if item["category"]["name"] == category.name for
                                  investment in item["investments"]}
        category_sum = sum(response_category_list.values())
        tmp.category_overall_amount = category_sum
        tmp.save()

        investments = Investment.objects.filter(category=category)
        for investment in investments:
            round_investment = RoundInvestment.objects.filter(category_investment=tmp, investment=investment).first()
            round_investment.overall_amount = response_category_list[investment.name]
            round_investment.save()
    # endregion
    # check if the next round should have an event
    event = None
    # synchronize values for multiplayer?
    if game.lobby is not None:
        for i in range(game.lobby.number_of_players):
            if games_in_lobby[i].current_round > game.current_round:
                event = Round.objects.filter(game=games_in_lobby[i], round_number=round_number+1).first().event
                break

    if event is None and random.random() < probability_event:
        # Choose a random event 
        ids = Event.objects.values_list('pk', flat=True)
        random_id = random.choice(ids)
        event = Event.objects.get(pk=random_id)


    # create the new round and update the investments made in last round according to stock in/decrease
    # event will be calculated in the current next round and the information of the event that happend will be included in the new round
    new_round = Round.objects.create(game=game, start_capital=current_round.end_capital, round_number=round_number + 1,
                                     event=event)
    

    morals = Morals.objects.filter(game=game).first()
    # update the given investments in moral values
    morals_dict = request_json["game"]["morals"][0]
    morals.housing_investment = morals_dict["housing_investment"]
    morals.health_investment = morals_dict["health_investment"]
    morals.freetime_investment = morals_dict["freetime_investment"]
    # calculate a potential moral_event
    moral_event = calculate_morals_event(morals)
    # print(moral_event.name)
    new_round.moralEvent = moral_event
    overall_difference = 0

    
    # check if in the last round a moral_event was active which effected a max_value
    if current_round.moralEvent is not None and current_round.moralEvent.moral_max_reset == True:
        reset_morals_max_value(morals, current_round.moralEvent)

    
    morals.housing_max = morals.housing_max * (1 + inflation)
    morals.health_max = morals.health_max * (1 + inflation)
    morals.freetime_max = morals.freetime_max * (1 + inflation)
    categories = Category.objects.all()

    

    # region Moral event evaluation
    if moral_event is not None and moral_event.moral_type == '2' and not moral_event.positive_event:
        moral_event.value += moral_event.value * game.health_punishment_counter/2
        game.health_punishment_counter += 1

    if moral_event is not None and moral_event.moral_operation_type == '1' and moral_event.moral_type == '2':
        moral_event.text = moral_event.text.rstrip(".0123456789\u20ac") + str(abs(moral_event.value)) + "\u20ac."

    if moral_event is not None and moral_event.moral_operation_type == '2':
        if moral_event.target_moral == '1':
            morals.housing_max += moral_event.value
        if moral_event.target_moral == '2':
            morals.health_max += moral_event.value
        if moral_event.target_moral == '3':
            morals.freetime_max += moral_event.value

    if moral_event is not None and moral_event.moral_operation_type == '3':
        if moral_event.target_moral == '1':
            morals.housing_max *= moral_event.value
        if moral_event.target_moral == '2':
            morals.health_max *= moral_event.value
        if moral_event.target_moral == '3':
            morals.freetime_max *= moral_event.value
    # endregion

    for category in categories:
        category_difference = 0
        tmp = RoundCategoryInvestment.objects.create(round=new_round, category=category)
        investments = Investment.objects.filter(category=category)
        for investment in investments:
            round_investment = RoundInvestment.objects.create(round=new_round, investment=investment,
                                                              category_investment=tmp)
            old_round_investment = RoundInvestment.objects.filter(round=current_round, investment=investment).first()

            # region The event triggers a market mode change
            if event is not None and event.type == '3':
                if event.category == category or event.investment == investment:
                    market_mode = event.mode
                    market_probabilities = event.market_probabilities
                    market_years = event.market_years
                    market_reset = event.market_reset
                else:
                    (market_mode, market_probabilities, market_years, market_reset) = calculate_market(
                        old_round_investment)
            else:
                (market_mode, market_probabilities, market_years, market_reset) = calculate_market(old_round_investment)
            # endregion
            # print(market_mode, market_probabilities, market_years)
            percentage = getPercentage(game, category, investment, market_mode)

            # region The event triggers a multiplication of the asset value
            if event is not None and event.type == '2':
                if event.category == category or event.investment == investment:
                    percentage += event.value
            # endregion
            # region The event triggers an Addition on the overall amount
            if event is not None and event.type == '1':
                if event.category == category or event.investment == investment:
                    if old_round_investment.overall_amount != 0:
                        difference = old_round_investment.overall_amount * percentage
                        difference += event.value
                    else:
                        difference = event.value
                else:
                    difference = old_round_investment.overall_amount * percentage

            else:
                difference = old_round_investment.overall_amount * percentage

            # endregion

            round_investment.difference_percent = percentage
            round_investment.asset_value = round(old_round_investment.asset_value * (1 + percentage), 2)
            
            # synchronize values for multiplayer?
            if game.lobby is not None:
                for i in range(game.lobby.number_of_players):
                    if games_in_lobby[i].current_round > game.current_round:
                        other_round_investment = RoundInvestment.objects.get(round=Round.objects.filter(game=games_in_lobby[i], round_number=round_number+1).first(), investment=round_investment.investment)
                        
                        round_investment.difference_percent = other_round_investment.difference_percent
                        round_investment.asset_value = other_round_investment.asset_value
                        difference = old_round_investment.overall_amount * round_investment.difference_percent
                        break

            round_investment.overall_amount = old_round_investment.overall_amount + difference
            # check if after a potential event the overall amount is negative
            if round_investment.overall_amount <= 0:
                round_investment.overall_amount = 0
            round_investment.difference_amount = difference
            round_investment.market_mode = market_mode
            round_investment.market_years = market_years
            round_investment.market_probabilities = market_probabilities
            round_investment.market_reset = market_reset
            round_investment.save()
            category_difference += round_investment.overall_amount - old_round_investment.overall_amount

        old_round_category = RoundCategoryInvestment.objects.filter(round=current_round, category=category).first()
        tmp.category_overall_amount = old_round_category.category_overall_amount + category_difference
        if old_round_category.category_overall_amount == 0:
            tmp.category_difference_percent = (category_difference / 1) * 100
        else:
            tmp.category_difference_percent = round((
                    (tmp.category_overall_amount / old_round_category.category_overall_amount) - 1), 4)
        tmp.category_difference_amount = category_difference
        tmp.save()
        overall_difference += category_difference
    new_round.start_investment = current_round.end_investment + overall_difference

    # update game information
    game.current_capital = new_round.start_capital
    game.current_investment = new_round.start_investment
    game.current_round = game.current_round + 1
    # update morals according to request

    # Event handling on other ressources (for example 1 is capital)
    if event is not None and event.type == '1':
        if event.other == '1':
            game.current_capital += event.value
            current_round.end_capital += event.value
            new_round.start_capital += event.value
            new_round.end_capital = new_round.start_capital

    if moral_event is not None and moral_event.moral_operation_type == '1':
        game.current_capital += moral_event.value
        if moral_event.change_round_salary:
            if moral_event.positive_event:
                game.round_salary_multiplier *= 1.25
            else:
                game.round_salary_multiplier /= 1.25
        current_round.end_capital += moral_event.value
        new_round.start_capital += moral_event.value
        new_round.end_capital = new_round.start_capital

    # user approaches win if capital + investment is at least the threshold
    if game.current_capital + game.current_investment >= win_threshold and game.winning_rounds < rounds_to_win:
        game.winning_rounds = game.winning_rounds + 1
    # user looses potential win
    elif game.current_capital + game.current_investment < win_threshold:
        game.winning_rounds = 0 
        
    # check if the user won or lost and set the right variable
    # user looses if he doesnt won at the end of the game
    if round_number >= end_round and game.winning_rounds == 0:
        game.won = False
        game.won_description = "user didn't reached the target net value of " + str(win_threshold)
    # user wins if capital + investment is at least the threshold for a few consectuive rounds
    elif game.winning_rounds >= rounds_to_win:
        game.won = True
        game.won_description = "Player reached target net value of " + str(win_threshold)
    # user looses if capital is less than 0
    elif game.current_capital < 0:
        game.won = False
        game.won_description = "Player reached a negative capital"
    
    game.previous_capital=current_capital
    game.previous_investment=current_investment
    game.save()
    current_round.save()
    new_round.save()
    morals.save()

    return new_round


def calculate_market(old_round_investment) -> (str, str, int, bool):
    MARKET_YEAR_MIN = 1
    MARKET_YEAR_MAX = 3

    if old_round_investment.market_years - 1 <= 0:
        market_years = random.randint(MARKET_YEAR_MIN, MARKET_YEAR_MAX)
        market_choices = ['BES', 'BE', 'ID', 'BU', 'BUS']
        prob_list = parse_market_probability_string(old_round_investment.market_probabilities)
        try:
            market_mode = np.random.choice(market_choices, p=prob_list)
        except:
            market_mode = 'BU'
            investment = Investment.objects.filter(roundinvestment=old_round_investment.id).first()
            prob_list = parse_market_probability_string(investment.market_probabilities)
        if old_round_investment.market_reset == True:
            market_reset = False
            investment = Investment.objects.filter(roundinvestment=old_round_investment.id).first()
            prob_list = parse_market_probability_string(investment.market_probabilities)
        else:
            market_reset = False
            prob_list = rearrange_market_probabilities(prob_list, market_mode)
        market_probabilities = convert_market_probability_string(prob_list)

    else:
        market_years = old_round_investment.market_years - 1
        market_mode = old_round_investment.market_mode
        market_probabilities = old_round_investment.market_probabilities
        market_reset = old_round_investment.market_reset

    return market_mode, market_probabilities, market_years, market_reset


def getPercentage(game, category, investment, market_mode):
    current_round = Round.objects.filter(game=game, round_number=game.current_round).first()
    round_investment = RoundInvestment.objects.filter(round=current_round, investment=investment).first()

    percentage = 0
    if market_mode == MarketMode.BEARISH_STRONG.value:
        # print('BEARISH_STRONG')
        percentage = np.random.uniform(low=(category.volatility * -1), high=((category.volatility * -1) / 4))
    elif market_mode == MarketMode.BEARISH.value:
        # print('BEARISH')
        percentage = np.random.uniform(low=((category.volatility * -1) * 0.75), high=(category.volatility / 4))
    elif market_mode == MarketMode.IDLE.value:
        """
        mean = mean value of distribution
        sd = standard deviation of distribution
        low = lower bound
        upp = upperbound
        """
        # print('IDLE')
        random_function = get_truncated_normal(mean=0, sd=((category.volatility / 4) / 4),
                                               low=((category.volatility * -1) / 4), upp=(category.volatility / 4))
        random_percentage = random_function.rvs()
        if random_percentage > 0:
            percentage = (category.volatility / 4) - random_percentage
        else:
            percentage = ((category.volatility * -1) / 4) + (random_percentage * -1)
    elif market_mode == MarketMode.BULLISH.value:
        # print('BULLISH')
        percentage = np.random.uniform(low=((category.volatility * -1) / 4), high=category.volatility * 0.75)
    elif market_mode == MarketMode.BULLISH_STRONG.value:
        # print('BULLISH_STRONG')
        percentage = np.random.uniform(low=(category.volatility * 0.25), high=category.volatility)
    return round(percentage, 3)


def get_truncated_normal(mean=0, sd=0.025, low=-0.1, upp=0.1):
    return stats.truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


# region Validate functions
def validate_round_request(round_information, game, round) -> (int, dict):
    (error_code, error_message) = validate_json(round_information, game, round)
    if error_code != 0:
        return error_code, error_message
    (error_code, error_message) = validate_semantics(round_information, game, round)
    if error_code != 0:
        return error_code, error_message
    return 0, {}


def validate_semantics(round_information, game, round) -> (int, dict):
    
    current_capital = game.current_capital
    moral_obj = Morals.objects.filter(game=game).first()
    investment_difference = 0
    response_category_list = {investment["investment"]["name"]: investment["overall_amount"] for item in
                              round_information["category_investments"] for investment in item['investments']}
    categories = Category.objects.all()
    for category in categories:
        for investment in Investment.objects.filter(category=category):
            last_round_investment = RoundInvestment.objects.filter(round=round,
                                                                   investment=Investment.objects.filter(
                                                                       name=investment.name).first()).first()
            # Check if the invested amount is smaller then 0
            if response_category_list[investment.name] < 0:
                return 1, {"error": "Investment cannot be < 0."}
            if last_round_investment is None:
                continue
            investment_difference += last_round_investment.overall_amount - response_category_list[investment.name]

    #print(f"current capital: {current_capital}")
    #print(f"Investment difference: {investment_difference}")

    # check if given moral investments are valid
    moral_dict = round_information["game"]["morals"][0]
    moral_investment_sum = 0
    morals = ["housing_investment", "health_investment", "freetime_investment"]
    for moral in morals:
        if moral_dict[moral] < 0:
            return 1, {"error": "A moral investment cannot be smaller then 0."}
        else:
            if moral == "housing_investment":
                moral_investment_sum += moral_obj.housing_investment - moral_dict[moral]
            elif moral == "health_investment":
                moral_investment_sum += moral_obj.health_investment - moral_dict[moral]
            elif moral == "freetime_investment":
                moral_investment_sum += moral_obj.freetime_investment - moral_dict[moral]

    # Check if the total amount of money which is invested exceeds the total capital
    if current_capital + investment_difference + moral_investment_sum < 0:
        return 1, {"error": "Investment exceeds the total capital."}
    return 0, {}


def validate_json(round_information, game, round) -> (int, dict):
    try:
        response_category_list = {
            item['category']['name']: [investment['investment']['name'] for investment in item['investments']] for item
            in round_information["category_investments"]}
    except Exception as e:
        return 1, {"error": "Failed to validate request."}

    # check if all categories and its investments are in the request
    categories = Category.objects.all()
    for category in categories:
        if category.name in response_category_list.keys():
            for investment in Investment.objects.filter(category=category):
                if investment.name not in response_category_list[category.name]:
                    return 1, {
                        "error": f"A investment ({investment.name}) of category {category.name} is missing in the request."}
        else:
            return 1, {"error": f"The category {category.name} is not in the response."}

    # check if all moral investments were given
    try:
        morals = ["housing_investment", "health_investment", "freetime_investment"]
        for moral in morals:
            if moral not in round_information["game"]["morals"][0]:
                return 1, {"error": f"Moral {moral} was missing in body."}
    except Exception as e:
        return 1, {"error": "Failed to validate request."}

    return 0, {}
# endregion
