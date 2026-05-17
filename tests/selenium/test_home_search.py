from urllib.parse import parse_qs, urlparse

from tests.selenium.base import By, EC, SeleniumTestCase


class HomeSearchSeleniumTests(SeleniumTestCase):
    def test_home_search_navigates_to_search_results(self):
        self.open_path("/")

        self.driver.find_element(By.ID, "keywordSearch").send_keys("pizza")
        self.driver.find_element(By.ID, "locationSearch").send_keys("Perth")
        self.driver.find_element(By.CSS_SELECTOR, ".hero-search button[type='submit']").click()

        self.wait.until(EC.url_contains("/search"))
        parsed_url = urlparse(self.driver.current_url)
        query = parse_qs(parsed_url.query)

        self.assertEqual(parsed_url.path, "/search")
        self.assertEqual(query.get("q"), ["pizza"])
        self.assertEqual(query.get("location"), ["Perth"])

    def test_search_page_shows_results_area(self):
        self.open_path("/search?q=cafe")

        heading = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".search-results-main"))
        )

        self.assertTrue(heading.is_displayed())


if __name__ == "__main__":
    import unittest

    unittest.main()
