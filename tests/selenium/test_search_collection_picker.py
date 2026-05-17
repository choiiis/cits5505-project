from tests.selenium.base import By, EC, SeleniumTestCase


class SearchCollectionPickerSeleniumTests(SeleniumTestCase):
    def test_logged_in_user_can_open_collection_picker_from_search_card(self):
        self.login_as_seed_customer()
        self.open_path("/search?q=pizza")

        bookmark_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-bookmark]"))
        )
        bookmark_button.click()

        modal = self.wait.until(
            EC.visibility_of_element_located((By.ID, "collectionPickerModal"))
        )
        options = self.driver.find_elements(By.CSS_SELECTOR, "[data-picker-collection]")

        self.assertEqual(modal.get_attribute("aria-hidden"), "false")
        self.assertGreaterEqual(len(options), 1)

    def test_collection_picker_option_can_be_selected(self):
        self.login_as_seed_customer()
        self.open_path("/search?q=cafe")

        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-bookmark]"))
        ).click()
        option = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-picker-collection]"))
        )
        option.click()

        self.assertIn("is-selected", option.get_attribute("class"))


if __name__ == "__main__":
    import unittest

    unittest.main()
