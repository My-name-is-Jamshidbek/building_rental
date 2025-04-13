# core/templatetags/calc_tags.py
from django import template
from django.utils import timezone

from core.models import ProductHistory, ProductMoldHistory

register = template.Library()

@register.filter
def calculate_total(history):
    """
    Calculate the total cost for a history record.
    Assumes that:
       - If history has a product, its per-day cost is history.product.price.
       - If history has a product mold, its per-day cost is history.product_mold.price.
       - Duration is computed as (end_time - start_time) in days.
    Returns 0 if no end_time is available.
    """
    if not history.end_time:
        return 0
    # Calculate duration in days as float
    duration = (history.end_time - history.start_time).total_seconds() / 86400.0

    # Select the cost: check if the history has 'product' attribute; else, use product_mold.
    try:
        cost = history.product.price
    except AttributeError:
        try:
            cost = history.product_mold.price
        except AttributeError:
            cost = 0

    total = duration * cost
    return total


@register.filter
def rented_product(product):
    """
    Calculates the sum of active (uncompleted) ProductHistory 'count' for the given product.
    """
    active_histories = ProductHistory.objects.filter(product=product, end_time__isnull=True)
    return sum(history.count for history in active_histories)

@register.filter
def available_product(product):
    """
    Returns the product's total count minus the amount currently rented.
    """
    return product.count - rented_product(product)


@register.filter
def rented_mold(mold):
    """
    Returns the sum of the 'count' field in active (not completed) ProductMoldHistory records for the given product mold.
    """
    active_histories = ProductMoldHistory.objects.filter(product_mold=mold, end_time__isnull=True)
    return sum(history.count for history in active_histories)

@register.filter
def available_mold(mold):
    """
    Returns the available quantity for the product mold.
    """
    return mold.count - rented_mold(mold)