import pytest
from django.test import TestCase
from core.factories import ProductFactory, ComboFactoryCreator
from core.inventory_manager import InventoryManager
from inventory.repositories import DjangoInventoryRepo

class TestSingletonPattern(TestCase):
    def test_singleton_instance(self):
        """Prueba que InventoryManager sea un Singleton"""
        repo1 = DjangoInventoryRepo()
        manager1 = InventoryManager(repo1)
        
        repo2 = DjangoInventoryRepo()
        manager2 = InventoryManager(repo2)
        
        # Deberían ser la misma instancia
        self.assertIs(manager1, manager2)
        self.assertEqual(id(manager1), id(manager2))

class TestFactoryMethodPattern(TestCase):
    def setUp(self):
        self.factory = ProductFactory()

    def test_create_arabica_coffee(self):
        """Prueba la creación de café Arábica usando Factory Method"""
        coffee = self.factory.create('arabica', 1.0, origin='Colombia')
        self.assertEqual(coffee.label(), "Café Arábica Premium (Colombia) - 1.0kg")
        self.assertEqual(coffee.get_price_per_kg(), 45.00)

    def test_create_robusta_coffee(self):
        """Prueba la creación de café Robusta usando Factory Method"""
        coffee = self.factory.create('robusta', 0.5, origin='Vietnam')
        self.assertEqual(coffee.label(), "Café Robusta Intenso (Vietnam) - 0.5kg")
        self.assertEqual(coffee.get_price_per_kg(), 35.00)

    def test_create_blend_coffee(self):
        """Prueba la creación de café Blend usando Factory Method"""
        coffee = self.factory.create('blend', 2.0, ratio='70:30', blend_name='Especial')
        self.assertEqual(coffee.label(), "Blend Especial (70:30) - 2.0kg")
        self.assertEqual(coffee.get_price_per_kg(), 40.00)

class TestAbstractFactoryPattern(TestCase):
    def test_beginner_combo_factory(self):
        """Prueba la creación de combo principiante usando Abstract Factory"""
        factory = ComboFactoryCreator.create_factory('beginner')
        combo = factory.create_combo('arabica', 0.25)
        
        self.assertEqual(combo.combo_name, "Combo Principiante")
        self.assertEqual(combo.mug.design, "Básica Cerámica")
        self.assertEqual(combo.filter.type, "Papel")
        self.assertAlmostEqual(combo.get_total_price(), 21.825, places=2)

    def test_premium_combo_factory(self):
        """Prueba la creación de combo premium usando Abstract Factory"""
        factory = ComboFactoryCreator.create_factory('premium')
        combo = factory.create_combo('robusta', 0.5)
        
        self.assertEqual(combo.combo_name, "Combo Premium")
        self.assertEqual(combo.mug.material, "Porcelana")
        self.assertEqual(combo.filter.type, "Algodón Orgánico")
        self.assertEqual(combo.discount, 0.15)