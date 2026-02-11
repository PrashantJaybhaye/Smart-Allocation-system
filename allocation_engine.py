class AllocationEngine:
    def __init__(self, students, courses):
        """
        :param students: List of Student model objects
        :param courses: List of Course model objects
        """
        # Sort students by priority: GPA (descending) and then Submission Time (ascending)
        self.students = sorted(students, key=lambda s: (-s.gpa, s.submission_time))
        self.courses = {c.name: c for c in courses}
        self.course_usage = {c.name: 0 for c in courses}
        self.allocations = []

    def allocate(self):
        """
        Performs priority-based allocation.
        """
        # Reset state to allow multiple calls without corruption
        self.allocations = []
        for c in self.courses.values():
            self.course_usage[c.name] = 0
            # Reset student records for a clean run if necessary
            # (assuming the caller handles DB session or we update them here)
            
        for student in self.students:
            allocated_course_name = "Unassigned"
            prefs = student.preferences or []
            
            for course_name in prefs:
                if course_name in self.courses:
                    course = self.courses[course_name]
                    if self.course_usage[course_name] < course.capacity:
                        allocated_course_name = course_name
                        self.course_usage[course_name] += 1
                        student.allocated_course_id = course.id
                        student.allocation_status = 'Allocated'
                        break
            
            if allocated_course_name == "Unassigned":
                student.allocation_status = 'Unassigned'
            
            self.allocations.append({
                'Student ID': student.student_id,
                'Name': student.name,
                'GPA': student.gpa,
                'Allocated Course': allocated_course_name,
                'Status': student.allocation_status
            })
            
        return self.allocations

    def get_analytics(self):
        """
        Returns stats for the dashboard.
        """
        total = len(self.students)
        assigned = sum(1 for s in self.students if getattr(s, 'allocation_status', 'Unallocated') == 'Allocated')
        
        # Course Demand (count how many students put each course as 1st preference)
        demand = {}
        for s in self.students:
            if s.preferences:
                first_pref = s.preferences[0]
                demand[first_pref] = demand.get(first_pref, 0) + 1

        return {
            "total_students": total,
            "assigned_count": assigned,
            "assigned_students": assigned,  # for compatibility
            "unassigned_students": total - assigned,
            "satisfaction_rate": (assigned / total * 100) if total > 0 else 0,
            "course_demand": demand,
            "occupancy": {name: (usage / self.courses[name].capacity * 100) 
                          if self.courses[name].capacity > 0 else 0
                          for name, usage in self.course_usage.items()}
        }
