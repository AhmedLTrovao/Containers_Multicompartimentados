from fl_solver import fl_solver
import os

def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida =  os.path.join(dir_path, "teste.txt")
    (L,W,H) = (12, 8, 8)
    boxes = [(6,3,2,2), (6,4,3,5), (8,3,2,3), (4,3,2,2), (4,4,3,3)]
    fl_solver(L, W, H, boxes, arquivo_saida)
    return

if __name__ == "__main__":
    main()