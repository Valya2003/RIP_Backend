import segno
import base64
from io import BytesIO
from django.utils.timezone import localtime

from app.models import Calculation, ResistorCalculation, Resistor

def generate_calc_qr(calculation):
    """
    Генерирует QR-код с информацией о вычислении и резисторах.

    :param calculation: Экземпляр модели Calculation
    :return: строка Base64, представляющая изображение QR-кода
    """
    # Сбор информации о вычислении
    calculation_info = f"""
    Вычисление №{calculation.id}
    Напряжение: {calculation.voltage} В

    Студент: {calculation.owner.username if calculation.owner else 'Не указан'}
    """

    # Добавляем информацию о каждом резисторе в вычислении
    resistor_calculations = ResistorCalculation.objects.filter(calculation=calculation).select_related('resistor')
    for resistor_calculation in resistor_calculations:
        resistor = resistor_calculation.resistor
        calculation_info += f"""
        Резистор: {resistor.name} (Сопротивление: {resistor.resistance} Ом)
        Количество: {resistor_calculation.count}
        """

    # Добавляем информацию о силе тока и дате завершения
    calculation_info += f"""
    Сила тока: {calculation.current} А
    Дата завершения: {localtime(calculation.date_complete).strftime('%Y-%m-%d %H:%M:%S') if calculation.date_complete else 'Не завершена'}
    """

    # Генерация QR-кода
    qr = segno.make(calculation_info.strip())

    # Сохранение QR-кода в строку Base64
    buffer = BytesIO()
    qr.save(buffer, kind='png', scale=5)
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()

    return qr_base64
