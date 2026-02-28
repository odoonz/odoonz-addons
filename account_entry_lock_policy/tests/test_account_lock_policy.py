from datetime import date

from odoo import fields
from odoo.tests import TransactionCase, freeze_time, tagged


@freeze_time("2024-03-10")
@tagged("post_install", "-at_install")
class TestLockPolicy(TransactionCase):
    """Tests for company-level account.lock.policy behaviour."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

    def _create_policy(self, **vals):
        base = {
            "lock_date_field": "fiscalyear_lock_date",
            "days": 7,
            "day_type": "day",
            "months": 1,
            "company_id": self.company.id,
        }
        base.update(vals)
        return self.env["account.lock.policy"].create(base)

    def test_calculate_lock_date_days_over_limit(self):
        """When over the day limit, use last day of month N+1 months ago."""
        policy = self._create_policy(days=7, day_type="day", months=1)
        lock_date = policy._calculate_lock_date()
        # With today frozen at 2024-03-10, this should be 2024-01-31.
        self.assertEqual(lock_date, date(2024, 1, 31))

    def test_calculate_lock_date_days_not_over_limit(self):
        """When not over the day limit, go back one additional month."""
        policy = self._create_policy(days=15, day_type="day", months=1)
        lock_date = policy._calculate_lock_date()
        # With today frozen at 2024-03-10, this should be 2023-12-31.
        self.assertEqual(lock_date, date(2023, 12, 31))

    def test_over_days_limit_weekdays(self):
        """Weekday-based limit counts working days only."""
        policy = self._create_policy(days=6, day_type="weekday", months=0)
        today = fields.Date.context_today(policy)
        # For the frozen date (2024-03-10, a Sunday), there are 5
        # weekdays since the previous month-end; we should *not* be
        # over the limit when days == 5.
        self.assertFalse(policy._over_days_limit(today))

        policy.days = 3
        self.assertTrue(policy._over_days_limit(today))

    def test_update_lock_dates_sets_company_field(self):
        """_update_lock_dates sets the target lock date when allowed."""
        policy = self._create_policy(lock_date_field="fiscalyear_lock_date")
        self.company.fiscalyear_lock_date = False

        expected = policy._calculate_lock_date()
        policy._update_lock_dates()

        self.assertEqual(self.company.fiscalyear_lock_date, expected)

    def test_update_lock_dates_never_regresses_lock_date(self):
        """Existing lock dates are not moved backwards in time."""
        policy = self._create_policy(lock_date_field="fiscalyear_lock_date")
        newer = date(2024, 2, 28)
        self.company.fiscalyear_lock_date = newer

        # Force policy to compute an older date than `newer`.
        policy.months = 2
        computed = policy._calculate_lock_date()
        self.assertLess(computed, newer)

        policy._update_lock_dates()
        # Lock date must stay at the newer value.
        self.assertEqual(self.company.fiscalyear_lock_date, newer)
