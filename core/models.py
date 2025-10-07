from django.db import models

class GrainType(models.TextChoices):
    ARABICA = 'AR', 'Arábica'
    ROBUSTA = 'RO', 'Robusta'
    BLEND = 'BL', 'Blend'

class ProcessStage(models.TextChoices):
    TOSTADO = 'TO', 'Tostado'
    MOLIDO = 'MO', 'Molido'
    ENVASADO = 'EN', 'Envasado'
    COMPLETADO = 'CO', 'Completado'

class DeliverySpeed(models.TextChoices):
    RAPIDA = 'RA', 'Rápida'
    ECONOMICA = 'EC', 'Económica'