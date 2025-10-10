from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Tuple

# Productos de Café (Factory Method - YA IMPLEMENTADO)
class CoffeeProduct(ABC):
    @abstractmethod
    def label(self) -> str:
        pass

    @abstractmethod
    def get_price_per_kg(self) -> float:
        pass

@dataclass
class ArabicaCoffee(CoffeeProduct):
    weight_kg: float
    origin: str = "Etiopía"
    
    def label(self) -> str:
        return f"Café Arábica Premium ({self.origin}) - {self.weight_kg}kg"
    
    def get_price_per_kg(self) -> float:
        return 45.00  # Precio por kg

@dataclass
class RobustaCoffee(CoffeeProduct):
    weight_kg: float
    origin: str = "Vietnam"
    
    def label(self) -> str:
        return f"Café Robusta Intenso ({self.origin}) - {self.weight_kg}kg"
    
    def get_price_per_kg(self) -> float:
        return 35.00  # Precio por kg

@dataclass
class BlendCoffee(CoffeeProduct):
    weight_kg: float
    ratio: str
    blend_name: str = "House Blend"
    
    def label(self) -> str:
        return f"Blend {self.blend_name} ({self.ratio}) - {self.weight_kg}kg"
    
    def get_price_per_kg(self) -> float:
        return 40.00  # Precio por kg

# Factory Method para productos de café
class ProductFactory:
    def create(self, kind: str, weight_kg: float, **kwargs) -> CoffeeProduct:
        if kind == 'arabica':
            origin = kwargs.get('origin', 'Etiopía')
            return ArabicaCoffee(weight_kg=weight_kg, origin=origin)
        elif kind == 'robusta':
            origin = kwargs.get('origin', 'Vietnam')
            return RobustaCoffee(weight_kg=weight_kg, origin=origin)
        elif kind == 'blend':
            ratio = kwargs.get('ratio', '50:50')
            blend_name = kwargs.get('blend_name', 'House Blend')
            return BlendCoffee(weight_kg=weight_kg, ratio=ratio, blend_name=blend_name)
        else:
            raise ValueError(f"Tipo de café desconocido: {kind}")

# Productos para Combos (Abstract Factory - A IMPLEMENTAR)
@dataclass
class Mug:
    design: str
    material: str
    capacity_ml: int
    price: float
    
    def __str__(self) -> str:
        return f"Taza {self.design} ({self.material}, {self.capacity_ml}ml)"

@dataclass
class Filter:
    size: str
    type: str
    quantity: int
    price: float
    
    def __str__(self) -> str:
        return f"Filtro {self.size} ({self.type}, {self.quantity} unidades)"

@dataclass
class Combo:
    coffee: CoffeeProduct
    mug: Mug
    filter: Filter
    combo_name: str
    discount: float = 0.10  # 10% de descuento en combos
    
    def get_total_price(self) -> float:
        coffee_price = self.coffee.get_price_per_kg() * self.coffee.weight_kg
        total = coffee_price + self.mug.price + self.filter.price
        return total * (1 - self.discount)
    
    def get_description(self) -> str:
        return (f"🎁 {self.combo_name}\n"
                f"☕ {self.coffee.label()}\n"
                f"🍵 {self.mug}\n"
                f"⏳ {self.filter}\n"
                f"💰 Precio total: ${self.get_total_price():.2f} (incluye {self.discount*100:.0f}% descuento)")

# Abstract Factory para combos
class ComboFactory(ABC):
    @abstractmethod
    def create_combo(self, coffee_type: str, coffee_weight: float) -> Combo:
        pass

    @abstractmethod
    def get_combo_type(self) -> str:
        pass

# Fábricas Concretas para diferentes tipos de combos
class BeginnerComboFactory(ComboFactory):
    def create_combo(self, coffee_type: str, coffee_weight: float) -> Combo:
        coffee_factory = ProductFactory()
        coffee = coffee_factory.create(coffee_type, coffee_weight)
        
        mug = Mug(
            design="Básica Cerámica",
            material="Cerámica",
            capacity_ml=300,
            price=8.00
        )
        
        filter = Filter(
            size="Nº2",
            type="Papel",
            quantity=40,
            price=5.00
        )
        
        return Combo(
            coffee=coffee,
            mug=mug,
            filter=filter,
            combo_name="Combo Principiante"
        )
    
    def get_combo_type(self) -> str:
        return "Principiante"

class PremiumComboFactory(ComboFactory):
    def create_combo(self, coffee_type: str, coffee_weight: float) -> Combo:
        coffee_factory = ProductFactory()
        coffee = coffee_factory.create(coffee_type, coffee_weight)
        
        mug = Mug(
            design="Premium Porcelana",
            material="Porcelana",
            capacity_ml=350,
            price=15.00
        )
        
        filter = Filter(
            size="Nº4",
            type="Algodón Orgánico",
            quantity=30,
            price=12.00
        )
        
        return Combo(
            coffee=coffee,
            mug=mug,
            filter=filter,
            combo_name="Combo Premium",
            discount=0.15  # 15% de descuento
        )
    
    def get_combo_type(self) -> str:
        return "Premium"

class ProfessionalComboFactory(ComboFactory):
    def create_combo(self, coffee_type: str, coffee_weight: float) -> Combo:
        coffee_factory = ProductFactory()
        coffee = coffee_factory.create(coffee_type, coffee_weight, origin="Especial")
        
        mug = Mug(
            design="Barista Professional",
            material="Porcelana de Gres",
            capacity_ml=400,
            price=25.00
        )
        
        filter = Filter(
            size="Nº6",
            type="Acero Inoxidable",
            quantity=1,
            price=20.00
        )
        
        return Combo(
            coffee=coffee,
            mug=mug,
            filter=filter,
            combo_name="Combo Profesional",
            discount=0.20  # 20% de descuento
        )
    
    def get_combo_type(self) -> str:
        return "Profesional"

# Fábrica para crear las fábricas de combos
class ComboFactoryCreator:
    @staticmethod
    def create_factory(combo_level: str) -> ComboFactory:
        if combo_level == 'beginner':
            return BeginnerComboFactory()
        elif combo_level == 'premium':
            return PremiumComboFactory()
        elif combo_level == 'professional':
            return ProfessionalComboFactory()
        else:
            raise ValueError(f"Nivel de combo desconocido: {combo_level}")
    
    @staticmethod
    def get_available_combo_types() -> list:
        return [
            {'value': 'beginner', 'name': '🎯 Combo Principiante', 'description': 'Perfecto para empezar'},
            {'value': 'premium', 'name': '⭐ Combo Premium', 'description': 'Experiencia mejorada'},
            {'value': 'professional', 'name': '🏆 Combo Profesional', 'description': 'Para expertos'}
        ]