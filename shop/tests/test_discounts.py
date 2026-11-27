from django.test import SimpleTestCase
from shop.discounts import DISCOUNT_TIERS, apply_discount, get_discount_percent


class GetDiscountPercentTestCase(SimpleTestCase):
    def test_no_discount_for_new_customer(self):
        self.assertEqual(get_discount_percent(0), 0)

    def test_just_below_first_threshold(self):
        self.assertEqual(get_discount_percent(9999), 0)

    def test_thresholds_are_inclusive(self):
        for threshold, percent in DISCOUNT_TIERS:
            self.assertEqual(get_discount_percent(threshold), percent)

    def test_just_below_each_threshold(self):
        previous = 0
        for threshold, percent in DISCOUNT_TIERS:
            self.assertEqual(get_discount_percent(threshold - 1), previous)
            previous = percent

    def test_maximum_discount(self):
        self.assertEqual(get_discount_percent(10 ** 9), 15)

    def test_tiers_are_sorted_and_increasing(self):
        thresholds = [t for t, _ in DISCOUNT_TIERS]
        percents = [p for _, p in DISCOUNT_TIERS]
        self.assertEqual(thresholds, sorted(thresholds))
        self.assertEqual(percents, sorted(percents))


class ApplyDiscountTestCase(SimpleTestCase):
    def test_zero_percent(self):
        self.assertEqual(apply_discount(1000, 0), 1000)

    def test_regular_discount(self):
        self.assertEqual(apply_discount(10000, 3), 9700)
        self.assertEqual(apply_discount(45000, 5), 42750)

    def test_fraction_is_dropped(self):
        self.assertEqual(apply_discount(999, 3), 969)

    def test_full_discount(self):
        self.assertEqual(apply_discount(1000, 100), 0)

    def test_incorrect_percent(self):
        with self.assertRaises(ValueError):
            apply_discount(1000, -1)
        with self.assertRaises(ValueError):
            apply_discount(1000, 101)
