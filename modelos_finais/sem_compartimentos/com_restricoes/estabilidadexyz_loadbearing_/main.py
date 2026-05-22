
from IIPP.restricoes_praticas.solver import resolver_instancia
import os

def main():
    L, W, H = (12, 8, 8)
    boxes = [(6, 3, 2, 2), (6, 4, 3, 5), (8, 3, 2, 3), (4, 3, 2, 2), (4,4,3,3)]
    Sigma = [0, 3, 5, 0, 3]
    Peso = [l*w*h for (l, w, h, b) in boxes]
    print(Peso)
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    resolver_instancia(L, W, H, boxes, os.path.join( dir_path ,'saida.txt'), Sigma, Peso)

if __name__ == "__main__":
    main()