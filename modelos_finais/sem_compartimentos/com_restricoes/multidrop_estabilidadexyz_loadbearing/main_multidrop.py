
from multidrop_solver import resolver_instancia
import os

def main():
    test = "Fasano"
    
    if test == "multidrop_comparison":
        L, W, H = (12, 8, 8)
        boxes = [(6, 3, 2), (6, 4, 3), (8, 3, 2), (4, 3, 2), (4,4,3)]
        m = len(boxes)
        b = [(1,3,0,0,0), (0,1,2,0,2), (1,1,1,2,1)]
        n = len(b)
        
        # 
        delta = [[boxes[i][0] for i in range(m)] for k in range(n)]
        print (delta)
                
        Sigma = [0, 3, 5, 0, 3]
        Peso = [l*w*h for (l, w, h) in boxes]
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        resolver_instancia(L, W, H, boxes, b, n, delta, os.path.join( dir_path ,'fasano_test.txt'), Sigma, Peso,3600,True,False,False)

    elif "multidrop_comparison":
        L, W, H = (8, 8, 8)
        boxes = [(6, 3, 2), (6, 4, 3), (8, 3, 2), (4, 3, 2), (4,4,3)]
        m = len(boxes)
        b = [(1,3,0,0,0), (0,1,2,0,2), (1,1,1,2,1)]
        n = len(b)
        
        # 
        delta = [[boxes[i][0] for i in range(m)] for k in range(n)]
        print (delta)
                
        Sigma = [0, 3, 5, 0, 3]
        Peso = [l*w*h for (l, w, h) in boxes]
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        resolver_instancia(L, W, H, boxes, b, n, delta, os.path.join( dir_path ,'multidrop_comparison.txt'), Sigma, Peso,3600,True,False,False)
    else:
        L, W, H = (12, 8, 8)
        boxes = [(6, 3, 2), (6, 4, 3), (8, 3, 2), (4, 3, 2), (4,4,3)]
        m = len(boxes)
        b = [(1,3,0,0,0), (0,1,2,0,2), (1,1,1,2,1)]
        n = len(b)
        
        # 
        delta = [[boxes[i][0] for i in range(m)] for k in range(n)]
        print (delta)
                
        Sigma = [0, 3, 5, 0, 3]
        Peso = [l*w*h for (l, w, h) in boxes]
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        resolver_instancia(L, W, H, boxes, b, n, delta, os.path.join( dir_path ,'test_all_restr.txt'), Sigma, Peso,3600,True,True,True)
        

if __name__ == "__main__":
    main()