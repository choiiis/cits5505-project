from tests.selenium.base import By, EC, Keys, SeleniumTestCase


class BookmarkWorkflowSeleniumTests(SeleniumTestCase):
    def test_bookmark_page_collection_section_loads(self):
        self.open_path("/bookmarks")

        collections_title = self.wait.until(
            EC.presence_of_element_located((By.ID, "collectionsTitle"))
        )
        public_collections_title = self.driver.find_element(By.ID, "publicCollectionsTitle")

        self.assertTrue(collections_title.is_displayed())
        self.assertTrue(public_collections_title.is_displayed())

    def test_create_collection_modal_opens(self):
        self.open_path("/bookmarks")

        self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-open-create-collection]"))
        ).click()
        modal = self.wait.until(
            EC.visibility_of_element_located((By.ID, "createCollectionModal"))
        )

        self.assertEqual(modal.get_attribute("aria-hidden"), "false")

    def test_bookmark_search_filters_collection_cards(self):
        self.open_path("/bookmarks")

        search_input = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-bookmark-search]"))
        )
        collection_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-collection-card]")

        if not collection_cards:
            self.skipTest("No collection cards are available in the seeded database.")

        first_card_text = collection_cards[0].text
        first_search_word = first_card_text.split()[0]
        search_input.send_keys(first_search_word)

        visible_cards = [
            card
            for card in self.driver.find_elements(By.CSS_SELECTOR, "[data-collection-card]")
            if card.is_displayed()
        ]

        self.assertGreaterEqual(len(visible_cards), 1)
        self.assertIn(first_search_word.lower(), visible_cards[0].text.lower())

        search_input.send_keys(Keys.COMMAND, "a")
        search_input.send_keys("no-matching-collection-name")
        visible_after_no_match = [
            card
            for card in self.driver.find_elements(By.CSS_SELECTOR, "[data-collection-card]")
            if card.is_displayed()
        ]

        self.assertEqual(visible_after_no_match, [])


if __name__ == "__main__":
    import unittest

    unittest.main()
