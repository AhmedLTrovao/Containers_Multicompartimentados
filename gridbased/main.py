
from read_data import read_data
from solver import resolver_instancia
import os

def main():
    os.makedirs("DATA_1_n30m05b2d1", exist_ok=True)
    instancias = read_data("DATA_1_n30m05b2d1.txt")
    for idx, inst in enumerate(instancias):
        print(f"Resolvendo instância {idx+1}...")
        arquivo_saida = os.path.join("DATA_1_n30m05b2d1", f"solucao_{idx+1}.txt")
        resolver_instancia(inst["L"], inst["W"], inst["H"], inst["boxes"], arquivo_saida)
        print(f"Instância {idx+1} concluída.\n")

if __name__ == "__main__":
    main()