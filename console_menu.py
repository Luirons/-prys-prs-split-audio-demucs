import questionary

opciones = [
    {"name": "Opción 1", "value": 1},
    {"name": "Opción 2", "value": 2},
    {"name": "Opción 3", "value": 3},
]

respuesta = questionary.select("Selecciona una opción:", opciones).ask()

print(f"Seleccionaste la opción {respuesta}")

