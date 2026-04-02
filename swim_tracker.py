"""
swim_tracker.py

A terminal-based swim progress tracker featuring:
- Workout logging (distance, duration, type, rating, notes)
- Meet result logging with automatic time-change calculations
- Performance goal setting and tracking
- Formatted summaries for workouts, meets, and goals
"""


# ---------------------------------------------------------------------------
# Workout
# ---------------------------------------------------------------------------

class Workout:
    """
    Stores the details of a single swim workout.

    Attributes:
        date     (str): Workout date in MM/DD/YYYY format.
        distance (int): Distance swum in yards.
        duration (int): Duration in total minutes.
        wtype    (str): Workout type (e.g. Aerobic, Sprint, Recovery).
        rating   (int): Athlete's self-rating from 1 to 5.
        notes    (str): Optional notes about the session.
    """

    def __init__(self, date, distance, duration, wtype, rating, notes):
        self.date = date
        self.distance = distance
        self.duration = duration
        self.wtype = wtype
        self.rating = rating
        self.notes = notes

    def workout_summary(self):
        """Return a formatted summary string for this workout."""
        hours   = self.duration // 60
        minutes = self.duration % 60

        if hours == 0:
            duration_text = f"{minutes} minutes"
        elif minutes == 0:
            duration_text = f"{hours} hours"
        else:
            duration_text = f"{hours} hours {minutes} minutes"

        return (
            f"--Workout Summary--\n"
            f" Date: {self.date}\n"
            f" Distance: {self.distance} yards\n"
            f" Duration: {duration_text}\n"
            f" Workout type: {self.wtype}\n"
            f" Rating: {self.rating}/5\n"
            f" Notes: {self.notes}"
        )


# ---------------------------------------------------------------------------
# Goal
# ---------------------------------------------------------------------------

class Goal:
    """
    Stores a performance goal for a specific event.

    Attributes:
        event       (str): Target event (e.g. "100 Free").
        target_time (int): Target time in seconds.
    """

    def __init__(self, event, target_time):
        self.event = event
        self.target_time = target_time

    def goal_summary(self):
        """Return a formatted summary string for this goal."""
        minutes   = self.target_time // 60
        seconds   = self.target_time % 60
        time_text = f"{minutes} minutes {seconds} seconds"

        return (
            f"--Goal Summary--\n"
            f" Event: {self.event}\n"
            f" Target time: {time_text} ({self.target_time} seconds)"
        )


# ---------------------------------------------------------------------------
# MeetResult
# ---------------------------------------------------------------------------

class MeetResult:
    """
    Stores the outcome of a competitive swim meet for a single event.

    Attributes:
        date          (str):  Meet date in MM/DD/YYYY format.
        event         (str):  Event name (e.g. "200 IM").
        seed_time     (int):  Seed time in seconds.
        final_time    (int):  Final race time in seconds.
        notes         (str):  Optional notes.
        change_label  (str):  "Faster by", "Slower by", or "No change".
        change_amount (int):  Difference in seconds between seed and final.
        goal_status   (str):  Whether the athlete's goal was met.
    """

    def __init__(self, date, event, seed_time, final_time, notes):
        self.date = date
        self.event = event
        self.seed_time = seed_time
        self.final_time = final_time
        self.notes = notes
        self.change_label = None
        self.change_amount = None
        self.goal_status = None

    def _format_seconds(self, total_seconds):
        """Convert a raw second count to a human-readable time string."""
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        if minutes == 0:
            return f"{seconds} seconds"
        elif seconds == 0:
            return f"{minutes} minutes"
        else:
            return f"{minutes} minutes {seconds} seconds"

    def meet_results_summary(self):
        """Return a formatted summary string for this meet result."""
        seed_text  = self._format_seconds(self.seed_time)
        final_text = self._format_seconds(self.final_time)

        change_text = (
            "Not calculated yet"
            if self.change_label is None or self.change_amount is None
            else f"{self.change_label} {self.change_amount} seconds"
        )
        goal_text = self.goal_status if self.goal_status is not None else "No goal set yet"

        return (
            f"--Meet Summary--\n"
            f" Date: {self.date}\n"
            f" Event: {self.event}\n"
            f" Seed time: {seed_text}\n"
            f" Final time: {final_text}\n"
            f" Time change: {change_text}\n"
            f" Goal check: {goal_text}\n"
            f" Notes: {self.notes}"
        )


# ---------------------------------------------------------------------------
# Athlete
# ---------------------------------------------------------------------------

class Athlete:
    """
    Represents a swimmer and stores all their logged data.

    Attributes:
        name         (str):  Athlete's name.
        workouts     (list): Logged Workout objects.
        meet_results (list): Logged MeetResult objects.
        goal         (Goal): Current performance goal (or None).
    """

    def __init__(self, name):
        self.name = name
        self.workouts = []
        self.meet_results = []
        self.goal = None

    def add_workout(self, workout):
        """Add a Workout to the athlete's workout log."""
        self.workouts.append(workout)

    def add_meet_result(self, meet_result):
        """Add a MeetResult to the athlete's meet history."""
        self.meet_results.append(meet_result)

    def set_goal(self, goal):
        """Set or replace the athlete's current performance goal."""
        self.goal = goal


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

