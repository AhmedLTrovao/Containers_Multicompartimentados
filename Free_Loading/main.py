from read_data import read_data
from solver import resolver_instancia_free_loading

def main():
    instancias = read_data("instancias.txt")
    for idx, inst in enumerate(instancias):
        print(f"Resolvendo instância {idx+1}...")
        arquivo_saida = f"solucao_{idx+1}.txt"
        resolver_instancia_free_loading(inst["L"], inst["W"], inst["H"], inst["boxes"], arquivo_saida)
        print(f"Instância {idx+1} concluída.\n")

if __name__ == "__main__":
    main()
