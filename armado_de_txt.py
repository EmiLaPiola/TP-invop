
import numpy as np
import matplotlib.pyplot as plt
import random

np.random.seed(42)
random.seed(42)


# Primero generamos una grilla 50  de coordenadas en R2 para representar las casas . Tomamos el (500,500) como el deposit ( justo el medio) 
# y generamos numeros randoms de una grilla de 1000 x 1000
# tomamos como distancias entre las casas la distancia euclideana 
# El costo de ir de una casa a la otra será la distancia que hay entre ellas 


# Luego construimos la matriz COSTOS que va a tener en la coordenada ij el costo que hay para ir de la casa i a la casa j 
# que va a ser la distancia entre las casas 

# Parámetros

num_puntos = 50
limite_grilla = 1000
deposito = (500, 500)
costo_repartidor = 50
d_max = 250 


# Generamos coordenadas aleatorias

x = np.random.randint(0, limite_grilla, size=num_puntos)
y = np.random.randint(0, limite_grilla, size=num_puntos)

# Lista de clientes con sus coordenadas, el nodo 0 es el depósito

clientes = [(0, deposito)] + [(i + 1, (x[i], y[i])) for i in range(num_puntos)]


# Mostrar clientes

for id_cliente, coord in clientes:
    print(f"Cliente {id_cliente}: {coord}")

# Matriz de costos (distancia euclideana)

n = len(clientes)
costos = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        xi, yi = clientes[i][1]
        xj, yj = clientes[j][1]
        distancia = np.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
        costos[i][j] = round(distancia, 2)

# Graficar

plt.figure(figsize=(8, 8))
plt.scatter(x, y, color='blue', s=30, label='Clientes')
plt.scatter(*deposito, color='red', s=60, label='Depósito')

plt.xlim(0, limite_grilla)
plt.ylim(0, limite_grilla)
plt.gca().set_aspect('equal', adjustable='box')
plt.title('Ubicación de los clientes')
plt.xlabel('Coordenada X')
plt.ylabel('Coordenada Y')
plt.grid(True)
plt.legend()
plt.show()


# Entonces como los parametros del modelo son : 
# 1) las distancias entre las casas que las tenemos con la matriz de costos 
# 2) dmax a eleccion 
# 3) cij el costo para ir de la casa i a la casa j que lo sacamos de la matriz de costos 
# 4) costo_repartidor a eleccion tambien 
# 5) refrigerados a eleccion 
# 6) clientes_oblig_camion tambien a eleccion 
# 7) cantidad total de clientes ( 300 por ahora)


# Elegimos 20 clientes únicos al azar para refrigerados y exclusivos

refrigerados = random.sample(range(1, num_puntos + 1), 5)
exclusivos = random.sample(range(1, num_puntos + 1),5 )

print("Refrigerados:", refrigerados)
print("Exclusivos:", exclusivos)


# Guardar datos en archivo de texto

with open("test_100.txt", "w") as f:
    f.write(f"{num_puntos}\n")
    f.write(f"{costo_repartidor}\n")
    f.write(f"{d_max}\n")
    
    # Coordenadas de los nodos
    for _, (cx, cy) in clientes:
        f.write(f"{cx} {cy}\n")
    
    # Matriz de costos
    for fila in costos:
        f.write(" ".join(map(str, fila)) + "\n")
    
    # Refrigerados
    f.write(" ".join(map(str, refrigerados)) + "\n")
    
    # Exclusivos
    f.write(" ".join(map(str, exclusivos)) + "\n")
    
    
    # Lineas de salida para el txt : 
    
    
