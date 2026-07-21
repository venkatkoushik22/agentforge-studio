import unittest

from src.agents.planner import plan_project


class PlannerTests(unittest.TestCase):
    def test_detects_requested_stack(self) -> None:
        requirement = (
            "Build a React booking application using FastAPI "
            "and PostgreSQL with login and payment processing."
        )

        plan = plan_project(requirement)

        self.assertEqual(plan.frontend, "React")
        self.assertEqual(plan.backend, "FastAPI")
        self.assertEqual(plan.database, "PostgreSQL")
        self.assertEqual(plan.application_type, "Booking application")
        self.assertIn("User authentication", plan.features)
        self.assertIn("Payment processing", plan.features)

    def test_uses_default_stack(self) -> None:
        plan = plan_project("Create a simple inventory application.")

        self.assertEqual(plan.frontend, "React")
        self.assertEqual(plan.backend, "FastAPI")
        self.assertEqual(plan.database, "SQLite")

    def test_rejects_empty_requirement(self) -> None:
        with self.assertRaises(ValueError):
            plan_project("   ")


if __name__ == "__main__":
    unittest.main()