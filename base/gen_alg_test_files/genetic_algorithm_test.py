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
    MockModel(day="Mon", time_interval=mock_time_intervals[0], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Mon", time_interval=mock_time_intervals[1], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Mon", time_interval=mock_time_intervals[2], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Mon", time_interval=mock_time_intervals[3], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Mon", time_interval=mock_time_intervals[4], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    
    # Wtorek
    MockModel(day="Tue", time_interval=mock_time_intervals[0], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Tue", time_interval=mock_time_intervals[1], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Tue", time_interval=mock_time_intervals[2], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Tue", time_interval=mock_time_intervals[3], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Tue", time_interval=mock_time_intervals[4], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    
    # Środa
    MockModel(day="Wed", time_interval=mock_time_intervals[0], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Wed", time_interval=mock_time_intervals[1], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Wed", time_interval=mock_time_intervals[2], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Wed", time_interval=mock_time_intervals[3], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    MockModel(day="Wed", time_interval=mock_time_intervals[4], classrooms=[mock_classrooms[0], mock_classrooms[1], mock_classrooms[2], mock_classrooms[3],  mock_classrooms[4], mock_classrooms[5]], employees=[mock_teachers[0], mock_teachers[1], mock_teachers[2],mock_teachers[3], mock_teachers[4]]),
    
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
