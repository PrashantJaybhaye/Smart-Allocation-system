class AllocationEngine:
    def __init__(self, student_df, course_capacities):
        """
        :param student_df: Pandas DataFrame with student details and preferences.
        :param course_capacities: Dictionary { 'Course Name': capacity }
        """
        self.students = student_df.to_dict('records')
        self.capacities = course_capacities.copy()
        self.allocations = []
        self.course_usage = {course: 0 for course in course_capacities}

    def allocate(self):
        """
        Performs the allocation based on preferences.
        """
        if not self.students:
            return []

        # Dynamically find all "Preference X" columns and sort them correctly
        pref_cols = [col for col in self.students[0].keys() if 'Preference' in col]
        pref_cols.sort() # Sorting ensures Preference 1 < Preference 2 < Preference 3 etc.
        
        for student in self.students:
            allocated_course = "Unassigned"
            
            # Check preferences in order
            for pref_col in pref_cols:
                desired_course = student.get(pref_col)
                
                # Skip if empty or not in capacities
                if not desired_course or desired_course not in self.capacities:
                    continue
                    
                # If the course has space
                if self.course_usage[desired_course] < self.capacities[desired_course]:
                    allocated_course = desired_course
                    self.course_usage[desired_course] += 1
                    break
            
            # Prepare result entry
            result = student.copy()
            result['Allocated Course'] = allocated_course
            self.allocations.append(result)
            
        return self.allocations

    def get_summary(self):
        """
        Returns a summary of course usage.
        """
        return {
            "course_usage": self.course_usage,
            "total_students": len(self.students),
            "assigned_students": sum(self.course_usage.values()),
            "unassigned_students": len(self.students) - sum(self.course_usage.values())
        }
