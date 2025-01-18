import matplotlib.pyplot as plt
import random
import time
from deap import base, creator, tools

# Mock classes to simulate Django models
class MockModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

mock_courses = [
    MockModel(id=1, name="FR1", teachers=[1, 2], weekly_classes=3),
    MockModel(id=2, name="FR2", teachers=[1, 2], weekly_classes=3),
    MockModel(id=3, name="GER1", teachers=[3, 5], weekly_classes=3),
    MockModel(id=4, name="GER2", teachers=[3], weekly_classes=2),
    MockModel(id=5, name="POL1", teachers=[1, 2, 3], weekly_classes=3),
    MockModel(id=6, name="POL2", teachers=[1, 2, 3], weekly_classes=2),
    MockModel(id=7, name="ANG1", teachers=[2, 5], weekly_classes=2),
    MockModel(id=8, name="ANG2", teachers=[1, 5], weekly_classes=3),
]

mock_teachers = [
    MockModel(id=1, user=MockModel(last_name="Mieszko")), 
    MockModel(id=2, user=MockModel(last_name="Nowak")),
    MockModel(id=3, user=MockModel(last_name="Kowal")),  
    MockModel(id=4, user=MockModel(last_name="Wiśniewska")),  
    MockModel(id=5, user=MockModel(last_name="Orzeł")),  
]

mock_classrooms = [
    MockModel(id=1, name="101"), 
    MockModel(id=2, name="102"), 
    MockModel(id=3, name="103"), 
    MockModel(id=4, name="104"), 
    MockModel(id=5, name="105"),
    MockModel(id=6, name="106"),
]

mock_time_intervals = [
    MockModel(id=1, start_time="8:00", end_time="9:00"),  
    MockModel(id=2, start_time="9:00", end_time="10:00"),  
    MockModel(id=3, start_time="10:00", end_time="11:00"),  
    MockModel(id=4, start_time="11:00", end_time="12:00"),  
    MockModel(id=5, start_time="12:00", end_time="13:00"),  
]

