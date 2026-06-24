import os
from fl_read_data import fl_read_data
from fl_solver import fl_solver
from fl_compile_results import fl_compile_results

arquivo_instancias = r"C:\Users\progo\Containers_Multicompartimentados\Free_Loading\DATA_1_m05b2d1\DATA_1_n20m05b2d1.dat"

pasta_saida = "resultados DATA_1_n20m05b2d1"
os.makedirs(pasta_saida, exist_ok=True)

instancias = fl_read_data(arquivo_instancias)

for idx, inst in enumerate(instancias):
    print(f"\n Resolvendo instância {idx+1}...")
    nome = f"instancia_{idx+1}"
    arquivo_saida = os.path.join(pasta_saida, f"{nome}.txt")
    fl_solver(inst["L"], inst["W"], inst["H"], inst["boxes"], arquivo_saida)

print("\n Todas as instâncias resolvidas.")
fl_compile_results(pasta_saida)
