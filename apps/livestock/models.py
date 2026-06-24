from django.db import models
from django.conf import settings
from apps.farms.models import Farm

class Animal(models.Model):
    SPECIES = [('cattle','Cattle'),('goat','Goat'),('poultry','Poultry'),('pig','Pig'),('sheep','Sheep')]

    farm       = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='animals')
    owner      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    species    = models.CharField(max_length=50, choices=SPECIES)
    breed      = models.CharField(max_length=100, blank=True)
    tag_number = models.CharField(max_length=50, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.species} - {self.tag_number or self.id}'

class HealthRecord(models.Model):
    animal      = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='health_records')
    symptom     = models.CharField(max_length=200)
    diagnosis   = models.TextField(blank=True)
    treatment   = models.TextField(blank=True)
    vet_visited = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.animal} - {self.symptom}'
