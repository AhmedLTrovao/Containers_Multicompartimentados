# solver para resultados testes
import os
from solver_mhlopp_transversal import resolver_multi_compartimento
    
def main():
    # no teste 1, roda a mesma instancia com 1 unico compartimento. vemos que dá o mesmo resultado
    teste = 2
    
    
    if teste==1:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        arquivo_saida = os.path.join(dir_path, "teste1.txt")
        
        compartimentos = [(12, 8, 8)]
        boxes = [(6,3,2,2), (6,4,3,5), (8,3,2,3), (4,3,2,2), (4,4,3,3)]
        
        resolver_multi_compartimento(compartimentos, boxes, arquivo_saida)
    elif teste==2:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        arquivo_saida = os.path.join(dir_path, "teste2.txt")
        
        compartimentos = [(12, 8, 8), (12, 8, 8), (12, 8, 8), (12, 8, 8)]
        boxes = [(6,3,2,8), (6,4,3,20), (8,3,2,12), (4,3,2,8), (4,4,3,12)]
        
        resolver_multi_compartimento(compartimentos, boxes, arquivo_saida)
    
    
if __name__=="__main__":
    main()