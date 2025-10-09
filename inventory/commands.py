from abc import ABC, abstractmethod
from django.core.exceptions import ObjectDoesNotExist
import json
from .repositories import DjangoInventoryRepo

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

    @abstractmethod
    def undo(self):
        pass

class AgregarStockCommand(Command):
    def __init__(self, repo, sku: str, kg: float):
        self.repo = repo
        self.sku = sku
        self.kg = kg
        self._previous_stock = None
        self._executed = False

    def execute(self):
        item = self.repo.get_item(self.sku)
        self._previous_stock = item.stock_kg
        item.stock_kg += self.kg
        self.repo.save(item)
        self._executed = True
        return f"Agregados {self.kg}kg a {self.sku}. Stock actual: {item.stock_kg}kg"

    def undo(self):
        if self._executed and self._previous_stock is not None:
            item = self.repo.get_item(self.sku)
            item.stock_kg = self._previous_stock
            self.repo.save(item)
            return f"Stock de {self.sku} revertido a {self._previous_stock}kg (undo)"
        return "No se puede deshacer - comando no ejecutado"

    def to_dict(self):
        return {
            'type': 'AgregarStockCommand',
            'sku': self.sku,
            'kg': self.kg,
            'previous_stock': self._previous_stock,
            'executed': self._executed
        }

class ConsumirStockCommand(Command):
    def __init__(self, repo, sku: str, kg: float):
        self.repo = repo
        self.sku = sku
        self.kg = kg
        self._previous_stock = None
        self._executed = False

    def execute(self):
        item = self.repo.get_item(self.sku)
        self._previous_stock = item.stock_kg
        if item.stock_kg >= self.kg:
            item.stock_kg -= self.kg
            self.repo.save(item)
            self._executed = True
            return f"Consumidos {self.kg}kg de {self.sku}. Stock actual: {item.stock_kg}kg"
        else:
            raise ValueError(f"Stock insuficiente en {self.sku}")

    def undo(self):
        if self._executed and self._previous_stock is not None:
            item = self.repo.get_item(self.sku)
            item.stock_kg = self._previous_stock
            self.repo.save(item)
            return f"Stock de {self.sku} revertido a {self._previous_stock}kg (undo)"
        return "No se puede deshacer - comando no ejecutado"

    def to_dict(self):
        return {
            'type': 'ConsumirStockCommand',
            'sku': self.sku,
            'kg': self.kg,
            'previous_stock': self._previous_stock,
            'executed': self._executed
        }

class AgregarProductoCommand(Command):
    def __init__(self, repo, item_data: dict):
        self.repo = repo
        self.item_data = item_data
        self._added_item = None
        self._executed = False

    def execute(self):
        from .models import InventoryItem
        self._added_item = InventoryItem(**self.item_data)
        self.repo.save(self._added_item)
        self._executed = True
        return f"Producto {self._added_item.sku} agregado exitosamente"

    def undo(self):
        if self._executed and self._added_item:
            self._added_item.delete()
            return f"Producto {self._added_item.sku} eliminado (undo)"
        return "No se puede deshacer - comando no ejecutado"
    
    def to_dict(self):
        return {
            'type': 'AgregarProductoCommand',
            'item_data': self.item_data,
            'executed': self._executed
        }

class CommandInvoker:
    def __init__(self, request):
        self.request = request
        # Inicializar historial desde la sesión
        if 'command_history' not in self.request.session:
            self.request.session['command_history'] = []
        self._history = self.request.session['command_history']

    def execute_command(self, command: Command):
        result = command.execute()
        # Guardar comando serializado en la sesión
        command_dict = command.to_dict()
        self._history.append(command_dict)
        self.request.session['command_history'] = self._history
        self.request.session.modified = True
        return result

    def undo_last(self):
        if self._history:
            # Recuperar el último comando
            last_command_dict = self._history.pop()
            self.request.session['command_history'] = self._history
            self.request.session.modified = True
            
            # Recrear el comando a partir del dict
            repo = DjangoInventoryRepo()
            command_type = last_command_dict['type']
            
            if command_type == 'AgregarStockCommand':
                command = AgregarStockCommand(repo, last_command_dict['sku'], last_command_dict['kg'])
                command._executed = last_command_dict['executed']
                command._previous_stock = last_command_dict['previous_stock']
                
            elif command_type == 'ConsumirStockCommand':
                command = ConsumirStockCommand(repo, last_command_dict['sku'], last_command_dict['kg'])
                command._executed = last_command_dict['executed']
                command._previous_stock = last_command_dict['previous_stock']
                
            elif command_type == 'AgregarProductoCommand':
                command = AgregarProductoCommand(repo, last_command_dict['item_data'])
                command._executed = last_command_dict['executed']
                if command._executed:
                    # Recuperar el item agregado
                    try:
                        command._added_item = repo.get_item(last_command_dict['item_data']['sku'])
                    except ObjectDoesNotExist:
                        command._added_item = None
            
            else:
                return "Tipo de comando no reconocido"
            
            # Ejecutar undo
            return command.undo()
        return "No hay comandos para deshacer"

    def get_history(self):
        return self._history

    def clear_history(self):
        self._history = []
        self.request.session['command_history'] = []
        self.request.session.modified = True