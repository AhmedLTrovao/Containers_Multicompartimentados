import os

def teste_multidrop_puro():
    compartimentos = [
        (10, 10, 10), # k=0 (Par - acesso esquerdo, origem O_X = 0)
        (10, 10, 10)  # k=1 (Ímpar - acesso direito, origem O_X = 10)
    ]
    
    clientes = [
        {
          
            "id_cliente": 0, 
            "itens": [
                {"dims": (5, 5, 5), "qtd": 10, "peso": 125.0, "sigma": 990.0, "delta_x": 5.0},
            ]
        },
        {
            "id_cliente": 1,
            "itens": [
                {"dims": (5, 5, 5), "qtd": 6, "peso": 125.0, "sigma": 990.0, "delta_x": 5.0},
            ]
        }
    ]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'teste_multidrop_puro.txt')
    
    stabv = stabh = loadbearing = False
    tempo_limite = 30
    
    return (compartimentos, clientes, arquivo_saida, stabv, stabh, loadbearing, tempo_limite)


def teste_unicompartimentado():
    compartimentos = [
        (12, 8, 8), # k=0 (Par - acesso esquerdo, origem O_X = 0)
    ]
    
    clientes = [
       
         { # ordem do cliente invertida com relação ao fasano
             "id_cliente": 0, 
            "itens": [
                {"dims": (6, 3, 2), "qtd": 1, "peso": 36.0, "sigma": 0, "delta_x": 6.0},
                {"dims": (6, 4, 3), "qtd": 1, "peso":72.0, "sigma": 3, "delta_x": 6.0},
                {"dims": (8, 3, 2), "qtd": 1, "peso":48.0, "sigma": 5, "delta_x": 8.0},
                {"dims": (4, 3, 2), "qtd": 2, "peso":24.0, "sigma": 0, "delta_x": 4.0},
                {"dims": (4, 4, 3), "qtd": 1, "peso": 48.0, "sigma": 3, "delta_x": 4.0}
            ]
        }, {
             "id_cliente": 1, 
            "itens": [
                {"dims": (6, 3, 2), "qtd": 0, "peso": 36.0, "sigma": 0, "delta_x": 6.0},
                {"dims": (6, 4, 3), "qtd": 1, "peso":72.0, "sigma": 3, "delta_x": 6.0},
                {"dims": (8, 3, 2), "qtd": 2, "peso":48.0, "sigma": 5, "delta_x": 8.0},
                {"dims": (4, 3, 2), "qtd": 0, "peso":24.0, "sigma": 0, "delta_x": 4.0},
                {"dims": (4, 4, 3), "qtd": 2, "peso": 48.0, "sigma": 3, "delta_x": 4.0}
            ]
        },{
          
            "id_cliente": 2, 
            "itens": [
                {"dims": (6, 3, 2), "qtd": 1, "peso": 36.0, "sigma": 0, "delta_x": 6.0},
                {"dims": (6, 4, 3), "qtd": 3, "peso":72.0, "sigma": 3, "delta_x": 6.0},
                {"dims": (8, 3, 2), "qtd": 0, "peso":48.0, "sigma": 5, "delta_x": 8.0},
                {"dims": (4, 3, 2), "qtd": 0, "peso":24.0, "sigma": 0, "delta_x": 4.0},
                {"dims": (4, 4, 3), "qtd": 0, "peso": 48.0, "sigma": 3, "delta_x": 4.0}
            ]
        },
        
    ]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'teste_multidrop_unicompartimentado.txt')
    
    stabh = loadbearing = False
    stabv = True
    tempo_limite = 30
    
    return (compartimentos, clientes, arquivo_saida, stabv, stabh, loadbearing, tempo_limite)


def teste_multidrop_2():
    compartimentos = [
        (10, 10, 10), # k=0 
        (10, 10, 10) # k=1 
    ]
    
    clientes = [
       
         { # ordem do cliente invertida com relação ao fasano
             "id_cliente": 0, 
            "itens": [
                {"dims": (5, 5, 5), "qtd": 2, "peso": 36.0, "sigma": 0, "delta_x": 6.0}
            ]
        }, {
             "id_cliente": 1, 
            "itens": [
                {"dims": (5, 5, 5), "qtd": 3, "peso": 36.0, "sigma": 0, "delta_x": 6.0}
            ]
        },{
          
            "id_cliente": 2, 
            "itens": [
                {"dims": (5, 5, 5), "qtd": 11, "peso": 36.0, "sigma": 0, "delta_x": 6.0}
            ]
        },
        
    ]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'teste_multidrop_2.txt')
    
    stabh = loadbearing = False
    stabv = True
    tempo_limite = 30
    
    return (compartimentos, clientes, arquivo_saida, stabv, stabh, loadbearing, tempo_limite)

