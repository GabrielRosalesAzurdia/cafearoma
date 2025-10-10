from abc import ABC, abstractmethod
from django.core.mail import send_mail
from django.conf import settings

class Subject(ABC):
    @abstractmethod
    def attach(self, observer):
        pass

    @abstractmethod
    def detach(self, observer):
        pass

    @abstractmethod
    def notify(self):
        pass

class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass

class ResponsableDeCompras(Observer):
    def update(self, subject):
        low_stock_items = subject.check_low_stock()
        if low_stock_items:
            print(f"🔔 NOTIFICACIÓN: Stock bajo detectado en {len(low_stock_items)} items")
            for item in low_stock_items:
                print(f"   - {item.sku} ({item.name}): {item.stock_kg}kg (mínimo: {item.min_stock_kg}kg)")
            # Aquí podrías enviar un email
            # self._send_notification_email(low_stock_items)
    
    def _send_notification_email(self, items):
        subject = "Alerta: Stock Bajo en Café Aroma"
        message = "Los siguientes items necesitan reposición:\n\n"
        for item in items:
            message += f"- {item.name} (SKU: {item.sku}): {item.stock_kg}kg restantes\n"
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['compras@cafearoma.com'],
            fail_silently=True,
        )