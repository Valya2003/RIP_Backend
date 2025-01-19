from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Resistor(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(default="images/default.png")
    description = models.TextField(verbose_name="Описание", blank=True)

    resistance = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Резистор"
        verbose_name_plural = "Резисторы"
        db_table = "resistors"


class Calculation(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Преподаватель", null=True, related_name='moderator')

    amperage = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "Вычисление №" + str(self.pk)

    def get_resistors(self):
        return [
            setattr(item.resistor, "value", item.value) or item.resistor
            for item in ResistorCalculation.objects.filter(calculation=self)
        ]

    class Meta:
        verbose_name = "Вычисление"
        verbose_name_plural = "Вычисления"
        ordering = ('-date_formation', )
        db_table = "calculations"


class ResistorCalculation(models.Model):
    resistor = models.ForeignKey(Resistor, models.DO_NOTHING, blank=True, null=True)
    calculation = models.ForeignKey(Calculation, models.DO_NOTHING, blank=True, null=True)
    value = models.IntegerField(verbose_name="Поле м-м", blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "resistor_calculation"
        unique_together = ('resistor', 'calculation')
