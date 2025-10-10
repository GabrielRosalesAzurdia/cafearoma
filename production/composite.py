from abc import ABC, abstractmethod
from typing import List

class ProcessComponent(ABC):
    @abstractmethod
    def execute(self) -> str:
        pass

    @abstractmethod
    def get_duration(self) -> int:
        pass

class BasicProcess(ProcessComponent):
    def __init__(self, name: str, duration: int = 1):
        self.name = name
        self._duration = duration

    def execute(self) -> str:
        return f"✅ {self.name} - LISTO para ejecutar"

    def get_duration(self) -> int:
        return self._duration

    def __str__(self):
        return self.name

class ProcessComposite(ProcessComponent):
    def __init__(self, name: str):
        self.name = name
        self._children: List[ProcessComponent] = []
        self._current_child_index = 0

    def add(self, component: ProcessComponent) -> None:
        self._children.append(component)

    def remove(self, component: ProcessComponent) -> None:
        self._children.remove(component)

    def execute_current(self) -> str:
        """Ejecuta solo la etapa actual"""
        if not self._children:
            return "⚠️ No hay procesos para ejecutar"

        if self._current_child_index < len(self._children):
            current_child = self._children[self._current_child_index]
            result = current_child.execute()
            return f"🎯 Etapa {self._current_child_index + 1}/{len(self._children)}: {result}"
        else:
            return "✅ Todas las etapas completadas"

    def advance_to_next(self) -> bool:
        """Avanza a la siguiente etapa"""
        if self._current_child_index < len(self._children) - 1:
            self._current_child_index += 1
            return True
        return False

    def get_current_stage_name(self) -> str:
        """Obtiene el nombre de la etapa actual"""
        if self._current_child_index < len(self._children):
            return str(self._children[self._current_child_index])
        return "Completado"

    def get_progress(self) -> float:
        """Obtiene el progreso porcentual"""
        if not self._children:
            return 0
        return (self._current_child_index / len(self._children)) * 100

    def is_complete(self) -> bool:
        """Verifica si todas las etapas están completas"""
        return self._current_child_index >= len(self._children)

    def execute(self) -> str:
        """Ejecuta todas las etapas (para compatibilidad)"""
        if not self._children:
            return f"⚠️ Proceso compuesto '{self.name}' no tiene subprocesos"

        results = [f"🏭 Iniciando proceso compuesto: {self.name}"]
        total_duration = 0
        
        for i, child in enumerate(self._children, 1):
            results.append(f"  {i}. Ejecutando: {child}")
            results.append(f"     {child.execute()}")
            total_duration += child.get_duration()
        
        results.append(f"🎉 Proceso compuesto '{self.name}' completado en {total_duration} horas")
        return "\n".join(results)

    def get_duration(self) -> int:
        return sum(child.get_duration() for child in self._children)

    def __str__(self):
        return f"{self.name} ({len(self._children)} etapas)"