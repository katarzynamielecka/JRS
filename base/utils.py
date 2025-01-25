import random
from deap import base, creator, tools
from .models import LanguageCourse, Employee, Classroom, Availability, TimeInterval, Semester

elitism_size = 1
def genetic_algorithm_schedule(population_size=100, generations=10000):

    toolbox = base.Toolbox()
    if not hasattr(creator, "FitnessMin"):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMin)
    current_semesters = Semester.get_current_semesters()
    courses = list(LanguageCourse.objects.filter(semesters__in=current_semesters).distinct())
    classrooms = list(Classroom.objects.all())
    teachers = list(Employee.objects.filter(courses__isnull=False).distinct())
    availability = Availability.objects.all()
    time_intervals = TimeInterval.objects.filter(
        id__in=Availability.objects.values_list("time_interval", flat=True).distinct()
    )
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    if not courses or not classrooms or not teachers or not time_intervals:
        raise ValueError("Brakuje danych wejściowych do algorytmu (kursy, sale, nauczyciele lub interwały czasowe).")
    available_time_slots = [(a.day, a.time_interval) for a in availability.all()]
    def generate_individual():
        individual = []
        for course in courses:
            teacher = random.choice(course.teachers.all())
            for _ in range(course.weekly_classes):
                day, time = random.choice(available_time_slots)
                individual.append([
                    course,                        # 0: Kurs
                    day,                           # 1: Dzień
                    time,                          # 2: Interwał czasu
                    random.choice(classrooms),     # 3: Sala
                    teacher                        # 4: Ten sam nauczyciel dla danego kursu
                ])
        return individual


    toolbox.register("individual", tools.initIterate, creator.Individual, generate_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual):
        conflicts = 0

        scheduled_courses = {gene[0] for gene in individual}
        if len(scheduled_courses) != len(courses):
            conflicts += len(courses) - len(scheduled_courses)


        teacher_schedule = {}
        classroom_schedule = {}

        for schedule in individual:
            course, day, time_interval, classroom, teacher = schedule
            key = (day, time_interval)

            availability_teachers_classrooms = [
                a
                for a in availability.all()
                if a.day == day and a.time_interval == time_interval
            ]
            if not any(
                teacher in a.employees.all() and classroom in a.classrooms.all()
                for a in availability_teachers_classrooms
            ):
                conflicts += 1


            if key not in teacher_schedule:
                teacher_schedule[key] = set()
            if teacher in teacher_schedule[key]:
                conflicts += 1  # Konflikt: nauczyciel zarezerwowany dwa razy
            else:
                teacher_schedule[key].add(teacher)

            if key not in classroom_schedule:
                classroom_schedule[key] = set()
            if classroom in classroom_schedule[key]:
                conflicts += 1  # Konflikt: sala zarezerwowana dwa razy
            else:
                classroom_schedule[key].add(classroom)

        return (conflicts,)

    def custom_crossover(parent1, parent2):
        child1 = []
        child2 = []
        for gene1, gene2 in zip(parent1, parent2):
            new_gene1 = [gene1[0], gene2[1], gene2[2], gene2[3], gene1[4]]
            new_gene2 = [gene2[0], gene1[1], gene1[2], gene1[3], gene2[4]]
            child1.append(new_gene1)
            child2.append(new_gene2)
        return creator.Individual(child1), creator.Individual(child2)


    def custom_mutation(individual):
        course_teacher_map = {} 
        for gene in individual:
            course = gene[0]
            if course not in course_teacher_map:
                teacher = random.choice([t for t in teachers if t in course.teachers.all()])
                course_teacher_map[course] = teacher
            else:
                teacher = course_teacher_map[course]
            day, time = random.choice(available_time_slots)
            gene[1] = day
            gene[2] = time
            gene[3] = random.choice(classrooms)
            gene[4] = teacher  
        return individual


    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", custom_crossover)
    toolbox.register("mutate", custom_mutation)
    toolbox.register("select", tools.selTournament, tournsize=3)


    population = toolbox.population(n=population_size)
    for gen in range(generations):
        elites = tools.selBest(population, elitism_size)

        offspring = toolbox.select(population, len(population) - elitism_size)
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.1:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            toolbox.mutate(mutant)
            del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        population[:] = elites + offspring
        best_ind = tools.selBest(population, 1)[0]
        if best_ind.fitness.values[0] == 0: 
            break

    conflicts = best_ind.fitness.values[0]
    return best_ind, conflicts