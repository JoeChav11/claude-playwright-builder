import pytest

# Fixtures live in fixtures/ and are registered here so every test can use them.
pytest_plugins = ["fixtures.auth", "fixtures.pages"]


@pytest.fixture(scope="session", autouse=True)
def use_data_test_attribute(playwright):
    # saucedemo marks elements with data-test="..." instead of the default data-testid.
    playwright.selectors.set_test_id_attribute("data-test")
