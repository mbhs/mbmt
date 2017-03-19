import frontend.models
from . import models


ROUND = "round"
QUESTION = "question"


class CompetitionGrader:
    """Base class for a competition grader."""

    COMPETITION = ""

    def __init__(self):
        """Initialize the competition grader."""

        self.question_graders = {}
        self.round_graders = {}

    def default_question_grader(self, question, answer):
        """Default action for grading a question."""

        return question.weight * answer.value

    def default_individual_round_grader(self, round: models.Round):
        """Grade an individual round.

        Return a dictionary mapping team division to student to the
        student score.
        """

        scores = {}
        for student in frontend.models.Student.current():
            score = 0
            for question in round.questions.all():
                answer = models.Answer.objects.filter(student=student, question=question).first()
                score += self.question_graders.get(question.id, self.default_question_grader)(question, answer)

            # Account division
            try:
                scores[student.team.division][student] = score
            except IndexError:
                scores[student.team.division] = {student: score}

        return scores

    def default_team_round_grader(self, round: models.Round):
        """Grade a team round.

        Return a dictionary mapping team division to team to the
        team score.
        """

        scores = {}
        for team in frontend.models.Team.current():
            score = 0
            for question in round.questions.all():
                answer = models.Answer.objects.filter(team=team, question=question).first()
                if not answer:
                    score += 0
                    continue
                result = self.question_graders.get(question.id, self.default_question_grader)(question, answer)
                score += result or 0

            # Account for division
            try:
                scores[team.division][team] = score
            except IndexError:
                scores[team.division] = {team: score}

        return scores

    def default_round_grader(self, round):
        """Default action for grading a round."""

        if round.get_grouping_display() == "individual":
            return self.default_individual_round_grader(round)
        elif round.get_grouping_display() == "team":
            return self.default_team_round_grader(round)
        else:
            return None

    def register_question_grader(self, query, function):
        """Register a question grading function to a set of questions."""

        for question in models.Question.objects.filter(query, round__competition__id=self.COMPETITION).all():
            self.question_graders[question.id] = function

    def register_round_grader(self, query, function):
        """Register a round grading function to a set of questions."""

        for round in models.Question.objects.filter(query, round__competition__id=self.COMPETITION).all():
            self.round_graders[round.id] = function

    def grade_round(self, round):
        """Grade a round."""

        return self.round_graders.get(round.id, self.default_round_grader)(round)

    def grade_competition(self, competition):
        """Grade a competition."""

        if not self.COMPETITION == competition.id:
            print("Competition does not match grader type.")
            return None

        results = {}
        for round in competition:
            results[round.ref] = self.grade_round(round)

        return results
