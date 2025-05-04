import frappe
from frappe.tests import IntegrationTestCase

from fossunited.api.dashboard import get_session_user_profile
from fossunited.doctype_ids import USER_PROFILE


class TestDashboardAPI(IntegrationTestCase):
    def setUp(self):
        self.test_user = "test2@example.com"

        self.user_profile_name = frappe.db.get_value(
            USER_PROFILE, {"user": self.test_user}, "name"
        )

        self.original_session_user = frappe.session.user

        frappe.session.user = self.test_user

        self.setup_test_profile()

    def tearDown(self):
        frappe.session.user = self.original_session_user

        self.reset_test_profile()

    def setup_test_profile(self):
        test_data = {
            "full_name": "Test User",
            "username": "testuser",
            "current_city": "Test City",
            "website": "https://example.com",
            "about": "This is a test profile",
            "bio": "Test user bio",
            "github": "testgithub",
            "linkedin": "testlinkedin",
        }

        for field, value in test_data.items():
            frappe.db.set_value(USER_PROFILE, self.user_profile_name, field, value)

        self.original_data = frappe.db.get_value(
            USER_PROFILE, self.user_profile_name, list(test_data.keys()), as_dict=1
        )

    def reset_test_profile(self):
        if hasattr(self, "original_data"):
            for field, value in self.original_data.items():
                frappe.db.set_value(USER_PROFILE, self.user_profile_name, field, value or "")

    def test_get_session_user_profile(self):
        """Test that get_session_user_profile returns the correct user profile data"""

        user_profile = get_session_user_profile()

        self.assertIsInstance(user_profile, dict)

        self.assertEqual(user_profile.get("user"), self.test_user)

        self.assertEqual(user_profile.get("full_name"), "Test User")
        self.assertEqual(user_profile.get("username"), "testuser")
        self.assertEqual(user_profile.get("current_city"), "Test City")
        self.assertEqual(user_profile.get("website"), "https://example.com")
        self.assertEqual(user_profile.get("github"), "testgithub")

        expected_fields = [
            "full_name",
            "username",
            "profile_photo",
            "cover_image",
            "route",
            "current_city",
            "gender",
            "website",
            "about",
            "bio",
            "user",
            "name",
            "is_private",
            "github",
            "gitlab",
            "linkedin",
            "mastodon",
            "x",
            "instagram",
            "devto",
            "youtube",
        ]

        for field in expected_fields:
            self.assertIn(field, user_profile)

    def test_get_session_user_profile_not_logged_in(self):
        """Test that get_session_user_profile handles not logged in users appropriately"""

        frappe.session.user = "Guest"

        try:
            result = get_session_user_profile()

            if result is not None:
                self.fail("Expected None or exception for guest user, got: {}".format(result))
        except frappe.PermissionError:
            pass
        except Exception as e:
            self.assertTrue(True, f"Got exception: {str(e)}")
        finally:
            frappe.session.user = self.test_user
