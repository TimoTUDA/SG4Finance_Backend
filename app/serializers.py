from rest_framework import serializers
from app.models import Game, Investment, RoundInvestment, RoundCategoryInvestment, Category, Round, Event, Morals, \
    MoralEvent, Gamemode, Lobby


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = 'name',


class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = 'name',


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('name', 'text', 'value')


class MoralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Morals
        fields = (
            'housing_investment', 'housing_max', 'health_investment', 'health_max', 'freetime_investment',
            'freetime_max')


class MoralEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoralEvent
        fields = ('name', 'text', 'value', 'moral_operation_type')


class RoundInvestmentSerializer(serializers.ModelSerializer):
    investment = InvestmentSerializer(read_only=True)

    class Meta:
        model = RoundInvestment
        fields = ('investment', 'overall_amount', 'difference_amount', 'difference_percent', 'asset_value')


class RoundCategoryInvestmentSerializer(serializers.ModelSerializer):
    investments = RoundInvestmentSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = RoundCategoryInvestment
        fields = ('category', 'category_overall_amount', 'category_difference_amount', 'category_difference_percent',
                  'investments')


class GamemodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gamemode
        fields = ('end_round', 'round_salary', 'probability_event', 'win_threshold', 'inflation', 'rounds_to_win','start_capital')


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('player_name','current_round','current_capital','previous_capital','current_investment','previous_investment')

class LobbySerializer(serializers.ModelSerializer):
    players = serializers.SerializerMethodField('get_players')

    def get_players(self, lobby):
        games = Game.objects.filter(lobby=lobby)
        return PlayerSerializer(games, many=True, read_only=True).data

    class Meta:
        model = Lobby
        fields = ('access_key', 'number_of_players', 'private', 'players')

class GameSerializer(serializers.ModelSerializer):
    morals = MoralSerializer(many=True, read_only=True)
    gamemode = GamemodeSerializer(read_only=True)
    lobby = LobbySerializer(read_only=True)

    class Meta:
        model = Game
        fields = ('access_token', 'current_capital', 'previous_capital', 'current_investment', 'won', 'won_description', 'current_round', 'morals', 'winning_rounds', 'gamemode', 'round_salary_multiplier', 'player_name', 'lobby')


class RoundSerializer(serializers.ModelSerializer):
    category_investments = RoundCategoryInvestmentSerializer(many=True, read_only=True)
    game = GameSerializer(read_only=True)
    event = EventSerializer(read_only=True)
    moralEvent = MoralEventSerializer()

    class Meta:
        model = Round
        fields = ('category_investments', 'game', 'event', 'moralEvent','start_capital','end_capital','start_investment','end_investment')


# region History
class HistoryRoundCategoryInvestmentSerializer(serializers.ModelSerializer):
    investments = RoundInvestmentSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = RoundCategoryInvestment
        fields = ('category', 'category_overall_amount', 'category_difference_amount', 'category_difference_percent',
                  'investments')


class HistoryRoundSerializer(serializers.ModelSerializer):
    category_investments = HistoryRoundCategoryInvestmentSerializer(many=True, read_only=True)

    class Meta:
        model = Round
        fields = ('round_number', 'category_investments', 'event')

    def to_representation(self, instance):
        self._context["category"] = self.parent.context["category"]
        data = super(HistoryRoundSerializer, self).to_representation(instance)
        category_investments_list = data['category_investments']
        category_investments_list = [item for item in category_investments_list if
                                     item['category']['name'] == self.context['category']]
        data['category_investments'] = category_investments_list
        return data


class GameHistorySerializer(serializers.ModelSerializer):
    rounds = HistoryRoundSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = 'rounds',
# endregion