mock_availability = [
    # Poniedziałek
    MockModel(day="Mon", time_interval=mock_time_intervals[0], classrooms=[mock_classrooms[0], mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1]]),
    MockModel(day="Mon", time_interval=mock_time_intervals[1], classrooms=[mock_classrooms[0], mock_classrooms[3], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Mon", time_interval=mock_time_intervals[2], classrooms=[mock_classrooms[0], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Mon", time_interval=mock_time_intervals[3], classrooms=[mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2]]),
    MockModel(day="Mon", time_interval=mock_time_intervals[4], classrooms=[mock_classrooms[1], mock_classrooms[2],  mock_classrooms[4]], employees=[mock_teachers[0], mock_teachers[4]]),
    
    # Wtorek
    MockModel(day="Tue", time_interval=mock_time_intervals[0], classrooms=[mock_classrooms[2], mock_classrooms[3], mock_classrooms[5]], employees=[mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Tue", time_interval=mock_time_intervals[1], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[4]]),
    MockModel(day="Tue", time_interval=mock_time_intervals[2], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[4]]),
    MockModel(day="Tue", time_interval=mock_time_intervals[3], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3],]),
    MockModel(day="Tue", time_interval=mock_time_intervals[4], classrooms=[], employees=[mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    
    # Środa
    MockModel(day="Wed", time_interval=mock_time_intervals[0], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Wed", time_interval=mock_time_intervals[1], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Wed", time_interval=mock_time_intervals[2], classrooms=[mock_classrooms[0], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0],  mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Wed", time_interval=mock_time_intervals[3], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0],  mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Wed", time_interval=mock_time_intervals[4], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    
    # Czwartek
    MockModel(day="Thu", time_interval=mock_time_intervals[0], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Thu", time_interval=mock_time_intervals[1], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Thu", time_interval=mock_time_intervals[2], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Thu", time_interval=mock_time_intervals[3], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Thu", time_interval=mock_time_intervals[4], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    
    # Piątek
    MockModel(day="Fri", time_interval=mock_time_intervals[0], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Fri", time_interval=mock_time_intervals[1], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Fri", time_interval=mock_time_intervals[2], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Fri", time_interval=mock_time_intervals[3], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Fri", time_interval=mock_time_intervals[4], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
]

mock_days = ["Mon", "Tue", "Wed", "Thu", "Fri"]


def genetic_algorithm_schedule(
    population_sizes=[50, 100, 200, 300, 500],
    generations=10000,
    elitism_size=2,
    runs_per_config=5,
):
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    available_time_slots = [(a.day, a.time_interval) for a in mock_availability]

    def generate_individual():
        individual = []
        for course in mock_courses:
            teacher_id = random.choice(course.teachers)
            teacher = next(t for t in mock_teachers if t.id == teacher_id)
            for _ in range(course.weekly_classes):
                day, time = random.choice(available_time_slots)
                individual.append(
                    [
                        course,  # 0: Course
                        day,  # 1: Day
                        time,  # 2: Time Interval
                        random.choice(mock_classrooms),  # 3: Classroom
                        teacher,  # 4: Teacher
                    ]
                )
        return individual

    toolbox.register(
        "individual", tools.initIterate, creator.Individual, generate_individual
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual):
        conflicts = 0
        scheduled_courses = {gene[0] for gene in individual}

        if len(scheduled_courses) != len(mock_courses):
            conflicts += len(mock_courses) - len(scheduled_courses)

        teacher_schedule = {}
        classroom_schedule = {}
        course_teacher_map = {}

        for schedule in individual:
            course, day, time_interval, classroom, teacher = schedule
            key = (day, time_interval)

            if course not in course_teacher_map:
                course_teacher_map[course] = teacher
            elif course_teacher_map[course] != teacher:
                conflicts += 1

            availability = [
                a
                for a in mock_availability
                if a.day == day and a.time_interval == time_interval
            ]
            if not any(
                teacher in a.employees and classroom in a.classrooms
                for a in availability
            ):
                conflicts += 1

            if key not in teacher_schedule:
                teacher_schedule[key] = set()
            if teacher in teacher_schedule[key]:
                conflicts += 1 
            else:
                teacher_schedule[key].add(teacher)

            if key not in classroom_schedule:
                classroom_schedule[key] = set()
            if classroom in classroom_schedule[key]:
                conflicts += 1 
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
                teacher = random.choice([t for t in mock_teachers if t.id in course.teachers])
                course_teacher_map[course] = teacher
            else:
                teacher = course_teacher_map[course]
            day, time = random.choice(available_time_slots)
            gene[1] = day
            gene[2] = time
            gene[3] = random.choice(mock_classrooms)
            gene[4] = teacher  
        return individual

    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", custom_crossover)
    toolbox.register("mutate", custom_mutation)
    toolbox.register("select", tools.selBest)

    results_iterations = {size: [] for size in population_sizes}
    results_times = {size: [] for size in population_sizes}

    for pop_size in population_sizes:
        iteration_conflicts = []
        time_conflicts = []

        for _ in range(runs_per_config):
            population = toolbox.population(n=pop_size)
            start_time = time.time()

            best_conflicts = []
            for gen in range(generations):
                elites = tools.selBest(population, elitism_size)

                offspring = toolbox.select(population, len(population) - elitism_size)
                offspring = list(map(toolbox.clone, offspring))

                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < 0.2:
                        toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values

                for mutant in offspring:
                    if random.random() < 0.7:
                        toolbox.mutate(mutant)
                        del mutant.fitness.values

                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = map(toolbox.evaluate, invalid_ind)
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit

                population[:] = elites + offspring
                best_ind = tools.selBest(population, 1)[0]

                best_conflicts.append(best_ind.fitness.values[0])

            iteration_conflicts.append(best_conflicts)
            time_conflicts.append((time.time() - start_time, best_ind.fitness.values[0]))

        avg_iterations = [
            sum(conflicts[i] for conflicts in iteration_conflicts) / runs_per_config
            for i in range(generations)
        ]
        results_iterations[pop_size] = avg_iterations

        avg_times = sum(t[0] for t in time_conflicts) / runs_per_config
        avg_final_conflicts = sum(t[1] for t in time_conflicts) / runs_per_config
        results_times[pop_size] = (avg_times, avg_final_conflicts)

    plt.figure(figsize=(10, 6))
    for pop_size, conflicts in results_iterations.items():
        plt.plot(conflicts, label=f"Populacja: {pop_size}")
    plt.xlabel("Pokolenia")
    plt.ylabel("Liczba konfliktów")
    plt.title("Liczba konfliktów w zależności od liczby pokoleń")
    plt.legend()
    plt.grid()
    plt.savefig("conflicts_vs_iterations.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    for pop_size, (avg_time, avg_conflicts) in results_times.items():
        plt.bar(
            f"Pop: {pop_size}", avg_conflicts, label=f"Czas: {avg_time:.2f}s"
        )
    plt.xlabel("Rozmiar populacji")
    plt.ylabel("Liczba konfliktów")
    plt.title("Liczba konfliktów w zależności od czasu")
    plt.legend()
    plt.grid()
    plt.savefig("conflicts_vs_time.png")
    plt.close()


genetic_algorithm_schedule()
