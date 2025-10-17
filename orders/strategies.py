from abc import ABC, abstractmethod
from .models import Order

class DistribucionStrategy(ABC):
    @abstractmethod
    def plan_route(self, order: Order) -> str:
        pass

class DistribucionRapida(DistribucionStrategy):
    def plan_route(self, order: Order) -> str:
        # Lógica para distribución rápida (prioridad)
        routes_rapidas = [
            f"🚀 Ruta EXPRESS #{order.id}: Centro Logístico → Cliente directo (24h)",
            f"🚀 Ruta PRIORIDAD #{order.id}: Centro → Aeropuerto → Cliente (18h)",
            f"🚀 Ruta URGENTE #{order.id}: Moto mensajería directa (12h)"
        ]
        import random
        return random.choice(routes_rapidas)

class DistribucionEconomica(DistribucionStrategy):
    def plan_route(self, order: Order) -> str:
        # Lógica para distribución económica (optimización de costos)
        routes_economicas = [
            f"💰 Ruta ECONÓMICA #{order.id}: Centro → Bodega regional → Cliente (3-5 días)",
            f"💰 Ruta OPTIMIZADA #{order.id}: Agrupación con otros pedidos → Ruta terrestre (4 días)",
            f"💰 Ruta ESTÁNDAR #{order.id}: Transporte terrestre programado (5 días)"
        ]
        import random
        return random.choice(routes_economicas)

class ContextoDeDistribucion:
    def __init__(self, strategy: DistribucionStrategy = None):
        self._strategy = strategy

    def set_strategy(self, strategy: DistribucionStrategy):
        self._strategy = strategy

    def execute_strategy(self, order: Order) -> str:
        if self._strategy is None:
            raise ValueError("Estrategia no definida")
        return self._strategy.plan_route(order)
    
    def get_available_strategies(self):
        return {
            'rapida': DistribucionRapida(),
            'economica': DistribucionEconomica()
        }