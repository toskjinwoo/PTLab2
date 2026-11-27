"""Накопительная скидка: чем больше покупатель потратил, тем она выше."""

# (минимальная общая сумма покупок в рублях, скидка в процентах),
# строго по возрастанию суммы
DISCOUNT_TIERS = (
    (10000, 3),
    (30000, 5),
    (60000, 10),
    (100000, 15),
)


def get_discount_percent(total_spent: int) -> int:
    """Скидка (%) для покупателя, уже потратившего total_spent."""
    for threshold, percent in reversed(DISCOUNT_TIERS):
        if total_spent >= threshold:
            return percent
    return 0


def apply_discount(price: int, percent: int) -> int:
    """Цена со скидкой; дробная часть отбрасывается (в пользу клиента)."""
    if not 0 <= percent <= 100:
        raise ValueError('Скидка должна быть в пределах 0-100%')
    return price * (100 - percent) // 100
