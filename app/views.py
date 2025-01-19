from django.shortcuts import render

resistors = [
    {
        "id": 1,
        "name": "Углеродный резистор",
        "description": "Углеродные резисторы являются одним из наиболее распространенных типов электроники. Они изготавливаются из твердого цилиндрического элемента резистора со встроенными проволочными выводами или металлическими торцевыми заглушками.",
        "resistance": 10,
        "image": "http://localhost:9000/images/1.png"
    },
    {
        "id": 2,
        "name": "Углеродный пленочный резистор",
        "description": "Углеродный пленочный резистор является электронным компонентом, который обеспечивает сопротивление электрическому току. Хотя существует много типов резисторов, изготовленных из множества различных материалов, углеродный пленочный резистор имеет тонкую пленку углерода, образованную вокруг цилиндра.",
        "resistance": 25,
        "image": "http://localhost:9000/images/2.png"
    },
    {
        "id": 3,
        "name": "Металло пленочный резистор",
        "description": "Металлопленочные резисторы имеют тонкий металлический слой в качестве резистивного элемента на непроводящем теле . Они являются одними из самых распространенных типов аксиальных резисторов.",
        "resistance": 15,
        "image": "http://localhost:9000/images/3.png"
    },
    {
        "id": 4,
        "name": "Металло оксидный резистор",
        "description": "Металлооксидные пленочные резисторы используют пленку, в которой оксиды металлов смешаны с резистивным элементом . Они используются в относительно промежуточных приложениях мощности около нескольких ватт и недороги.",
        "resistance": 30,
        "image": "http://localhost:9000/images/4.png"
    },
    {
        "id": 5,
        "name": "Проволочный резистор",
        "description": "Проволочные резисторы — это резисторы, в которых резистивным элементом является высокоомная проволока (изготавливается из высокоомных сплавов: константан, нихром, никелин).",
        "resistance": 15,
        "image": "http://localhost:9000/images/5.png"
    },
    {
        "id": 6,
        "name": "Разрывной резистор",
        "description": "Разрывной резистор, также известный как предохранительный резистор или антирезистор, — это специальный компонент, который используется в электрических и электронных устройствах для защиты цепей от перегрузок, коротких замыканий или других аномальных условий.",
        "resistance": 5,
        "image": "http://localhost:9000/images/6.png"
    }
]

draft_calculation = {
    "id": 123,
    "status": "Черновик",
    "date_created": "12 сентября 2024г",
    "amperage": 8,
    "resistors": [
        {
            "id": 1,
            "value": 8
        },
        {
            "id": 2,
            "value": 4
        },
        {
            "id": 3,
            "value": 10
        }
    ]
}


def getResistorById(resistor_id):
    for resistor in resistors:
        if resistor["id"] == resistor_id:
            return resistor


def getResistors():
    return resistors


def searchResistors(resistor_name):
    res = []

    for resistor in resistors:
        if resistor_name.lower() in resistor["name"].lower():
            res.append(resistor)

    return res


def getDraftCalculation():
    return draft_calculation


def getCalculationById(calculation_id):
    return draft_calculation


def index(request):
    resistor_name = request.GET.get("resistor_name", "")
    resistors = searchResistors(resistor_name) if resistor_name else getResistors()
    draft_calculation = getDraftCalculation()

    context = {
        "resistors": resistors,
        "resistor_name": resistor_name,
        "resistors_count": len(draft_calculation["resistors"]),
        "draft_calculation": draft_calculation
    }

    return render(request, "home_page.html", context)


def resistor(request, resistor_id):
    context = {
        "id": resistor_id,
        "resistor": getResistorById(resistor_id),
    }

    return render(request, "resistor_page.html", context)


def calculation(request, calculation_id):
    calculation = getCalculationById(calculation_id)
    resistors = [
        {**getResistorById(resistor["id"]), "value": resistor["value"]}
        for resistor in calculation["resistors"]
    ]

    context = {
        "calculation": calculation,
        "resistors": resistors
    }

    return render(request, "calculation_page.html", context)
