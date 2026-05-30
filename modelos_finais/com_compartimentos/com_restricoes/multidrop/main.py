import os
import sys

from solver import resolver_instancia
from testes import *

def main():
    
    (compartimentos_t, clientes_t, arquivo_saida_t, stabv_t, stabh_t, loadbearing_t, tempo_limite_t) = teste_unicompartimentado()

    resolver_instancia(
        compartimentos=compartimentos_t, 
            clientes=clientes_t, 
            arquivo_saida=arquivo_saida_t,
            tempo_limite=tempo_limite_t,
            stabv = stabv_t,
            stabh = stabh_t,
            loadbearing = loadbearing_t
    )


if __name__ == "__main__":
    main()