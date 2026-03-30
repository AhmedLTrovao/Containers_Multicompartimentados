def read_data(arquivo):
    instancias = []
    with open(arquivo, "r") as f:
        linhas = [l.strip() for l in f if l.strip()]
    
    i = 0
    while i < len(linhas):
        # 1. Cabeçalho
        parts = linhas[i].split()
        num_caixas = int(parts[0])
        L, W, H = map(int, parts[1:4])
        i += 1
        
        # 2. Ler Caixas
        boxes = []
        for _ in range(num_caixas):
            p = linhas[i].split()
            boxes.append((int(p[1]), int(p[2]), int(p[3]), int(p[4])))
            i += 1
        
        # 3. Ler Número de Paredes
        num_paredes = int(linhas[i])
        i += 1
        
        # 4. Ler cada Parede
        walls_list = []
        for _ in range(num_paredes):
            p_w = list(map(float, linhas[i].split()))
            walls_list.append({
                'l': int(p_w[1]), 'w': int(p_w[2]), 'h': int(p_w[3]),
                'b': int(p_w[4]), 'x': int(p_w[5]), 'y': int(p_w[6])
            })
            i += 1
        
        instancias.append({"L": L, "W": W, "H": H, "boxes": boxes, "walls": walls_list})
    return instancias