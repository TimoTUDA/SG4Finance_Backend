import random
import string

from .gameLogic import *
from django.http import JsonResponse
from app.models import Game, Investment, Round
from app.serializers import RoundSerializer, InvestmentSerializer, GameHistorySerializer, LobbySerializer, GamemodeSerializer
from rest_framework import viewsets
import json


class GameViewSet(viewsets.ModelViewSet):
    http_method_names = ['post', 'get']
    queryset = Game.objects.all()
    serializer_class = RoundSerializer

    # POST
    def create(self, request):
        """
        Creates new game
        -----
        # Description:

        Creates a new game

        # Request:

        # Responses:
        - HTTP 200:


        ```
        {
        "category_investments": [
            {
                "category": {
                    "name": "Krypto"
                },
                "category_overall_amount": 0,
                "category_difference_amount": 0,
                "category_difference_percent": 0.0,
                "investments": [
                    {
                        "investment": {
                            "name": "Bitcoin"
                        },
                        "overall_amount": 0,
                        "difference_amount": 0,
                        "difference_percent": -0.112,
                        "asset_value": 17760.0
                    },
                    {
                        "investment": {
                            "name": "Ethereum"
                        },
                        "overall_amount": 0,
                        "difference_amount": 0,
                        "difference_percent": 0.072,
                        "asset_value": 1608.0
                    }
                ]
            },
            ... more Categories
        ],
            "game": {
                "access_token": "JRCxugsMS7AQ3ORJlp1O",
                "current_capital": 40000,
                "current_investment": 0,
                "won": null,
                "won_description": null,
                "current_round": 2,
                "morals": [
                    {
                        "housing_investment": 0,
                        "housing_max": 250,
                        "health_investment": 0,
                        "health_max": 250,
                        "freetime_investment": 0,
                        "freetime_max": 250
                    }
                ]
            },
            "event": null OR {
                "name": "The Big Hack",
                "text": "Some Text"
            },
            "moralEvent": null OR {
                "name": "Name"
                "text": "Some Text"
            }
        }
        ```

         - HTTP 401: ```{"error": "Access Token missing"} ```
         - HTTP 406: ```{"error": "Access Token does not exist"}```
        """
        try:
            
            request_body = str(request.body, 'utf-8')
            attributes = request_body.split(":", 4)

             #check if this is the settings JSON or an actual start-Game
            if request_body.endswith('}') or request_body.startswith('{'):
                #check for sandbox mode
                values = {}
                # Remove leading and trailing { } characters
                values = json.loads(request_body)

                if values['mode'] == "sandbox":
                    #the gamemode with id 10 is supposed to be the sandbox mode
                    gamemode_id=10
                    #print("angekommen2")  
                    #print(attributes)
                    return JsonResponse(GamemodeSerializer(create_sandbox(gamemode_id,
                    values['end_round'],values['round_salary'],values['probability_event'],
                    values['win_threshold'],values['inflation'],values['rounds_to_win'],values['start_capital'])).data, safe=False)

            if attributes[0] == "":
                attributes[0] = "Spieler"+"".join(random.choice(string.digits) for _ in range(5))

            gamemode_id = 0
            if attributes[1] == "arm":
                gamemode_id += 1
            elif attributes[1] == "normal":
                gamemode_id += 2
            elif attributes[1] == "reich":
                gamemode_id += 3

            if attributes[2] == "langfristige Planung":
                gamemode_id += 0
            elif attributes[2] == "hoher Gewinn":
                gamemode_id += 3
            elif attributes[2] == "arbeitslos":
                gamemode_id += 6
            elif attributes[2] == "sandbox":
                gamemode_id = 10
            

            if attributes[3] == '0':
                return JsonResponse(RoundSerializer(create_game(attributes[0], gamemode_id, False, None)).data, safe=False)
            elif attributes[3] == '1':
                return JsonResponse(RoundSerializer(create_game(attributes[0], gamemode_id, True, None)).data, safe=False)
            return JsonResponse(RoundSerializer(create_game(attributes[0], gamemode_id, True, attributes[3])).data, safe=False)

        except Exception as ex:
            print(ex.with_traceback())
            return JsonResponse({"error": "Cannot create game"}, status=500)

    # GET /app/game/<id>
    # NOT USED
    def retrieve(self, request, *args, **kwargs):
        """
            ***This method is not allowed by the backend***
        """
        return JsonResponse({"error": "Not allowed"})

    # GET
    def list(self, request, *args, **kwargs):
        """
        Returns current Information
        ---
        # Description:

        Returns the current information of the game for the given accessToken

        # Request:

        Authorization = "accessToken" (accessToken ist der 'access_token' der nach dem POST zurückgegeben wurde)

        # Responses:
        - HTTP 200:


        ```
        {
        "category_investments": [
            {
                "category": {
                    "name": "Krypto"
                },
                "category_overall_amount": 0,
                "category_difference_amount": 0,
                "category_difference_percent": 0.0,
                "investments": [
                    {
                        "investment": {
                            "name": "Bitcoin"
                        },
                        "overall_amount": 0,
                        "difference_amount": 0,
                        "difference_percent": -0.112,
                        "asset_value": 17760.0
                    },
                    {
                        "investment": {
                            "name": "Ethereum"
                        },
                        "overall_amount": 0,
                        "difference_amount": 0,
                        "difference_percent": 0.072,
                        "asset_value": 1608.0
                    }
                ]
            },
            ... more Categories
        ],
            "game": {
                "access_token": "JRCxugsMS7AQ3ORJlp1O",
                "current_capital": 40000,
                "current_investment": 0,
                "won": null,
                "won_description": null,
                "current_round": 2,
                "morals": [
                    {
                        "housing_investment": 0,
                        "housing_max": 250,
                        "health_investment": 0,
                        "health_max": 250,
                        "freetime_investment": 0,
                        "freetime_max": 250
                    }
                ]
            },
            "event": null OR {
                "name": "The Big Hack",
                "text": null OR string
            },
            "moralEvent": null OR {
                "name": "Name"
                "text": "Some Text"
            }
        }
        ```

         - HTTP 401: ```{"error": "Access Token missing"} ```
         - HTTP 406: ```{"error": "Access Token does not exist"}```

        """
        if request.META.get('HTTP_AUTHORIZATION') is None:
            return JsonResponse({"error": "Access Token missing"}, status=401)
        access_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
        game = Game.objects.filter(access_token=access_token).first()
        if game is None:
            return JsonResponse({"error": "Access Token does not exist"}, status=406)
        round_obj = Round.objects.filter(game=game, round_number=game.current_round).first()
        if round_obj is None:
            return JsonResponse({"error": "Round does not exist"}, status=406)

        return JsonResponse(RoundSerializer(round_obj).data)


