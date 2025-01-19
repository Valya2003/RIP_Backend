from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class CalculationStatus(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Статус истории"
        verbose_name_plural = "Статусы историй"
        db_table = "calculation_status"


class Resistor(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    resistance = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
        db_table = "resistors"
        ordering = ('pk', )


class Calculation(models.Model):
    status = models.ForeignKey(CalculationStatus, on_delete=models.DO_NOTHING, blank=True, null=True)
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Преподаватель", related_name='moderator', blank=True,  null=True)

    voltage = models.IntegerField(blank=True, null=True)
    current = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "История №" + str(self.pk)

    class Meta:
        verbose_name = "История"
        verbose_name_plural = "Истории"
        db_table = "calculations"
        ordering = ('-date_formation', )


class ResistorCalculation(models.Model):
    resistor = models.ForeignKey(Resistor, on_delete=models.DO_NOTHING, blank=True, null=True)
    calculation = models.ForeignKey(Calculation, on_delete=models.DO_NOTHING, blank=True, null=True)
    count = models.IntegerField(default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "resistor_calculation"
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(fields=['resistor', 'calculation'], name="resistor_calculation_constraint")
        ]
