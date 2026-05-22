def ler_multiplas_instancias(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = [l.strip() for l in f.readlines() if l.strip()]
    
    i = 0
    instancia_id = 1
    while i < len(linhas):
        try:
            # Linha mestre: [num_tipos, L, W, H]
            cabecalho = linhas[i].split()
            num_tipos = int(cabecalho[0])
            
            # 1. Ler Caixas
            boxes = []
            for j in range(1, num_tipos + 1):
                partes = linhas[i + j].split()
                # (l, w, h, qtd)
                boxes.append((int(partes[1]), int(partes[2]), int(partes[3]), int(partes[4])))
            
            # 2. Ler Compartimentos
            # Eles começam após as 'num_tipos' linhas de caixas
            # Mas como saber quantos compartimentos existem? 
            # Geralmente termina quando a próxima linha tem 4 ou 6 elementos (novo cabeçalho)
            compartimentos = []
            ponteiro_comp = i + num_tipos + 1
            
            while ponteiro_comp < len(linhas):
                partes_comp = linhas[ponteiro_comp].split()
                # Se a linha tem 3 elementos, é um compartimento (L, W, H)
                if len(partes_comp) == 3:
                    compartimentos.append((int(partes_comp[0]), int(partes_comp[1]), int(partes_comp[2])))
                    ponteiro_comp += 1
                else:
                    # Se não tem 3, possivelmente é o início da próxima instância
                    break
            
            yield instancia_id, compartimentos, boxes
            
            # Atualiza o índice para o início da próxima instância
            i = ponteiro_comp
            instancia_id += 1
            
        except Exception as e:
            print(f"Erro ao processar bloco na linha {i}: {e}")
            break