# /app/round/
class RoundViewSet(viewsets.ModelViewSet):
    http_method_names = ['post']
    queryset = Game.objects.all()
    serializer_class = RoundSerializer

    # POST
    def create(self, request):
        """
        Close a round by submitting data
        -----

        # Description:

        Used to send the information about the finished round to the backend

        # Request:
        
        ```
        Authorization = "accessToken" (accessToken ist der 'access_token' der nach dem POST zurückgegeben wurde)

        {
            "category_investments": [
                {
                    "category": {
                        "name": "Krypto"
                    },
                    "investments": [
                        {
                            "investment": {
                                "name": "Bitcoin"
                            },
                            "overall_amount": 0
                        }
                    ]
                },
                {
                    "category": {
                        "name": "ETF"
                    },
                    "investments": [
                        {
                            "investment": {
                                "name": "MSCI_World"
                            },
                            "overall_amount": 0
                        }
                    ]
                },
                ...more Categories
            ],
            "game": {
                "morals": [
                    {
                        "housing_investment": 125,
                        "health_investment": 0,
                        "freetime_investment": 125
                    }
                ]
            }
        }
        ```

        # Responses:
        - HTTP 200: Same json as in game
        - HTTP 200: ```{"information": "End of game reached!"}```
        - HTTP 400: ```{"error": "Investment cannot be < 0."} ```
        - HTTP 400: ```{"error": "Investment exceeds the total capital."} ```
        - HTTP 400: ```{"error": "A investment InvestmentName of category CategoryName is missing in the request."} ```
        - HTTP 400: ```{"error": "The category CategoryName is not in the response."} ```
        - HTTP 401: ```{"error": "Access Token missing"} ```
        - HTTP 406: ```{"error": "Access Token does not exist"}```

        """
        if request.META.get('HTTP_AUTHORIZATION') is None:
            return JsonResponse({"error": "Access Token missing"}, status=401)
        access_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]

        game = Game.objects.filter(access_token=access_token).first()
        if game is None:
            return JsonResponse({"error": "Access Token does not exist"}, status=406)
        round_obj = Round.objects.filter(game=game, round_number=game.current_round).first()
        if round_obj is None:
            return JsonResponse({"error": "Round does not exist"}, status=406)
        request_body = json.loads(request.body)

        # Validate the Request
        (error_code, error_message) = validate_round_request(request_body, game, round_obj)
        if error_code != 0:
            return JsonResponse(error_message, status=400)

        # Update
        new_round = updateGame(request_body, game, round_obj)

        if not new_round:
            return JsonResponse({"information": "End of game reached!"})

        response = RoundSerializer(new_round).data
        if game.won is not None: 
            if game.lobby is None:
                game.delete()
            else:
                games_in_lobby = Game.objects.filter(lobby=game.lobby)
                if all(i.won is not None for i in games_in_lobby):
                    game.lobby.delete()

        return JsonResponse(response)


