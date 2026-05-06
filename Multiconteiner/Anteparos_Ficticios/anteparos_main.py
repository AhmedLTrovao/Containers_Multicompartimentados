import os
from anteparos_read_data import read_data
from anteparos_solver import resolver_instancia
from anteparos_compile_results import compilar_resultados

# Caminho do arquivo de instâncias
#arquivo_instancias = r"C:\Users\progo\Containers_Multicompartimentados\Multiconteiner\Anteparos_Ficticios\DATA_1_m10b2d1\DATA_1_n30m10b2d1.dat"
arquivo_instancias = r"C:\Users\progo\Containers_Multicompartimentados\Multiconteiner\Anteparos_Ficticios\DATA_0\Data_1_com_paredes.txt"

# Pasta onde todos os resultados serão salvos
pasta_saida = "resultados DATA_0"

# Cria a pasta se não existir
os.makedirs(pasta_saida, exist_ok=True)

# Lê todas as instâncias
instancias = read_data(arquivo_instancias)

# Resolve cada instância e salva os resultados na pasta
for idx, inst in enumerate(instancias):
    print(f"\n Resolvendo instância {idx+1}...")
    nome_base = f"instancia_{idx+1}"
    arquivo_saida = os.path.join(pasta_saida, f"{nome_base}.txt")
    # Agora passamos inst["walls"] também
    resolver_instancia(inst["L"], inst["W"], inst["H"], inst["boxes"], inst["walls"], arquivo_saida)

print("\n Todas as instâncias foram resolvidas. Resultados em:", pasta_saida)

compilar_resultados(pasta_saida)

