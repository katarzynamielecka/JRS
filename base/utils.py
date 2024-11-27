import random
from deap import base, creator, tools
from .models import LanguageCourse, Employee, Classroom, Availability, ClassSchedule, TimeInterval

def genetic_algorithm_schedule(population_size=50, generations=100):
    print('1')
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()

    courses = list(LanguageCourse.objects.all())
    classrooms = list(Classroom.objects.all())
    teachers = list(Employee.objects.filter(courses__isnull=False).distinct())
    time_intervals = TimeInterval.objects.filter(
        id__in=Availability.objects.values_list("time_interval", flat=True).distinct()
    )
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    if not courses or not classrooms or not teachers or not time_intervals:
        raise ValueError("Brakuje danych wejściowych do algorytmu (kursy, sale, nauczyciele lub interwały czasowe).")

    def generate_individual():
        return [
            [
                course,                        # 0: Kurs - przypisany bezpośrednio
                random.choice(days),           # 1: Dzień
                random.choice(time_intervals), # 2: Interwał czasu
                random.choice(classrooms),     # 3: Sala
                random.choice(teachers),       # 4: Nauczyciel
            ]
            for course in courses
        ]

    toolbox.register("individual", tools.initIterate, creator.Individual, generate_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual):
        conflicts = 0
        
        # Zbiór wszystkich kursów w harmonogramie (powinno być równy `courses`)
        scheduled_courses = {gene[0] for gene in individual}

        # Sprawdź, czy wszystkie kursy są obecne
        if len(scheduled_courses) != len(courses):
            conflicts += len(courses) - len(scheduled_courses)

        for schedule in individual:
            if len(schedule) != 5:
                raise ValueError(f"Invalid schedule structure: {schedule}. Expected 5 elements.")
            course, day, time_interval, classroom, teacher = schedule

            availability = Availability.objects.filter(
                day=day,
                time_interval=time_interval
            )

            # Konflikt: sala nie jest dostępna
            if not availability.filter(classrooms=classroom).exists():
                conflicts += 1

            # Konflikt: nauczyciel nie jest dostępny
            if not availability.filter(employees=teacher).exists():
                conflicts += 1

            # Konflikt: nauczyciel przypisany do więcej niż jednego kursu w tym samym czasie
            teacher_conflicts = [
                s for s in individual
                if s[4] == teacher and s[1] == day and s[2] == time_interval
            ]
            if len(teacher_conflicts) > 1:
                conflicts += 1

        return (conflicts,)


    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)


    population = toolbox.population(n=population_size)

    for gen in range(generations):
        offspring = toolbox.select(population, len(population))
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.7:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < 0.2:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        population[:] = offspring

    best_ind = tools.selBest(population, 1)[0]
    print(f'rozwiazanie: {best_ind}')
    return best_ind