# /app/investment/
class InvestmentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Investment.objects.all()
    serializer_class = InvestmentSerializer

    # GET
    def list(self, request):
        """
            Returns all the investments of a game for a given category for all past rounds.
            ---
        # Description:

        Used to send the information about the finished round to the backend

        # Request:
        
        ```
        Authorization = "accessToken" (accessToken ist der 'access_token' der nach dem POST zurückgegeben wurde)
        {"category":"CategoryName"}
        ```

        # Responses:
        - HTTP 200: 
        ```
        {
            "rounds": [
                {
                    "round_number": 1,
                    "category_investments": [
                        {
                            "category": {
                                "name": "ETF"
                            },
                            "category_overall_amount": 0,
                            "category_difference_amount": 0,
                            "category_difference_percent": 0.0,
                            "investments": [
                                {
                                    "investment": {
                                        "name": "MSCI_World"
                                    },
                                    "overall_amount": 0,
                                    "difference_amount": 0,
                                    "difference_percent": 0.0,
                                    "asset_value": 70.0
                                }
                            ]
                        }
                    ],
                    "event": null
                },
                {
                    "round_number": 2,
                    "category_investments": [
                        {
                            "category": {
                                "name": "ETF"
                            },
                            "category_overall_amount": 0,
                            "category_difference_amount": 0,
                            "category_difference_percent": 0.0,
                            "investments": [
                                {
                                    "investment": {
                                        "name": "MSCI_World"
                                    },
                                    "overall_amount": 0,
                                    "difference_amount": 0,
                                    "difference_percent": -0.035,
                                    "asset_value": 67.55
                                }
                            ]
                        }
                    ],
                    "event": 6
                },
                ...more Rounds
            ]
        }
        ```

        - HTTP 401: ```{"error": "Access Token missing"} ```
        - HTTP 406: ```{"error": "Access Token does not exist"}```
        """
        if request.META.get('HTTP_AUTHORIZATION') is None:
            return JsonResponse({"error": "Access Token missing"}, status=401)
        access_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
        try:
            request_body = json.loads(request.GET['category'])
        except:
            request_body = request.POST['category']
        if request_body is None:
            return JsonResponse({"error": "category not given"}, status=401)
        filter_category = request_body
        game = Game.objects.filter(access_token=access_token).first()
        if game is None:
            return JsonResponse({"error": "Access Token does not exist"}, status=406)
        return JsonResponse(GameHistorySerializer(game, context={'category': filter_category}).data)

    # NOT USED
    # GET
    def retrieve(self, request):
        """
            ***This method is not allowed by the backend***
        """
        return JsonResponse({"error": "Not allowed"})


class MultiplayerViewSet(viewsets.ModelViewSet):
    http_method_names = ['post', 'get']
    queryset = Game.objects.all()
    serializer_class = LobbySerializer

    # GET
    def retrieve(self, request, *args, **kwargs):
        try:
            if request.META.get('HTTP_AUTHORIZATION') is None:
                return JsonResponse({"error": "Access Token missing"}, status=401)

            access_token = request.META.get('HTTP_AUTHORIZATION').split(' ')[-1]
            game = Game.objects.filter(access_token=access_token).first()

            if game is None:
                return JsonResponse({"error": "Access Token does not exist"}, status=406)

            request_body = json.loads(request.body)
            lobby = Lobby.objects.filter(access_key=request_body).first()

            if lobby is None:
                return JsonResponse({"error": "Lobby not found"}, status=400)
            return JsonResponse(LobbySerializer(lobby).data)

        except Exception as ex:
            print(ex.with_traceback())
            return JsonResponse({"error": "Cannot search lobby"}, status=500)

    def list(self, request, *args, **kwargs):
        try:
            lobbies = Lobby.objects.all()
            return JsonResponse(LobbySerializer(lobbies, many=True).data)

        except Exception as ex:
            print(ex.with_traceback())
            return JsonResponse({"error": "Cannot search lobby"}, status=500)
