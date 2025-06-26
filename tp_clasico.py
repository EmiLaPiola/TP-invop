import sys
import cplex

TOLERANCE = 10e-6

class InstanciaRecorridoMixto:
    def __init__(self):
        self.cant_clientes = 0
        self.costo_repartidor = 0
        self.d_max = 0
        self.refrigerados = []
        self.exclusivos = []
        self.distancias = []        
        self.costos = []        

    def leer_datos(self,filename):
        with open(filename) as f:
            self.cantidad_clientes = int(f.readline())
            self.costo_repartidor = int(f.readline())
            self.d_max = int(f.readline())
            self.distancias = [[1000000 for _ in range(self.cantidad_clientes)] for _ in range(self.cantidad_clientes)]
            self.costos = [[1000000 for _ in range(self.cantidad_clientes)] for _ in range(self.cantidad_clientes)]

            cantidad_refrigerados = int(f.readline())
            for _ in range(cantidad_refrigerados):
                self.refrigerados.append(int(f.readline()))

            cantidad_exclusivos = int(f.readline())
            for _ in range(cantidad_exclusivos):
                self.exclusivos.append(int(f.readline()))

            for linea in f.readlines():
                row = list(map(int, linea.split(' ')))
                self.distancias[row[0]-1][row[1]-1] = row[2]
                self.distancias[row[1]-1][row[0]-1] = row[2]
                self.costos[row[0]-1][row[1]-1] = row[3]
                self.costos[row[1]-1][row[0]-1] = row[3]

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
        nombres.append(f"u_{i}")
        obj.append(0)
        lb.append(1 if i != 0 else 0)
        ub.append(n)
        tipos.append(prob.variables.type.integer)

    prob.variables.add(obj=obj, lb=lb, ub=ub, types=tipos, names=nombres)

def agregar_restricciones(prob, instancia):
    n = instancia.cantidad_clientes

    for j in range(n):
        indices = [f"x_{i}_{j}" for i in range(n) if i != j]
        coefs = [1] * len(indices)
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=coefs)],
            senses=["E"],
            rhs=[1],
            names=[f"entrada_{j}"]
        )

    for i in range(n):
        indices = [f"x_{i}_{j}" for j in range(n) if i != j]
        coefs = [1] * len(indices)
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=indices, val=coefs)],
            senses=["E"],
            rhs=[1],
            names=[f"salida_{i}"]
        )

    prob.linear_constraints.add(
        lin_expr=[cplex.SparsePair(ind=["u_0"], val=[1])],
        senses=["E"],
        rhs=[1],
        names=["u_inicio"]
    )

    for i in range(1, n):
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[f"u_{i}"], val=[1])],
            senses=["G"],
            rhs=[1],
            names=[f"u_lb_{i}"]
        )
        prob.linear_constraints.add(
            lin_expr=[cplex.SparsePair(ind=[f"u_{i}"], val=[1])],
            senses=["L"],
            rhs=[n],
            names=[f"u_ub_{i}"]
        )

    for i in range(1, n):
        for j in range(1, n):
            if i != j:
                prob.linear_constraints.add(
                    lin_expr=[cplex.SparsePair(
                        ind=[f"u_{i}", f"u_{j}", f"x_{i}_{j}"],
                        val=[1, -1, n]
                    )],
                    senses=["L"],
                    rhs=[n - 1],
                    names=[f"subtour_{i}_{j}"]
                )

def armar_lp(prob, instancia):
    agregar_variables(prob, instancia)
    agregar_restricciones(prob, instancia)
    prob.objective.set_sense(prob.objective.sense.minimize)
    prob.write('recorridoMixto.lp')

def resolver_lp(prob):
    prob.solve()

def mostrar_solucion(prob, instancia):
    status = prob.solution.get_status_string(status_code=prob.solution.get_status())
    valor_obj = prob.solution.get_objective_value()
    print(f"Funcion objetivo: {valor_obj:.2f} ({status})")

    x_vals = prob.solution.get_values()
    nombres = prob.variables.get_names()

    arcos = {}
    for name, val in zip(nombres, x_vals):
        if val > TOLERANCE and name.startswith("x_"):
            partes = name.split("_")
            if len(partes) == 3:
                i = int(partes[1])
                j = int(partes[2])
                arcos[i] = j

    recorrido = []
    actual = 0
    visitados = set()
    while actual not in visitados and actual in arcos:
        recorrido.append(actual)
        visitados.add(actual)
        actual = arcos[actual]
    recorrido.append(actual)

    print("Recorrido del camión:")
    print(" → ".join(map(str, recorrido)))

def main():
    instancia = cargar_instancia()
    prob = cplex.Cplex()
    armar_lp(prob, instancia)
    resolver_lp(prob)
    mostrar_solucion(prob, instancia)

if __name__ == '__main__':
    main()
