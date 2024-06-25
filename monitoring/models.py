# monitoring/models.py

from django.db import models

class PVSystem(models.Model):
    name = models.CharField(max_length=100)
    capacity = models.FloatField()
    inverter_type = models.CharField(max_length=100)
    number_of_panels = models.IntegerField()
    technology = models.CharField(max_length=100)
    year_of_installation = models.IntegerField()

class ElectricalData(models.Model):
    system = models.ForeignKey(PVSystem, on_delete=models.CASCADE)
    time = models.DateTimeField()
    adresse = models.IntegerField(null=True, blank=True)
    i1 = models.FloatField(null=True, blank=True)
    u_dc = models.FloatField(null=True, blank=True)
    p_dc = models.FloatField(null=True, blank=True)
    t1 = models.FloatField(null=True, blank=True)
    t2 = models.FloatField(null=True, blank=True)
    i_sum = models.FloatField(null=True, blank=True)

class MeteorologicalData(models.Model):
    time = models.DateTimeField()
    gti = models.FloatField(null=True, blank=True)
    ghi = models.FloatField(null=True, blank=True)
    dni = models.FloatField(null=True, blank=True)
    dhi = models.FloatField(null=True, blank=True)
    air_temp = models.FloatField(null=True, blank=True)
    rh = models.FloatField(null=True, blank=True)
    pressure = models.FloatField(null=True, blank=True)
    wind_speed = models.FloatField(null=True, blank=True)
    wind_dir = models.FloatField(null=True, blank=True)
    wind_gust = models.FloatField(null=True, blank=True)
    rain = models.FloatField(null=True, blank=True)
