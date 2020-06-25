import robin_stocks

from requests.adapters import HTTPAdapter
from robin_stocks import urls, helper
from src.common import logging, env

ROBINHOOD_PROTOCOLS = list(robin_stocks.globals.SESSION.adapters.keys())
logging.info("Fixing robinhood session protocols")
for protocl in ROBINHOOD_PROTOCOLS:
    robin_stocks.globals.SESSION.mount(
        protocl,
        HTTPAdapter(pool_maxsize=env.RVTM_ROBINHOOD_MAX_POOL_SIZE, pool_connections=env.RVTM_ROBINHOOD_MAX_POOL_SIZE,),
    )
    logging.info(f"Fixed session pool for robinhood @ {protocl}")


@helper.login_required
def cancel_crypto_order(orderID):
    """Cancels a specific crypto order.

    :param orderID: The ID associated with the order. Can be found using get_all_orders(info=None)
        or get_all_orders(info=None).
    :type orderID: str
    :returns: Returns the order information for the order that was cancelled.

    """
    url = f"{urls.order_crypto()}{orderID}/cancel/"
    data = helper.request_post(url)

    if data:
        print("Order " + orderID + " cancelled")

    return data


@helper.login_required
def get_crypto_order_info(orderID):
    """Returns the information for a single crypto order.

    :param orderID: The ID associated with the order. Can be found using get_all_orders(info=None)
        or get_all_orders(info=None).
    :type orderID: str
    :returns: Returns a list of dictionaries of key/value pairs for the order.

    """
    url = f"{urls.order_crypto()}{orderID}/"
    data = helper.request_get(url)
    return data


# update the robin_stocks
robin_stocks.get_crypto_order_info = get_crypto_order_info
robin_stocks.cancel_crypto_order = cancel_crypto_order
