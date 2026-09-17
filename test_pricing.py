"""
Bu testler, projenin en kritik kuralinin ('taban fiyatin altina asla inilmez')
her sartta gecerli oldugunu dogrular.

Calistirmak icin: pytest tests/test_pricing.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.pricing import calculate_base_price, evaluate_price


def test_base_price_formula():
    assert calculate_base_price(cost=100, min_profit_rate=10) == 110.0
    assert calculate_base_price(cost=250, min_profit_rate=20) == 300.0


def test_no_recommendation_without_market_data():
    result = evaluate_price(cost=100, min_profit_rate=10, current_price=115, market_price=None)
    assert result.recommended_price is None
    assert result.action_needed is False


def test_recommendation_triggers_when_market_rises():
    result = evaluate_price(cost=100, min_profit_rate=10, current_price=115, market_price=130)
    assert result.action_needed is True
    assert result.recommended_price is not None
    assert result.recommended_price >= result.base_price
    assert result.recommended_price < 130  # rakibin tam fiyatini degil, altini onerir


def test_never_recommends_below_base_price_even_if_market_crashes():
    # Piyasa fiyati taban fiyatin cok altina dustu.
    result = evaluate_price(cost=100, min_profit_rate=10, current_price=115, market_price=50)
    assert result.recommended_price is None
    assert result.action_needed is False
    # Guvenlik: base_price her zaman dogru hesaplanmis olmali
    assert result.base_price == 110.0


def test_never_recommends_below_base_price_when_market_is_slightly_above_base():
    # Piyasa taban fiyatin hemen ustunde ama olusan oneri taban fiyatin altina
    # dusecek olsa bile sistem taban fiyati garanti eder.
    result = evaluate_price(cost=100, min_profit_rate=10, current_price=105, market_price=111)
    if result.recommended_price is not None:
        assert result.recommended_price >= result.base_price


def test_no_recommendation_when_seller_already_competitive():
    result = evaluate_price(cost=100, min_profit_rate=10, current_price=128, market_price=130)
    assert result.action_needed is False
