grading_functions = {}


def register(round_names, question_indices):
    """Register a function as a grading function."""

    def decorator(function):
        grading_functions[name] = function
        return function
    return decorator


def grade(competition=None):
    """Do grading."""

    competition = competition or models.Competition.current()
    scoreboard = {"individual": {}, "team": {}}

    individual_rounds = competition.rounds.filter(models.ROUND_GROUPINGS["individual"]).all()
    individual_correct = {r: {q: 0 for q in r.questions} for r in individual_rounds}
    for r in individual_rounds:
        for q in r.questions.all():
            individual_correct[r][q] = sum([a.value for a in models.Answer.filter(question=q).all()])

    for student in models.Student.objects.all():
        pass
