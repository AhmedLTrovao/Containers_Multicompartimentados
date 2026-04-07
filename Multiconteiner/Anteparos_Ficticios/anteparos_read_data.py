def read_data(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    # 1. Primeira linha: [Qtd_Tipos, L_cont, W_cont, H_cont]
    cabecalho = list(map(int, lines[0].split()))
    L, W, H = cabecalho[1], cabecalho[2], cabecalho[3]

    # 2. Ler as Caixas (Próximas 5 linhas conforme seu exemplo)
    boxes = []
    idx = 1
    # Vamos ler até encontrar a linha que indica a quantidade de paredes
    while idx < len(lines):
        parts = list(map(float, lines[idx].split()))
        if len(parts) == 1: # Encontrou o "5" das paredes
            num_walls = int(parts[0])
            idx += 1
            break
        # parts[0]=Vol, parts[1]=l, parts[2]=w, parts[3]=h, parts[4]=qtd, parts[5]=cliente
        boxes.append((int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))
        idx += 1

    # 3. Ler as Paredes
    walls_list = []
    for _ in range(num_walls):
        if idx < len(lines):
            p = list(map(float, lines[idx].split()))
            # p[0]=Vol, p[1]=l, p[2]=w, p[3]=h, p[4]=qtd, p[5]=x, p[6]=y
            walls_list.append({
                'l': int(p[1]), 'w': int(p[2]), 'h': int(p[3]),
                'x': int(p[5]), 'y': int(p[6])
            })
            idx += 1

    return [{"L": L, "W": W, "H": H, "boxes": boxes, "walls": walls_list}]