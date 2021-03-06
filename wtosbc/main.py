import requests
from lxml.cssselect import CSSSelector
from lxml.etree import fromstring
import lxml.html
from lxml import etree
import json
from wtosbc import config, wtos, spreadsheet, bc, state


def go() -> None:
    bc_chef = config.bc_chef
    bc_number = state.load_bc_number()
    session = requests.Session()

    print("Session started")

    bc.login(session)

    posts = wtos.load_posts(bc_number)
    post_items_per_user = wtos.get_post_items_per_user(bc_number, posts)
    print("Orders loaded")

    if len(post_items_per_user) > 0:
        bc.clear_cart(session)
        print("Cart cleared")

        order_items_per_user = bc.get_order_items_per_user(session, post_items_per_user)
        print("Order items data fetched")

        bc.add_order_items(session, order_items_per_user)
        print("Order items added to the cart")

        bc.add_pa(session, order_items_per_user)
        print("Price alerts added")

        bc_spreadsheet = spreadsheet.load(bc_number)
        print("Spreadsheet loaded")

        spreadsheet.update(bc_spreadsheet, bc_number, order_items_per_user)
        print("Spreadsheet updated")
    else:
        print("No orders")

    if wtos.has_next_post(posts, bc_number, bc_chef):
        start_next_order(bc_number + 1)

    print("Finished")


def start_next_order(next_bc_number: int) -> None:
    state.set_bc_number(next_bc_number)
    spreadsheet.create_sheet(next_bc_number)


if __name__ == "__main__":
    go()
