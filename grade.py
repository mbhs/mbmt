import math

from grading import grading


individual_bonus_cache = {}


def calculate_bonuses(round):
    """Calculate the point bonuses for an individual round."""

    for question in round.questions:
        pass


def grade_subject_test(round, student):
    """Grade an individual subject test by round."""

    score = 0
    for question in round.questions:
        answer = models.Answer.objects.filter(question=question, student=student).first()
        if not answer:
            return None
        if question.type == models.QUESTION_TYPES["correct"]:
            score   += 1


@grade_for("subject1")
@grade_for("subject2")
def grade_subject_tests(competition=None):
    """Grade all individual scores."""

    pass


@grade_for("guts")
def grade_guts(competition=None):
    """Grade guts rounds for all teams."""

    competition = competition or models.Competition.current()
    guts = competition.rounds.filter(id="guts")
    scores = {}

    for team in models.Team.objects.all():
        score = 0
        for question in guts.questions:

            answer = models.Answer.filter(team=team, question=question).first()
            if not answer:
                score = None
                break

            value = 0
            if question.type == models.QUESTION_TYPES["correct"]:
                value = answer.value
            elif question.type == models.QUESTION_TYPES["estimation"]:
                e = answer.value
                a = question.answer
                value = max(0, 12 - math.log10(max(e/a, a/e)))

            score += value * question.weight

        try:
            scores[team.division][team.name] = score
        except IndexError:
            scores[team.division] = {}

    for division in scores:
        scores[division] = list(sorted(((team, scores[division][team]) for team in scores[division])))

    return scores
