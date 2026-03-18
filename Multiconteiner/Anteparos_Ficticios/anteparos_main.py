from anteparos_solver import resolver_anteparos

if __name__ == "__main__":

    L, W, H = 12, 8, 8

    # paredes FIXAS (você escolhe!)
    walls = [2, 6]

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
        walls,
        "solucao_anteparos.txt"
    )