"""A test that PASSES but is bad. Used in Exercise 4.

It lives outside tests/ so pytest does not collect it by default.
Run it explicitly with:  pytest exercises/bad_test.py
"""
import time

from playwright.sync_api import Page


def test_checkout(page: Page):
    page.goto("https://www.saucedemo.com/")
    page.locator("#user-name").fill("standard_user")
    page.locator("#password").fill("secret_sauce")
    page.locator("xpath=//*[@id='root']/div/div[2]/div[1]/div/div/form/input").click()
    time.sleep(3)
    page.locator("div.inventory_list > div:nth-child(1) button").click()
    page.locator(".shopping_cart_link").click()
    time.sleep(2)
    page.locator("button.btn.btn_action.btn_medium.checkout_button").click()
    page.locator("#first-name").fill("Test")
    page.locator("#last-name").fill("User")
    page.locator("#postal-code").fill("12345")
    page.locator("input[type=submit]").click()
    page.locator("#finish").click()
    time.sleep(2)
    assert page.locator(".complete-header").is_visible()
