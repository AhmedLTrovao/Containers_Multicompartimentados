def read_data(file_path):
    with open(file_path, 'r') as f:
        # Filtra linhas vazias
        lines = [line.strip() for line in f.readlines() if line.strip()]

    all_instances = []
    idx = 0
    
    # Loop para percorrer o arquivo inteiro
    while idx < len(lines):
        try:
            # 1. Cabeçalho da instância
            cabecalho = list(map(int, lines[idx].split()))
            L, W, H = cabecalho[1], cabecalho[2], cabecalho[3]
            idx += 1

            # 2. Ler as Caixas
            boxes = []
            while idx < len(lines):
                parts = list(map(float, lines[idx].split()))
                # Se a linha só tem 1 número, é a quantidade de paredes
                if len(parts) == 1:
                    num_walls = int(parts[0])
                    idx += 1
                    break
                
                # Armazena l, w, h, qtd
                boxes.append((int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))
                idx += 1

            # 3. Ler as Paredes
            walls_list = []
            for _ in range(num_walls):
                if idx < len(lines):
                    p = list(map(float, lines[idx].split()))
                    walls_list.append({
                        'l': int(p[1]), 'w': int(p[2]), 'h': int(p[3]),
                        'x': int(p[5]), 'y': int(p[6])
                    })
                    idx += 1
            
            # Adiciona a instância processada à lista final
            all_instances.append({
                "L": L, "W": W, "H": H, 
                "boxes": boxes, 
                "walls": walls_list
            })
            
        except IndexError:
            break # Fim do arquivo ou erro de formatação

    return all_instances