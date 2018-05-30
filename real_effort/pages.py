from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants, levenshtein, distance_and_ok
from django.conf import settings

class Introduction(Page):
    """Description of the game: How to play and returns expected"""
    pass

class Transcribe(Page):
    form_model = 'player'
    form_fields = ['transcribed_text']

    # Don't display this Transcribe page if the "transcription" value in
    # the dictionary representing this round in config.py is False
    def is_displayed(self):
        if (Constants.config[0][self.round_number - 1]["transcription"] == False):
            return False

        # Don't display this Transcribe page for each player who has completed
        # the first transcription task
        for p in self.player.in_all_rounds():
            if(p.transcriptionDone):
                return False

        return True

    def vars_for_template(self):
        return {
            'image_path': 'real_effort/paragraphs/{}.png'.format(2), 
            'reference_text': Constants.reference_texts[1],
            'debug': settings.DEBUG,
            'required_accuracy': 100 * (1 - Constants.allowed_error_rates[1]),
        }

    def transcribed_text_error_message(self, transcribed_text):
        """Determines the player's transcription accuracy."""

        reference_text = Constants.reference_texts[1]
        allowed_error_rate = Constants.allowed_error_rates[1]
        distance, ok = distance_and_ok(transcribed_text, reference_text,
                                       allowed_error_rate)
        if ok:
            self.player.levenshtein_distance = distance
            self.player.ratio = 1 - distance / Constants.maxdistance2
        else:
            if allowed_error_rate == 0:
                return "The transcription should be exactly the same as on the image."
            else:
                return "This transcription appears to contain too many errors."

    def before_next_page(self):
        """Initalize payoff to have a default value of 0"""

        self.player.payoff = 0

class Transcribe2(Page):
    form_model = 'player'
    form_fields = ['transcribed_text2']

    def is_displayed(self):
        # Don't display this Transcribe page if the "transcription" value in
        # the dictionary representing this round in config.py is False
        if (Constants.config[0][self.round_number - 1]["transcription"] == False):
            self.player.ratio = 1
            return False

        # Don't display this Transcribe page for each player who has completed
        # the second transcription task
        for p in self.player.in_all_rounds():
            if(p.transcriptionDone): 
                return False

        return True

    def vars_for_template(self):
        return {
            'image_path': 'real_effort/paragraphs/{}.png'.format(1),
            'reference_text': Constants.reference_texts[0],
            'debug': settings.DEBUG,
            'required_accuracy': 100 * (1 - Constants.allowed_error_rates[0]),
        }

    # Initalize a default value of 0 for each player's payoff
    def before_next_page(self):
        self.player.payoff = 0


class Results(Page):
    form_model = 'player'
    form_fields = []

    def is_displayed(self):
        # Don't display the Results page dispalying each player's transcription
        # accuracy (levenshtein value) if the "transcription" value in
        # the dictionary representing this round in config.py is False
        if (Constants.config[0][self.round_number - 1]["transcription"] == False):
            return False

        # Don't display this Results page for each player who has completed
        # the second transcription task
        for p in self.player.in_all_rounds():
            if(p.transcriptionDone):
                return False

        return True


    def vars_for_template(self):
        table_rows = []
        config = Constants.config
        self.player.income = config[0][self.round_number - 1]["end"]

        for prev_player in self.player.in_all_rounds(): # may be causing the wrong ratio 
        #income calculation done here
            if prev_player.transcribed_text == None:
                prev_player.transcribed_text = ""
                prev_player.levenshtein_distance = 0

            row = { 
                'round_number': prev_player.round_number,
                'reference_text_length': len(Constants.reference_texts[1]),
                'transcribed_text_length': len(prev_player.transcribed_text),
                'distance': prev_player.levenshtein_distance,
                'ratio':   1 - prev_player.levenshtein_distance / Constants.maxdistance2,
            }

            self.player.ratio = 1 - prev_player.levenshtein_distance / Constants.maxdistance2
            self.player.income *= self.player.ratio

            table_rows.append(row)

        return {'table_rows': table_rows}

    def before_next_page(self):
        # Disables transcription for the rest of the game
        self.player.transcriptionDone = True


class part2(Page):
    form_model = 'player'
    form_fields = ['contribution']

    def contribution_max(self):
        """Dynamically sets the maximum amount of his/her income that the player can report to be their income"""
        return self.player.income

    def vars_for_template(self):
        if self.player.ratio == 1 and Constants.config[0][self.round_number-1]["transcription"] == True:
            for p in self.player.in_all_rounds():
                if p.ratio < 1:
                    self.player.ratio = p.ratio
                    self.player.income *= self.player.ratio

        config = Constants.config

        # Displays the tax as a percentage rather than a decimal between 0 and 1
        self.player.ratio = round(self.player.ratio, 5)
        displaytax = config[0][self.round_number - 1]["tax"] * 100

        return{'ratio': self.player.ratio, 'income': self.player.income, 'tax': displaytax, 'flag': config[0][self.round_number-1]["transcription"]}


class resultsWaitPage(WaitPage):
    def after_all_players_arrive(self):
        # Group income calculation
        config = Constants.config

        group = self.group
        players = group.get_players()
        contributions = [p.contribution * config[0][int(self.round_number - 1)]["tax"] for p in players]
        group.total_contribution = sum(contributions)
        group.total_earnings = config[0][self.round_number-1]["multiplier"] * group.total_contribution
        group.individual_share = group.total_earnings / Constants.players_per_group

        for p in players:
            p.payoff = p.income - ( config[0][int(self.round_number - 1)]["tax"] * p.contribution) + group.individual_share


class results2(Page):
    def is_displayed(self):
        # May cause a problem, may change to something more direct later
        return self.player.payoff != 0

    def vars_for_template(self):
        config = Constants.config
        share = self.group.total_earnings / Constants.players_per_group

        return {
            'total_earnings': self.group.total_contribution * config[0][int(self.round_number-1)]["multiplier"], 'player_earnings': share
        }


page_sequence = [Introduction, Transcribe2, Transcribe, Results, part2, resultsWaitPage, results2]