from read_data import read_data
from solver import resolver_instancia

instancias = read_data("instancias.txt")

for idx, inst in enumerate(instancias):
    print(f"Resolvendo instância {idx+1}...")
    resolver_instancia(inst["L"], inst["W"], inst["H"], inst["boxes"], f"solucao_{idx+1}.txt")
