import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


def add_resistors():
    Resistor.objects.create(
        name="Углеродный резистор",
        description="Углеродные резисторы являются одним из наиболее распространенных типов электроники. Они изготавливаются из твердого цилиндрического элемента резистора со встроенными проволочными выводами или металлическими торцевыми заглушками. Углеродные резисторы бывают разных физических размеров с пределами рассеиваемой мощности, обычно от 1 Вт до 1/8 Вт.",
        resistance=10,
        image="1.png"
    )

    Resistor.objects.create(
        name="Углеродный пленочный резистор",
        description="Углеродный пленочный резистор является электронным компонентом, который обеспечивает сопротивление электрическому току. Хотя существует много типов резисторов, изготовленных из множества различных материалов, углеродный пленочный резистор имеет тонкую пленку углерода, образованную вокруг цилиндра.",
        resistance=25,
        image="2.png"
    )

    Resistor.objects.create(
        name="Металло пленочный резистор",
        description="Металлопленочные резисторы имеют тонкий металлический слой в качестве резистивного элемента на непроводящем теле . Они являются одними из самых распространенных типов аксиальных резисторов.",
        resistance=15,
        image="3.png"
    )

    Resistor.objects.create(
        name="Металло оксидный резистор",
        description="Металлооксидные пленочные резисторы используют пленку, в которой оксиды металлов смешаны с резистивным элементом . Они используются в относительно промежуточных приложениях мощности около нескольких ватт и недороги.",
        resistance=30,
        image="4.png"
    )

    Resistor.objects.create(
        name="Проволочный резисто",
        description="Проволочные резисторы — это резисторы, в которых резистивным элементом является высокоомная проволока (изготавливается из высокоомных сплавов: константан, нихром, никелин).",
        resistance=15,
        image="5.png"
    )

    Resistor.objects.create(
        name="Разрывной резистор",
        description="Разрывной резистор, также известный как предохранительный резистор или антирезистор, — это специальный компонент, который используется в электрических и электронных устройствах для защиты цепей от перегрузок, коротких замыканий или других аномальных условий.",
        resistance=5,
        image="6.png"
    )

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_calculations():
    users = User.objects.filter(is_superuser=False)
    moderators = User.objects.filter(is_superuser=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    resistors = Resistor.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        add_calculation(status, resistors, users, moderators)

    add_calculation(1, resistors, users, moderators)

    print("Заявки добавлены")


def add_calculation(status, resistors, users, moderators):
    calculation = Calculation.objects.create()
    calculation.status = status

    if calculation.status in [3, 4]:
        calculation.date_complete = random_date()
        calculation.date_formation = calculation.date_complete - random_timedelta()
        calculation.date_created = calculation.date_formation - random_timedelta()
    else:
        calculation.date_formation = random_date()
        calculation.date_created = calculation.date_formation - random_timedelta()

    calculation.owner = random.choice(users)
    calculation.moderator = random.choice(moderators)

    calculation.amperage = random.randint(1, 10)

    for resistor in random.sample(list(resistors), 3):
        item = ResistorCalculation(
            calculation=calculation,
            resistor=resistor,
            value=random.randint(1, 10)
        )
        item.save()

    calculation.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_resistors()
        add_calculations()
