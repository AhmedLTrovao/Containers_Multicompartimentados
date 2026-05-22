
from multidrop_solver import resolver_instancia
import os

def main():
    L, W, H = (8, 8, 8)
    boxes = [(2, 2, 2), (3, 3, 3)]
    m = len(boxes)
    b = [(1,1), (1,1), (1,1)]
    n = len(b)
    
    # 
    delta = [[boxes[i][0] for i in range(m)] for k in range(n)]
    print (delta)
            
    Sigma = [100, 100]
    Peso = [l*w*h for (l, w, h) in boxes]
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    resolver_instancia(L, W, H, boxes, b, n, delta, os.path.join( dir_path ,'saida.txt'), Sigma, Peso)

if __name__ == "__main__":
    main()