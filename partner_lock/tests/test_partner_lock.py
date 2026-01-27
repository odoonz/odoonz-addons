from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestResPartner(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_model = cls.env["res.partner"]
        cls.user_model = cls.env["res.users"]
        cls.group_unlock = cls.env.ref("partner_lock.group_res_partner_unlock")

        # Create test partners
        cls.partner = cls.partner_model.create(
            {
                "name": "Test Partner",
                "is_locked": False,
            }
        )

        cls.locked_partner = cls.partner_model.create(
            {
                "name": "Locked Partner",
                "is_locked": True,
            }
        )

        # Create test user
        cls.test_user = cls.user_model.create(
            {
                "name": "test user",
                "login": "test_user",
                "email": "test_user@example.com",
            }
        )

        cls.unlock_user = cls.user_model.create(
            {
                "name": "unlock user",
                "login": "unlock_user",
                "email": "unlock_user@example.com",
            }
        )
        cls.unlock_user.group_ids = [(4, cls.group_unlock.id)]

    def test_write_unlocked_partner(self):
        """Test writing to an unlocked partner"""
        self.partner.with_user(self.test_user).write({"name": "Updated Test Partner"})
        self.assertEqual(self.partner.name, "Updated Test Partner")

    def test_write_locked_partner_no_group(self):
        """Test writing to a locked partner without proper group permissions"""
        with self.assertRaises(ValidationError):
            self.locked_partner.with_user(self.test_user).write(
                {"name": "Updated Locked Partner"}
            )

    def test_write_locked_partner_with_group(self):
        """Test writing to a locked partner with proper group permissions"""
        self.locked_partner.with_user(self.unlock_user).write(
            {"name": "Updated Locked Partner"}
        )
        self.assertEqual(self.locked_partner.name, "Updated Locked Partner")

    def test_unlocked_fields(self):
        """Test updating unlocked fields for locked partner"""
        self.locked_partner.with_user(self.test_user).write({"customer_rank": 5})
        self.assertEqual(self.locked_partner.customer_rank, 5)
