function grafico_multi_2D(file, step_by_step)
    % Uso: grafico_multi_2D('saida_multicompartimento.txt', 0)
    
    fid = fopen(file, 'r');
    if fid == -1
        error('Não foi possível abrir o ficheiro: %s', file);
    end
    
    tfile = fscanf(fid, '%f');
    fclose(fid);
    
    % 1. Quantidade de compartimentos
    num_compartimentos = round(tfile(1));
    
    % 2. Dimensões dinâmicas dos compartimentos
    L_k = zeros(1, num_compartimentos);
    W_k = zeros(1, num_compartimentos);
    H_k = zeros(1, num_compartimentos);
    
    idx_leitura = 2; 
    for c = 1:num_compartimentos
        L_k(c) = tfile(idx_leitura); idx_leitura = idx_leitura + 1;
        W_k(c) = tfile(idx_leitura); idx_leitura = idx_leitura + 1;
        H_k(c) = tfile(idx_leitura); idx_leitura = idx_leitura + 1;
    end
    
    data_start_index = idx_leitura;
    
    % Setup do gráfico
    hf = figure;
    set(hf, 'color', [1 1 1]);
    hold on; axis equal; grid on; box on;
    xlabel('Eixo X (Comprimento)'); ylabel('Eixo Y (Largura)'); zlabel('Eixo Z (Altura)');
    view(120, 30); rotate3d on; light; camlight headlight;
    
    % --- Desenho dos Compartimentos Usando a Lógica Espelhada ---
    for c_id = 0:num_compartimentos-1
        idx = c_id + 1;
        
        % Cálculo do Offset Físico Idêntico ao solver.py
        if mod(c_id, 2) == 0
            O_X = 0; % Lado Esquerdo
        else
            O_X = L_k(idx - 1); % Lado Direito (Deslocado pelo comprimento do esquerdo)
        end
        
        % Soma das larguras dos pares anteriores para determinar a posição na coluna Y
        sum_W = 0;
        for c = 0:2:(c_id - mod(c_id, 2) - 1)
            sum_W = sum_W + W_k(c + 1);
        end
        O_Y = sum_W;
        
        % Desenhar a estrutura do compartimento
        draw_compartimento_frame(O_X, O_Y, 0, L_k(idx), W_k(idx), H_k(idx));
        
        % Destaque Visual das Portas Laterais (Acessos Externos)
        if mod(c_id, 2) == 0
            % Lado Esquerdo: Acesso pela parede X = 0
            draw_door(O_X, O_Y, 0, W_k(idx), H_k(idx));
        else
            % Lado Direito: Acesso pela parede externa oposta X = O_X + L
            draw_door(O_X + L_k(idx), O_Y, 0, W_k(idx), H_k(idx));
        end
        
        text(O_X + L_k(idx)/2, O_Y + W_k(idx)/2, H_k(idx) * 1.05, ...
             sprintf('Comp %d', c_id), 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
    end
    
    % --- Geração da Paleta de Cores baseada nos Clientes ---
    cor = [
        0.8 0.8 0.0;   0.8 0.4 0.0;
        0.6 0.2 0.8;   0.6 0.4 0.2;
        0.2 0.4 0.6;   0.8 0.2 0.6;
        0.0 0.4 0.8;   0.0 0.8 0.8;
        0.1 0.7 0.3;   0.9 0.1 0.2
    ];
    ncor = size(cor, 1);
    
    % --- Renderização das Caixas (Coordenadas Absolutas do Python) ---
    k_data = data_start_index;
    tbox = 0; 
    total_volume = 0;
    l_tfile = length(tfile);
    
    while k_data + 8 <= l_tfile
        x_plot = tfile(k_data);    k_data = k_data + 1;
        y_plot = tfile(k_data);    k_data = k_data + 1;
        z      = tfile(k_data);    k_data = k_data + 1;
        dx     = tfile(k_data);    k_data = k_data + 1;
        wy     = tfile(k_data);    k_data = k_data + 1;
        hz     = tfile(k_data);    k_data = k_data + 1;
        type   = tfile(k_data);    k_data = k_data + 1; 
        client = tfile(k_data);    k_data = k_data + 1;
        c_id   = tfile(k_data);    k_data = k_data + 1; 
        
        % Seleção de cor associada dinamicamente ao ID do Cliente
        bcor = mod(client, ncor) + 1;
        
        tbox = tbox + 1; 
        total_volume = total_volume + dx * wy * hz;
        
        % Desenho dos 6 lados do bloco em 3D
        fill3([x_plot x_plot+dx x_plot+dx x_plot], [y_plot y_plot y_plot+wy y_plot+wy], [z z z z], cor(bcor,:), 'FaceAlpha', 0.85);
        fill3([x_plot x_plot+dx x_plot+dx x_plot], [y_plot y_plot y_plot+wy y_plot+wy], [z+hz z+hz z+hz z+hz], cor(bcor,:), 'FaceAlpha', 0.85);
        fill3([x_plot x_plot+dx x_plot+dx x_plot], [y_plot y_plot y_plot y_plot], [z z z+hz z+hz], cor(bcor,:), 'FaceAlpha', 0.85);
        fill3([x_plot x_plot+dx x_plot+dx x_plot], [y_plot+wy y_plot+wy y_plot+wy y_plot+wy], [z z z+hz z+hz], cor(bcor,:), 'FaceAlpha', 0.85);
        fill3([x_plot x_plot x_plot x_plot], [y_plot y_plot+wy y_plot+wy y_plot], [z z z+hz z+hz], cor(bcor,:), 'FaceAlpha', 0.85);
        fill3([x_plot+dx x_plot+dx x_plot+dx x_plot+dx], [y_plot y_plot+wy y_plot+wy y_plot], [z z z+hz z+hz], cor(bcor,:), 'FaceAlpha', 0.85);
        
        plot_box_outline(x_plot, y_plot, z, dx, wy, hz);
        
        if step_by_step == 1, pause(0.05); end
    end
    
    % Ajuste automático das margens de visualização
    max_X_plot = max(L_k) * 2;
    max_Y_plot = sum(W_k) / 2;
    max_Z_plot = max(H_k);
    axis([-0.5, max_X_plot + 0.5, -0.5, max_Y_plot + 0.5, 0, max_Z_plot + 1]);
    
    fprintf('Total de caixas renderizadas: %d\n', tbox);
    fprintf('Volume total ocupado: %.2f m³\n', total_volume);
end

% --- Funções Auxiliares de Desenho ---
function draw_compartimento_frame(x, y, z, cx, cy, cz)
    col = [0.3 0.3 0.3]; lw = 1.5; 
    line([x x],       [y y],       [z z+cz],    'Color', col, 'LineWidth', lw);
    line([x+cx x+cx], [y y],       [z z+cz],    'Color', col, 'LineWidth', lw);
    line([x x],       [y+cy y+cy], [z z+cz],    'Color', col, 'LineWidth', lw);
    line([x+cx x+cx], [y+cy y+cy], [z z+cz],    'Color', col, 'LineWidth', lw);
    line([x x+cx],    [y y],       [z z],       'Color', col, 'LineWidth', lw);
    line([x+cx x+cx], [y y+cy],    [z z],       'Color', col, 'LineWidth', lw);
    line([x+cx x],    [y+cy y+cy], [z z],       'Color', col, 'LineWidth', lw);
    line([x x],       [y+cy y],    [z z],       'Color', col, 'LineWidth', lw);
    line([x x+cx],    [y y],       [z+cz z+cz], 'Color', col, 'LineWidth', lw);
    line([x+cx x+cx], [y y+cy],    [z+cz z+cz], 'Color', col, 'LineWidth', lw);
    line([x+cx x],    [y+cy y+cy], [z+cz z+cz], 'Color', col, 'LineWidth', lw);
    line([x x],       [y+cy y],    [z+cz z+cz], 'Color', col, 'LineWidth', lw);
end

function draw_door(x, y, z, dy, dz)
    Y = [y, y+dy, y+dy, y];
    Z = [z, z, z+dz, z+dz];
    X = [x, x, x, x];
    patch('XData', X, 'YData', Y, 'ZData', Z, ...
          'FaceColor', [1.0 0.3 0.3], 'FaceAlpha', 0.15, 'EdgeColor', [0.8 0 0], 'LineWidth', 1.5, 'LineStyle', '-.');
end

function plot_box_outline(x, y, z, dx, wy, hz)
    lcols = [0.1 0.1 0.1];
    line([x x],       [y y],       [z z+hz],    'Color', lcols);
    line([x+dx x+dx], [y y],       [z z+hz],    'Color', lcols);
    line([x x],       [y+wy y+wy], [z z+hz],    'Color', lcols);
    line([x+dx x+dx], [y+wy y+wy], [z z+hz],    'Color', lcols);
    line([x x+dx],    [y y],       [z z],       'Color', lcols);
    line([x+dx x+dx], [y y+wy],    [z z],       'Color', lcols);
    line([x+dx x],    [y+wy y+wy], [z z],       'Color', lcols);
    line([x x],       [y+wy y],    [z z],       'Color', lcols);
    line([x x+dx],    [y y],       [z+hz z+hz], 'Color', lcols);
    line([x+dx x+dx], [y y+wy],    [z+hz z+hz], 'Color', lcols);
    line([x+dx x],    [y+wy y+wy], [z+hz z+hz], 'Color', lcols);
    line([x x],       [y+wy y],    [z+hz z+hz], 'Color', lcols);
end