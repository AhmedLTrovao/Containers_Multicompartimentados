def read_data(arquivo):
    instancias = []
    with open(arquivo, "r") as f:
        linhas = [linha.strip() for linha in f if linha.strip() != ""]
    
    i = 0
    while i < len(linhas):
        # Lê a primeira linha da instância
        parts = linhas[i].split()
        num_tipos, L, W, H = map(int, parts[:4])
        i += 1
        
        # Lê as linhas de cada tipo de caixa
        boxes = []
        for _ in range(num_tipos):
            parts = linhas[i].split()
            v_i, l_i, w_i, h_i, b_i = map(float, parts[:5])
            boxes.append((int(l_i), int(w_i), int(h_i), int(b_i)))
            i += 1
        
        instancias.append({"L": L, "W": W, "H": H, "boxes": boxes})
    
    return instancias
