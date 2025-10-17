import json
import requests
from django.conf import settings

class ExternalLogisticsAPI:
    """
    Simulación de API externa de logística con interfaz diferente a la nuestra
    """
    def __init__(self):
        self.base_url = "https://api.externallogistics.com/v1"
        self.api_key = "fake-api-key-12345"

    def ship(self, order_id: int, priority: bool) -> str:
        """Método de la API externa con interfaz diferente"""
        # Simulación de llamada a API real
        payload = {
            "external_order_id": order_id,
            "express_delivery": priority,
            "carrier": "DHL" if priority else "STANDARD"
        }
        
        # En un caso real, haríamos:
        # response = requests.post(f"{self.base_url}/shipments", json=payload, headers={"Authorization": self.api_key})
        # return response.json().get("tracking_number")
        
        # Simulación
        if priority:
            return f"DHL_EXPRESS_{order_id}_TRACK"
        else:
            return f"STD_ECONOMY_{order_id}_TRACK"

    def get_shipment_status(self, tracking_number: str) -> dict:
        """Obtiene estado de envío desde API externa"""
        # Simulación
        statuses = ["RECEIVED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"]
        return {
            "tracking_number": tracking_number,
            "status": statuses[hash(tracking_number) % len(statuses)],
            "estimated_delivery": "2024-12-25"
        }

class ProviderAdapter:
    """
    Adaptador que convierte nuestra interfaz a la de la API externa
    """
    def __init__(self, provider: ExternalLogisticsAPI):
        self.provider = provider

    def create_shipment(self, order_id: int, speed: str) -> dict:
        """Nuestra interfaz uniforme para crear envíos"""
        # Adaptar nuestros parámetros a los de la API externa
        priority = True if speed == 'rapida' else False
        
        try:
            tracking_number = self.provider.ship(order_id, priority)
            
            return {
                'success': True,
                'tracking_number': tracking_number,
                'carrier': 'DHL Express' if priority else 'Transporte Económico',
                'estimated_days': 2 if priority else 7,
                'message': f'✅ Envío creado exitosamente. Número de seguimiento: {tracking_number}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'❌ Error al crear envío: {str(e)}'
            }

    def get_shipment_status(self, tracking_number: str) -> dict:
        """Obtiene el estado de un envío"""
        try:
            status = self.provider.get_shipment_status(tracking_number)
            return {
                'success': True,
                'status': status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Fábrica para crear el adapter
class LogisticsAdapterFactory:
    @staticmethod
    def create_adapter(provider_type: str = 'default'):
        if provider_type == 'default':
            external_api = ExternalLogisticsAPI()
            return ProviderAdapter(external_api)
        else:
            raise ValueError(f"Tipo de proveedor no soportado: {provider_type}")