def validacao_loadbearing():
    compartimentos = [
        (10, 10, 10) # k=0 
    ]
    
    clientes = [
       
         { 
             "id_cliente": 0, 
            "itens": [
                {"dims": (5, 5, 5), "qtd": 4, "peso": 125, "sigma": 1000, "delta_x": 0},
                {"dims": (5, 5, 4), "qtd": 4, "peso": 125, "sigma": 0, "delta_x": 0}
            ]
        }
    ]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'validacao_loadbearing.txt')
    
    stabh = False
    stabv = loadbearing = True
    tempo_limite = 30
    
    return (compartimentos, clientes, arquivo_saida, stabv, stabh, loadbearing, tempo_limite)

def validacao_loadbearing2():
    compartimentos = [
        (10, 10, 10) # k=0 
    ]
    
    clientes = [
       
         { 
             "id_cliente": 0, 
            "itens": [
                {"dims": (5, 5, 5), "qtd": 0, "peso": 125, "sigma": 1000, "delta_x": 0},
                {"dims": (5, 5, 4), "qtd": 8, "peso": 125, "sigma": 0, "delta_x": 0}
            ]
        }
    ]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'validacao_loadbearing2.txt')
    
    stabh = False
    stabv = loadbearing = True
    tempo_limite = 30
    
    return (compartimentos, clientes, arquivo_saida, stabv, stabh, loadbearing, tempo_limite)


def validacao_estabilidade():
    compartimentos = [
        (10, 10, 10) # k=0 
    ]
    
    clientes = [
       
         { 
             "id_cliente": 0, 
            "itens": [
                {"dims": (6, 6, 5), "qtd": 4, "peso": 180, "sigma": 1000, "delta_x": 0},
            ]
        }
    ]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'validacao_estabilidade.txt')
    
    loadbearing = False
    stabv = stabh = True
    tempo_limite = 30
    
    return (compartimentos, clientes, arquivo_saida, stabv, stabh, loadbearing, tempo_limite)

def validacao_multidrop():
    compartimentos = [
        (10, 10, 10), # k=0 
        (10, 10, 10), # k=0 
    ]
    
    clientes = [
       
         { 
             "id_cliente": 0, 
            "itens": [
                {"dims": (5, 10, 5), "qtd": 1, "peso": 200, "sigma": 1000, "delta_x": 5},
            ]
        }, 
         { 
             "id_cliente": 1, 
            "itens": [
                {"dims": (5, 10, 5), "qtd": 7, "peso": 200, "sigma": 1000, "delta_x": 5},
            ]
        }
    ]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'validacao_multidrop.txt')
    
    stabv = True
    loadbearing = stabh = False
    tempo_limite = 30
    
    return (compartimentos, clientes, arquivo_saida, stabv, stabh, loadbearing, tempo_limite)



def validacao_multidrop2():
    compartimentos = [
        (10, 10, 10), # k=0 
        (10, 10, 10), # k=0 
    ]
    
    clientes = [
        { 
             "id_cliente": 0, 
            "itens": [
                {"dims": (5, 10, 10), "qtd": 1, "peso": 200, "sigma": 1000, "delta_x": 5},
            ]
        }, 
         { 
             "id_cliente": 1, 
            "itens": [
                {"dims": (5, 10, 5), "qtd": 1, "peso": 200, "sigma": 1000, "delta_x": 5},
            ]
        }, 
         { 
             "id_cliente": 2, 
            "itens": [
                {"dims": (5, 10, 5), "qtd": 7, "peso": 200, "sigma": 1000, "delta_x": 5},
            ]
        }
    ]
    dir_path = os.path.dirname(os.path.realpath(__file__))
    arquivo_saida = os.path.join(dir_path, 'validacao_multidrop2.txt')
    
    stabv = True
    loadbearing = stabh = False
    tempo_limite = 30
    
    return (compartimentos, clientes, arquivo_saida, stabv, stabh, loadbearing, tempo_limite)