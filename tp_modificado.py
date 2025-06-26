import sys
#importamos el modulo cplex
import cplex

M = 50  # Constante grande para MTZ

TOLERANCE =10e-6 

class InstanciaRecorridoMixto:
    def __init__(self):
        self.cantidad_clientes = 0
        self.costo_repartidor = 0
        self.d_max = 0
        self.refrigerados = []
        self.exclusivos = []
        self.distancias = []        
        self.costos = []        

    def leer_datos(self,filename):
        f = open(filename)
        self.cantidad_clientes = int(f.readline())
        self.costo_repartidor = int(f.readline())
        self.d_max = int(f.readline())
        self.distancias = [[1000000 for _ in range(self.cantidad_clientes)] for _ in range(self.cantidad_clientes)]
        self.costos = [[1000000 for _ in range(self.cantidad_clientes)] for _ in range(self.cantidad_clientes)]
        cantidad_refrigerados = int(f.readline())
        for i in range(cantidad_refrigerados):
            self.refrigerados.append(int(f.readline()))
        cantidad_exclusivos = int(f.readline())
        for i in range(cantidad_exclusivos):
            self.exclusivos.append(int(f.readline()))
        lineas = f.readlines()
        for linea in lineas:
            row = list(map(int,linea.split(' ')))
            self.distancias[row[0]-1][row[1]-1] = row[2]
            self.distancias[row[1]-1][row[0]-1] = row[2]
            self.costos[row[0]-1][row[1]-1] = row[3]
            self.costos[row[1]-1][row[0]-1] = row[3]
        f.close()

def cargar_instancia():
    nombre_archivo = sys.argv[1].strip()
    instancia = InstanciaRecorridoMixto()
    instancia.leer_datos(nombre_archivo)
    return instancia

def agregar_variables(prob, instancia):
    n = instancia.cantidad_clientes
    nombres = []
    obj = []
    lb = []
    ub = []
    tipos = []
    for i in range(n):
        for j in range(n):
            if i != j:
                nombres.append(f"x_{i}_{j}")
                obj.append(instancia.costos[i][j])
                lb.append(0)
                ub.append(1)
                tipos.append(prob.variables.type.binary)
    for i in range(n):
        nombres.append(f"x_{i}")
        obj.append(0)
        lb.append(0)
        ub.append(1)
        tipos.append(prob.variables.type.binary)
    for i in range(n):
        for j in range(n):
            if i != j:
                nombres.append(f"delta_{i}_{j}")
                obj.append(0)
                lb.append(0)
                ub.append(1)
                tipos.append(prob.variables.type.binary)
    for i in range(n):
        nombres.append(f"delta_{i}")
        obj.append(instancia.costo_repartidor)
        lb.append(0)
        ub.append(1)
        tipos.append(prob.variables.type.binary)
    for i in range(n):
        nombres.append(f"u_{i}")
        obj.append(0)
        lb.append(0)
        ub.append(n)
        tipos.append(prob.variables.type.integer)
    for i in range(n):
        nombres.append(f"z_{i}")
        obj.append(0)
        lb.append(0)
        ub.append(1)
        tipos.append(prob.variables.type.binary)
    prob.variables.add(obj=obj, lb=lb, ub=ub, types=tipos, names=nombres)

# AGREGUEMOS LAS RESTRICICONES 

def agregar_restricciones_modificado(prob, instancia):
    n = instancia.cantidad_clientes

 # --- Restricción 1: Cada cliente debe ser atendido una única vez ---
 
    for i in range(n):
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[f"x_{i}", f"delta_{i}"], val=[1, 1])],
            senses=["E"],
            rhs=[1],
            names=[f"atencion_unica_{i}"]
        )

# --- Restricción 2: Entrada y salida única del camión para cada casa visitada ---


    for i in range(n):
        salidas = [f"x_{i}_{j}" for j in range(n) if i != j]
        entradas = [f"x_{j}_{i}" for j in range(n) if i != j]

        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=salidas + [f"x_{i}"], val=[1]*len(salidas) + [-1])],
            senses=["E"],
            rhs=[0],
            names=[f"salida_{i}"]
        )

        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=entradas + [f"x_{i}"], val=[1]*len(entradas) + [-1])],
            senses=["E"],
            rhs=[0],
            names=[f"entrada_{i}"]
        )
        
 # --- Restricción 3: Relación entre entregas individuales y si un cliente fue atendido por un repartidor ---
 
    for j in range(n):
        indices = [f"delta_{i}_{j}" for i in range(n) if i != j]
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices + [f"delta_{j}"], val=[1]*len(indices) + [-1])],
            senses=["E"],
            rhs=[0],
            names=[f"relacion_delta_{j}"]
        )
        
 # --- Restricción 4: Límite de distancia para repartidores ---
 
    for i in range(n):
        for j in range(n):
            if i != j:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(ind=[f"delta_{i}_{j}", f"x_{i}"], val=[instancia.distancias[i][j], -instancia.d_max])],
                    senses=["L"],
                    rhs=[0],
                    names=[f"dist_max_rep_{i}_{j}"]
                )
        

        
 # --- Restricción 5: Máximo un producto refrigerado entregado por repartidor desde cada casa ---
 
    for i in range(n):
        indices = [f"delta_{i}_{j}" for j in instancia.refrigerados if j != i]
        if indices:
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=indices, val=[1]*len(indices))],
                senses=["L"],
                rhs=[1],
                names=[f"refrigerados_{i}"]
            )
            
  # --- Restricción 6: Eliminación de subtours (MTZ modificada con nodo 1 como depósito) ---
    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=["u_1"], val=[1])],
        senses=["E"],
        rhs=[1],
        names=["u_inicio"]
    )

    for i in range(n):
        if i != 1:
            prob.linear_constraints.add(
                lin_expr=[cplex.SparsePair(ind=[f"u_{i}", f"x_{i}"], val=[1, -n])],
                senses=["L"],
                rhs=[0],
                names=[f"u_ub_{i}"]
            )

    for i in range(n):
        for j in range(n):
            if i != j and i != 1 and j != 1:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(
                        ind=[f"u_{i}", f"u_{j}", f"x_{i}_{j}", f"x_{i}"],
                        val=[1, -1, n, M]
                    )],
                    senses=["L"],
                    rhs=[n - 1 + M],
                    names=[f"subtour_{i}_{j}"]
                )

        





def armar_lp(prob, instancia):
    agregar_variables(prob, instancia)
    agregar_restricciones_modificado(prob, instancia)
    prob.objective.set_sense(prob.objective.sense.minimize)
    prob.write('recorridoMixto.lp')

def resolver_lp(prob):
    prob.solve()

def mostrar_solucion(prob,instancia):
    status = prob.solution.get_status_string(status_code = prob.solution.get_status())
    valor_obj = prob.solution.get_objective_value()
    print('Funcion objetivo: ',valor_obj,'(' + str(status) + ')')
    x = prob.solution.get_values()
    print("\nVariables activas:")
    for nombre, valor in zip(prob.variables.get_names(), x):
        if valor > TOLERANCE:
            print(f"{nombre} = {valor}")

def main():
    instancia = cargar_instancia()
    prob = cplex.Cplex()
    armar_lp(prob,instancia)
    resolver_lp(prob)
    mostrar_solucion(prob,instancia)

if __name__ == '__main__':
    main()
