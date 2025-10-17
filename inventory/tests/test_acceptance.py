from django.test import TestCase, Client
from django.contrib.auth.models import User
from inventory.models import InventoryItem
from core.models import GrainType

class InventoryAcceptanceTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='acceptanceuser',
            password='acceptancepass123'
        )
        self.client.force_login(self.user)

    def test_usuario_puede_crear_y_gestionar_inventario(self):
        """Prueba de aceptación: Usuario puede crear y gestionar items de inventario"""
        
        # 1. Usuario accede al dashboard de inventario
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gestión de Inventario')
        
        # 2. Usuario crea un nuevo producto
        response = self.client.post('/inventory/add-product/', {
            'sku': 'ACCEPT-001',
            'name': 'Café Aceptación',
            'type': GrainType.ARABICA,
            'stock_kg': 40.0,
            'min_stock_kg': 12.0
        })
        
        # Verificar redirección después de crear
        self.assertEqual(response.status_code, 302)
        
        # 3. Usuario verifica que el producto se creó
        response = self.client.get('/inventory/')
        self.assertContains(response, 'ACCEPT-001')
        self.assertContains(response, 'Café Aceptación')
        
        # 4. Verificar en la base de datos
        item = InventoryItem.objects.get(sku='ACCEPT-001')
        self.assertEqual(item.stock_kg, 40.0)