from django.test import TestCase
from orders.models import Order
from orders.strategies import ContextoDeDistribucion, DistribucionRapida, DistribucionEconomica

class StrategyPatternTest(TestCase):
    def setUp(self):
        self.order_rapida = Order.objects.create(
            customer="Cliente Express",
            delivery_speed='RA'
        )
        
        self.order_economica = Order.objects.create(
            customer="Cliente Standard",
            delivery_speed='EC'
        )

    def test_distribucion_rapida_strategy(self):
        """Prueba la estrategia de distribución rápida"""
        strategy = DistribucionRapida()
        result = strategy.plan_route(self.order_rapida)
        
        self.assertIn('🚀', result)
        self.assertIn(str(self.order_rapida.id), result)

    def test_distribucion_economica_strategy(self):
        """Prueba la estrategia de distribución económica"""
        strategy = DistribucionEconomica()
        result = strategy.plan_route(self.order_economica)
        
        self.assertIn('💰', result)
        self.assertIn(str(self.order_economica.id), result)