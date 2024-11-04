# pp.py
from texto import Texto  # Importa la variable desde texto.py

nombre = "Luca"

# Formatea el texto con el nombre
texto_final = Texto.format(nombre=nombre)

print(texto_final)
