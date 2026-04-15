function grafico_multi_seguro(file, step_by_step)
    
    fid = fopen(file, 'r');
    if fid == -1
        error('Não foi possível abrir o ficheiro: %s', file);
    end
    
    % 1. Lê a quantidade de compartimentos
    num_compartimentos = round(fscanf(fid, '%f', 1));
    fprintf('Número de compartimentos: %d\n', num_compartimentos);
    
    % 2. Lê as dimensões de cada compartimento
    L_k = zeros(1, num_compartimentos);
    W_k = zeros(1, num_compartimentos);
    H_k = zeros(1, num_compartimentos);
    
    for c = 1:num_compartimentos
        L_k(c) = fscanf(fid, '%f', 1);
        W_k(c) = fscanf(fid, '%f', 1);
        H_k(c) = fscanf(fid, '%f', 1);
        fprintf('Compartimento %d: L=%.1f, W=%.1f, H=%.1f\n', c-1, L_k(c), W_k(c), H_k(c));
    end
    
    % 3. Lê o resto do arquivo
    caixas_data = fscanf(fid, '%f');
    fclose(fid);
    
    
    fprintf('Total de valores lidos: %d\n', length(caixas_data));
    
    % Verifica se há caixas
    if isempty(caixas_data)
        warning('Nenhuma caixa encontrada no arquivo!');
        return;
    end
    
    % Setup do gráfico
    hf = figure;
    set(hf, 'color', [1 1 1]);
    hold on; axis equal; grid on; box on;
    xlabel('X (Largura)'); ylabel('Y (Profundidade)'); zlabel('Z (Altura)');
    view(66, 30); rotate3d on; light; camlight headlight;
    
    % Gap entre compartimentos
    compartimento_gap = 0; 
    
    % Desenhar os frames dos compartimentos
    offset_y = 0; 
    for c_id = 1:num_compartimentos
        L_atual = L_k(c_id);
        W_atual = W_k(c_id);
        H_atual = H_k(c_id);
        
        draw_compartimento_frame(0, offset_y, 0, L_atual, W_atual, H_atual);
        text(L_atual/2, offset_y + W_atual/2, H_atual * 1.1, ...
             sprintf('Comp %d', c_id-1), 'HorizontalAlignment', 'center', ...
             'FontWeight', 'bold', 'FontSize', 12);
             
        offset_y = offset_y + W_atual + compartimento_gap;
    end
    
    % Ajusta os eixos
    axis([-1, max(L_k)+1, -1, offset_y+1, 0, max(H_k)+1]);
    
    % Cores
    cores = [
        0.8 0.8 0;   % amarelo
        0.8 0.4 0;   % laranja
        0.6 0.2 0.8; % roxo
        0.6 0.4 0.2; % marrom
        0.2 0.4 0.6; % azul escuro
        0.8 0.2 0.6; % rosa
        0   0.4 0.8; % azul claro
        0   0.8 0.8; % ciano
        0.3 0.7 0.3; % verde
        0.9 0.3 0.3; % vermelho
    ];
    
    % Leitura das caixas
    idx = 1;
    tbox = 0; 
    total_volume = 0;
    l_data = length(caixas_data);
    
    fprintf('\nLendo caixas...\n');
    
    while idx + 8 <= l_data
        x = caixas_data(idx);     idx = idx + 1;
        y = caixas_data(idx);     idx = idx + 1;
        z = caixas_data(idx);     idx = idx + 1;
        dx = caixas_data(idx);    idx = idx + 1;
        wy = caixas_data(idx);    idx = idx + 1;
        hz = caixas_data(idx);    idx = idx + 1;
        type_box = caixas_data(idx); idx = idx + 1; 
        client = caixas_data(idx);   idx = idx + 1;
        c_id = caixas_data(idx);     idx = idx + 1; 

        
        
        % Verifica se o compartimento existe
        if c_id + 1 > num_compartimentos
            warning('Compartimento %d não existe! Pulando caixa...', c_id);
            continue;
        end
        
        % Seleciona cor
        cor_idx = mod(type_box, size(cores, 1)) + 1;
        
        tbox = tbox + 1; 
        volume = dx * wy * hz;
        total_volume = total_volume + volume;
        
        fprintf('Caixa %d: Comp=%d, Pos=(%.1f,%.1f,%.1f), Dim=(%.1f,%.1f,%.1f), Vol=%.1f\n', ...
                tbox, c_id, x, y, z, dx, wy, hz, volume);
        
        if step_by_step == 1
            pause(0.3);
        end
        
        % Desenha as faces da caixa
        draw_box_faces(x, y, z, dx, wy, hz, cores(cor_idx, :));
        plot_box_outline(x, y, z, dx, wy, hz);
    end
    
    fprintf('\n=== RESUMO ===\n');
    fprintf('Total de caixas plotadas: %d\n', tbox);
    fprintf('Volume total empacotado: %.2f\n', total_volume);
    fprintf('Volume total disponível: %.2f\n', sum(L_k .* W_k .* H_k));
    fprintf('Taxa de ocupação: %.1f%%\n', total_volume / sum(L_k .* W_k .* H_k) * 100);
    
    view(3);
    lighting gouraud;
