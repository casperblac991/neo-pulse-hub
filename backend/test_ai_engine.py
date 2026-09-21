#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اختبارات وحدات خفيفة لا تحتاج إلى مفاتيح API أو اتصالاً بالإنترنت."""

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))
import ai_engine


class AIEngineTests(unittest.TestCase):
    def setUp(self):
        self.products = [
            {"id": "p1", "name": {"ar": "ساعة ذكية"}, "price": 80, "rating": 4.5, "reviews": 100},
            {"id": "p2", "name_ar": "سماعات", "price": "120", "rating": "4.8", "reviews": "200"},
            {"id": "p3", "name": "مقبس ذكي", "price": 40, "rating": 4.0, "reviews": 10},
        ]

    def test_local_customer_fallback_does_not_use_fake_old_threshold(self):
        with patch.object(ai_engine, "GEMINI_API_KEY", ""), patch.object(ai_engine, "GROQ_API_KEY", ""), patch.object(ai_engine, "OPENAI_API_KEY", ""):
            answer = ai_engine.answer_customer("ما هي سياسة الشحن؟")
        self.assertIn("الشحن", answer)
        self.assertNotIn("مجاني للطلبات فوق $50", answer)

    def test_recommendation_validates_ids_and_handles_string_values(self):
        with patch.object(ai_engine, "_call_json", return_value={"recommendations": ["bad", "p2"], "reason": "مناسب"}):
            ids, reason, mode = ai_engine.recommend_products_with_reason("سماعات", self.products)
        self.assertEqual(ids, ["p2"])
        self.assertEqual(reason, "مناسب")
        self.assertEqual(mode, "ai")

    def test_recommendation_fallback_is_safe(self):
        with patch.object(ai_engine, "_call_json", return_value=None):
            ids, _, mode = ai_engine.recommend_products_with_reason("منتج", self.products, budget=100)
        self.assertEqual(mode, "fallback")
        self.assertEqual(ids, ["p1", "p3"])

    def test_extract_budget_local_arabic_digits(self):
        self.assertEqual(ai_engine.extract_budget("ميزانيتي ١٥٠ دولار"), 150.0)

    def test_json_parser_handles_fenced_json(self):
        self.assertEqual(ai_engine._parse_json('```json\n{"ok": true}\n```'), {"ok": True})

    def test_purchase_intent_requires_exact_yes(self):
        with patch.object(ai_engine, "_call", return_value="yesterday"):
            self.assertFalse(ai_engine.is_purchase_intent("أريد الشراء"))
        with patch.object(ai_engine, "_call", return_value="yes"):
            self.assertTrue(ai_engine.is_purchase_intent("أريد الشراء"))

    def test_marketing_post_respects_limit(self):
        with patch.object(ai_engine, "_call", return_value="x" * 1000):
            result = ai_engine.generate_marketing_post(self.products[0], "x")
        self.assertLessEqual(len(result), 240)

    def test_product_data_can_use_dict_or_string(self):
        with patch.object(ai_engine, "_call", return_value="وصف"):
            result = ai_engine.generate_product_description({"name": "منتج نصي", "features": "ميزة"})
        self.assertEqual(result, "وصف")

    def test_search_does_not_invent_product_when_model_fails(self):
        with patch.object(ai_engine, "_call_json", return_value=None):
            result = ai_engine.search_product_by_description("منتج غير معروف")
        self.assertFalse(result["found"])
        self.assertNotIn("estimated_price_usd", result)


if __name__ == "__main__":
    unittest.main()
