def read_data(arquivo_entrada):
    instancias = []
    with open(arquivo_entrada,'r') as f:
        linhas = [linha.strip() for linha in f if linha.strip()]
    idx = 0
    while idx < len(linhas):
        partes = linhas[idx].split()
        n_tipos, L, W, H = map(int, partes[:4])
        idx += 1
        boxes = []
        for _ in range(n_tipos):
            partes = linhas[idx].split()
            v_i, l_i, w_i, h_i, b_i = map(float, partes[:5])
            boxes.append((int(l_i), int(w_i), int(h_i), int(b_i)))
            idx += 1
        instancias.append({"L": int(L), "W": int(W), "H": int(H), "boxes": boxes})
    return instancias