class Helper:
    """Static utility methods for parsing input and performing calculations."""

    @staticmethod
    def parse_duration_to_minutes(time_str):
        """Parse H:MM or plain MM string into total minutes (int)."""
        if ":" in time_str:
            parts = time_str.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        return int(time_str)

    @staticmethod
    def parse_time_to_seconds(time_str):
        """Parse M:SS or plain SS string into total seconds (int)."""
        if ":" in time_str:
            parts = time_str.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        return int(time_str)

    @staticmethod
    def safe_parse_duration_to_minutes(time_str):
        """Return parsed minutes or None if the input is invalid."""
        try:
            return Helper.parse_duration_to_minutes(time_str)
        except (ValueError, IndexError):
            return None

    @staticmethod
    def safe_parse_time_to_seconds(time_str):
        """Return parsed seconds or None if the input is invalid."""
        try:
            return Helper.parse_time_to_seconds(time_str)
        except (ValueError, IndexError):
            return None

    @staticmethod
    def safe_parse_int(value_str):
        """Return parsed integer or None if the input is invalid."""
        try:
            return int(value_str)
        except ValueError:
            return None

    @staticmethod
    def calculate_time_change(seed_time, final_time):
        """
        Compare seed and final times.
        Returns a (label, amount) tuple where label is one of:
        'Faster by', 'Slower by', or 'No change', and amount is the
        difference in seconds.
        """
        if final_time < seed_time:
            return "Faster by", seed_time - final_time
        elif final_time > seed_time:
            return "Slower by", final_time - seed_time
        else:
            return "No change", 0

    @staticmethod
    def determine_goal_status(goal, event, final_time):
        """
        Check whether the athlete met their goal for this event.
        Returns a descriptive status string.
        """
        if goal is None:
            return "No goal set"
        if goal.event.lower().strip() != event.lower().strip():
            return "Goal is for a different event"
        if final_time <= goal.target_time:
            return "Goal met!"
        return "Goal not met yet"


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

def menu():
    """Run the interactive swim tracker menu loop."""
    print("--Swim Progress Tracker--\n")
    name    = input("Enter your name: ")
    athlete = Athlete(name)

    while True:
        print()
        print("--Main Menu--")
        print("1. Log Workout")
        print("2. Log Meet Result")
        print("3. Set Goal")
        print("4. View Workouts")
        print("5. View Meet Results")
        print("6. View Goal")
        print("7. Exit")

        choice = input("Choose an option: ")
        print()

        # Option 1: Log a workout
        if choice == "1":
            date = input("Enter workout date (MM/DD/YYYY): ")

            while True:
                distance = Helper.safe_parse_int(input("Enter distance in yards: "))
                if distance is None or distance <= 0:
                    print("Invalid distance. Please enter a positive number.")
                else:
                    break

            while True:
                duration = Helper.safe_parse_duration_to_minutes(input("Enter duration (H:MM or MM): "))
                if duration is None or duration <= 0:
                    print("Invalid duration. Please use H:MM or MM format.")
                else:
                    break

            wtype = input("Enter workout type (e.g. Aerobic, Sprint, Technique, Recovery): ")

            while True:
                rating = Helper.safe_parse_int(input("Enter workout rating (1-5): "))
                if rating is None or rating < 1 or rating > 5:
                    print("Invalid rating. Please enter a number between 1 and 5.")
                else:
                    break

            notes   = input("Enter any notes: ")
            workout = Workout(date, distance, duration, wtype, rating, notes)
            athlete.add_workout(workout)
            print("\nWorkout logged:")
            print(workout.workout_summary())

        # Option 2: Log a meet result
        elif choice == "2":
            date  = input("Enter meet date (MM/DD/YYYY): ")
            event = input("Enter event (e.g. 100 Free, 200 IM): ")

            while True:
                seed_time = Helper.safe_parse_time_to_seconds(input("Enter seed time (M:SS or SS): "))
                if seed_time is None or seed_time <= 0:
                    print("Invalid seed time. Please use M:SS or SS format.")
                else:
                    break

            while True:
                final_time = Helper.safe_parse_time_to_seconds(input("Enter final time (M:SS or SS): "))
                if final_time is None or final_time <= 0:
                    print("Invalid final time. Please use M:SS or SS format.")
                else:
                    break

            notes = input("Enter any notes: ")
            meet  = MeetResult(date, event, seed_time, final_time, notes)

            # Calculate and attach time change and goal status
            meet.change_label, meet.change_amount = Helper.calculate_time_change(seed_time, final_time)
            meet.goal_status = Helper.determine_goal_status(athlete.goal, event, final_time)

            athlete.add_meet_result(meet)
            print("\nMeet result logged:")
            print(meet.meet_results_summary())

        # Option 3: Set a goal
        elif choice == "3":
            event = input("Enter goal event (e.g. 100 Free, 200 IM): ")

            while True:
                target_time = Helper.safe_parse_time_to_seconds(input("Enter target time (M:SS or SS): "))
                if target_time is None or target_time <= 0:
                    print("Invalid target time. Please use M:SS or SS format.")
                else:
                    break

            goal = Goal(event, target_time)
            athlete.set_goal(goal)
            print("\nGoal set:")
            print(goal.goal_summary())

        # Option 4: View all logged workouts
        elif choice == "4":
            if not athlete.workouts:
                print("No workouts logged yet.")
            else:
                for w in athlete.workouts:
                    print(w.workout_summary())
                    print()

        # Option 5: View all meet results
        elif choice == "5":
            if not athlete.meet_results:
                print("No meet results logged yet.")
            else:
                for m in athlete.meet_results:
                    print(m.meet_results_summary())
                    print()

        # Option 6: View current goal
        elif choice == "6":
            if athlete.goal is None:
                print("No goal set yet.")
            else:
                print(athlete.goal.goal_summary())

        # Option 7: Exit
        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number from 1 to 7.")


if __name__ == "__main__":
    menu()
