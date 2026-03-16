from anteparos_solver import resolver_anteparos

if __name__ == "__main__":

    L, W, H = 12, 8, 8

    num_walls = 3

    boxes_example = [
        (6, 3, 2, 4),
        (6, 4, 3, 10),
        (8, 3, 2, 6),
        (4, 3, 2, 4),
        (4, 4, 3, 6)
    ]

    resolver_anteparos(
        L,
        W,
        H,
        boxes_example,
        num_walls,
        "solucao_anteparos.txt"
    )