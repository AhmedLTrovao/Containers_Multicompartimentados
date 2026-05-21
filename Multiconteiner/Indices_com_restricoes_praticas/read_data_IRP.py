# read_data.py

def ler_instancias_praticas(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = [l.strip() for l in f.readlines() if l.strip()]
    
    i = 0
    instancia_id = 1
    
    while i < len(linhas):
        try:
            # 1. Linha Mestre
            partes_mestre = linhas[i].split()
            num_tipos_caixas = int(partes_mestre[0])
            num_compartimentos = int(partes_mestre[1])
            i += 1
            
            # Dicionário temporário para agrupar itens por cliente
            clientes_dict = {}
            
            # 2. Ler as Caixas
            for _ in range(num_tipos_caixas):
                p = linhas[i].split()
                
                # Campos obrigatórios que sempre existem (Garantidos pelo seu layout)
                l, w, h = int(p[0]), int(p[1]), int(p[2])
                qtd = int(p[3])
                id_cliente = int(p[4])
                
                # Tratamento seguro para os parâmetros físicos opcionais/faltantes
                # Se não existirem na linha, assumem os valores padrão coerentes
                peso = float(p[5]) if len(p) > 5 else float(l * w * h)
                delta_x = float(p[6]) if len(p) > 6 else 4.0
                sigma = float(p[7]) if len(p) > 7 else 1000.0
                
                item = {
                    "dims": (l, w, h),
                    "qtd": qtd,
                    "peso": peso,
                    "sigma": sigma,
                    "delta_x": delta_x
                }
                
                if id_cliente not in clientes_dict:
                    clientes_dict[id_cliente] = []
                clientes_dict[id_cliente].append(item)
                
                i += 1
            
            # Converter o dicionário para a lista ordenada de clientes
            clientes = []
            for id_cli in sorted(clientes_dict.keys()):
                clientes.append({
                    "id_cliente": id_cli,
                    "itens": clientes_dict[id_cli]
                })
            
            # 3. Ler os Compartimentos
            compartimentos = []
            for _ in range(num_compartimentos):
                p_comp = linhas[i].split()
                compartimentos.append((
                    int(p_comp[0]), 
                    int(p_comp[1]), 
                    int(p_comp[2])
                ))
                i += 1
                
            yield instancia_id, compartimentos, clientes
            instancia_id += 1
            
        except IndexError:
            # Captura fim de arquivo inesperado ou blocos incompletos sem quebrar o loop anterior
            break
        except Exception as e:
            print(f"Erro ao processar linha {i} da Instância {instancia_id}: {e}")
            break