end

% Função para desenhar todas as faces da caixa
function draw_box_faces(x, y, z, dx, wy, hz, cor)
    % Face frontal (z constante)
    fill3([x x+dx x+dx x], [y y y+wy y+wy], [z z z z], cor, 'FaceAlpha', 0.7);
    % Face traseira (z+hz)
    fill3([x x+dx x+dx x], [y y y+wy y+wy], [z+hz z+hz z+hz z+hz], cor, 'FaceAlpha', 0.7);
    % Face inferior (y constante)
    fill3([x x+dx x+dx x], [y y y y], [z z z+hz z+hz], cor, 'FaceAlpha', 0.7);
    % Face superior (y+wy)
    fill3([x x+dx x+dx x], [y+wy y+wy y+wy y+wy], [z z z+hz z+hz], cor, 'FaceAlpha', 0.7);
    % Face esquerda (x constante)
    fill3([x x x x], [y y+wy y+wy y], [z z z+hz z+hz], cor, 'FaceAlpha', 0.7);
    % Face direita (x+dx)
    fill3([x+dx x+dx x+dx x+dx], [y y+wy y+wy y], [z z z+hz z+hz], cor, 'FaceAlpha', 0.7);
end

% Função para desenhar o frame do compartimento
function draw_compartimento_frame(x, y, z, cx, cy, cz)
    col = 'k'; lw = 2; 
    vertices = [
        x y z; x+cx y z; x+cx y+cy z; x y+cy z;  % base
        x y z+cz; x+cx y z+cz; x+cx y+cy z+cz; x y+cy z+cz  % topo
    ];
    edges = [
        1 2; 2 3; 3 4; 4 1;  % base
        5 6; 6 7; 7 8; 8 5;  % topo
        1 5; 2 6; 3 7; 4 8   % laterais
    ];
    
    for e = 1:size(edges, 1)
        line(vertices(edges(e,:), 1), vertices(edges(e,:), 2), vertices(edges(e,:), 3), ...
             'Color', col, 'LineWidth', lw);
    end
end

% Função para desenhar o contorno da caixa
function plot_box_outline(x, y, z, dx, wy, hz)
    lcols = 'k';
    vertices = [
        x y z; x+dx y z; x+dx y+wy z; x y+wy z;
        x y z+hz; x+dx y z+hz; x+dx y+wy z+hz; x y+wy z+hz
    ];
    edges = [
        1 2; 2 3; 3 4; 4 1;  % base
        5 6; 6 7; 7 8; 8 5;  % topo
        1 5; 2 6; 3 7; 4 8   % laterais
    ];
    
    for e = 1:size(edges, 1)
        line(vertices(edges(e,:), 1), vertices(edges(e,:), 2), vertices(edges(e,:), 3), ...
             'Color', lcols, 'LineWidth', 1);
    end
end