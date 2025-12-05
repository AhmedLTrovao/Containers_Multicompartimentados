from solver import resolver_multi_container

if __name__ == "__main__":
    # Example data
    L, W, H = 12, 8, 8
    num_containers = 2 # TRYING WITH 2 CONTAINERS
    
    # (L, W, H, quantity)
    boxes_example = [
        (6, 3, 2, 4), # 4 boxes available
        (6, 4, 3, 10), # 10 boxes available
        (8, 3, 2, 6),
        (4, 3, 2, 4),
        (4, 4, 3, 6)
    ]
    
    resolver_multi_container(L, W, H, boxes_example, num_containers, "solucao_multi.txt")
    
    