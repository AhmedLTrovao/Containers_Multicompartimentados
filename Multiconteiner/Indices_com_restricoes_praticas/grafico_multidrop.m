function grafico_multi_2D(file, step_by_step)
    % Uso: grafico_multi_2D('solucao_multi2.txt', 0)
    
    fid = fopen(file, 'r');
    if fid == -1
        error('Não foi possível abrir o ficheiro: %s', file);
    end
    
    % Lê TODO o arquivo para um vetor de uma vez só
    tfile = fscanf(fid, '%f');
    fclose(fid);
    
    % 1. Lê a quantidade de compartimentos (primeira posição do vetor)
    num_compartimentos = round(tfile(1));
    
    % 2. Lê as dimensões (L, W, H) de cada compartimento dinamicamente
    L_k = zeros(1, num_compartimentos);
    W_k = zeros(1, num_compartimentos);
    H_k = zeros(1, num_compartimentos);
    
    idx_leitura = 2; % Começa a ler a partir do segundo número
    for c = 1:num_compartimentos
        L_k(c) = tfile(idx_leitura); idx_leitura = idx_leitura + 1;
        W_k(c) = tfile(idx_leitura); idx_leitura = idx_leitura + 1;
        H_k(c) = tfile(idx_leitura); idx_leitura = idx_leitura + 1;
    end
    
    % Onde os dados das caixas realmente começam:
    data_start_index = idx_leitura;
    
    % - Setup do grafico
    hf = figure;
    set(hf, 'color', [1 1 1]);
    hold on; axis equal; grid on; box on;
    xlabel('X'); ylabel('Y'); zlabel('Z');
    view(66, 30); rotate3d on; light; camlight headlight;
    
    % Gap visual para separar os compartimentos (coloque 0 se quiser eles colados)
    compartimento_gap = 0; 
    
    % --- Cálculos dos Offsets e Gaps Visuais em 2D ---
    O_X_k = zeros(1, num_compartimentos);
    O_Y_k = zeros(1, num_compartimentos);
    gap_x = zeros(1, num_compartimentos);
    gap_y = zeros(1, num_compartimentos);
    
    for c_id = 0:num_compartimentos-1
        idx = c_id + 1; % MATLAB começa no índice 1
        
        % Paridade no Eixo X: 0, 2, 4 ficam na esquerda (X=0). 1, 3, 5 ficam na direita.
        if mod(c_id, 2) == 0
            O_X_k(idx) = 0;
            gap_x(idx) = 0;
            is_left = true;
        else
            O_X_k(idx) = L_k(idx - 1); % L do lado esquerdo
            gap_x(idx) = compartimento_gap; % Afasta visualmente
            is_left = false;
        end
        
        % Paridade no Eixo Y: Somamos apenas as larguras da coluna da esquerda
        limite_par_anterior = c_id - mod(c_id, 2); 
        sum_W = 0;
        for c = 0:2:(limite_par_anterior - 1)
            sum_W = sum_W + W_k(c + 1);
        end
        O_Y_k(idx) = sum_W;
        gap_y(idx) = (limite_par_anterior / 2) * compartimento_gap;
        
        % Desenhar o "Wireframe" do compartimento
        frame_x = O_X_k(idx) + gap_x(idx);
        frame_y = O_Y_k(idx) + gap_y(idx);
        
        draw_compartimento_frame(frame_x, frame_y, 0, L_k(idx), W_k(idx), H_k(idx));
        
        % --- DESTAQUE DA PORTA LATERAL ---
        if is_left
            % Porta no X inicial (X = frame_x)
            draw_door(frame_x, frame_y, 0, 0, W_k(idx), H_k(idx));
        else
            % Porta no X final (X = frame_x + L_k)
            draw_door(frame_x + L_k(idx), frame_y, 0, 0, W_k(idx), H_k(idx));
        end
        
        text(frame_x + L_k(idx)/2, frame_y + W_k(idx)/2, H_k(idx) * 1.1, ...
             sprintf('Comp %d', c_id), 'HorizontalAlignment', 'center', 'FontWeight', 'bold');
    end
    
    % Ajusta os limites do gráfico dinamicamente com base nas maiores coordenadas
    max_X_plot = max(O_X_k + L_k + gap_x);
    max_Y_plot = max(O_Y_k + W_k + gap_y);
    max_Z_plot = max(H_k);
    axis([-1, max_X_plot + 1, -1, max_Y_plot + 1, 0, max_Z_plot + 1]);
    
    % - Cores
    cor = []; ncor = 1; cor1 = 0;
    while cor1 <= 1
        cor2 = 0;
        while cor2 <= 1
            cor3 = 0;
            while cor3 <= 0.5
                cor3 = cor3 + 0.5; cor(ncor, :) = [cor1 cor2 cor3]; ncor = ncor + 1;            
            end
            cor2 = cor2 + 0.5;
        end
        cor1 = cor1 + 0.5;
    end
    cor(1,:) = [0.8 0.8 0];   cor(2,:) = [0.8 0.4 0];
    cor(3,:) = [0.6 0.2 0.8]; cor(4,:) = [0.6 0.4 0.2];
    cor(5,:) = [0.2 0.4 0.6]; cor(6,:) = [0.8 0.2 0.6];
    cor(7,:) = [0 0.4 0.8];   cor(8,:) = [0 0.8 0.8];
    
    % - Leitura das Caixas
    k_data = data_start_index;
    tbox = 0; 
    total_volume = 0;
    l_tfile = length(tfile);
    
    while k_data + 8 <= l_tfile
        x = tfile(k_data);     k_data = k_data + 1;
        y = tfile(k_data);     k_data = k_data + 1;
        z = tfile(k_data);     k_data = k_data + 1;
        dx = tfile(k_data);    k_data = k_data + 1;
        wy = tfile(k_data);    k_data = k_data + 1;
        hz = tfile(k_data);    k_data = k_data + 1;
        type_box = tfile(k_data); k_data = k_data + 1; 
        client = tfile(k_data);   k_data = k_data + 1;
        c_id = tfile(k_data);     k_data = k_data + 1; 
        
        c_idx = c_id + 1; 
        % MAGIA: Como o Python já calculou e somou as coordenadas globais,
        % o MATLAB apenas adiciona o "gap_x" e "gap_y" para separar no desenho!
        x_plot = x + gap_x(c_idx);
        y_plot = y + gap_y(c_idx);
        
        bcor = mod(client + 1, ncor); if bcor == 0, bcor = 1; end
        
        tbox = tbox + 1; 
        total_volume = total_volume + dx * wy * hz;
        if step_by_step == 1, pause(0.1); end
        
        fill3([x_plot x_plot+dx x_plot+dx x_plot], [y_plot y_plot y_plot+wy y_plot+wy], [z z z z], cor(bcor,:));
        fill3([x_plot x_plot+dx x_plot+dx x_plot], [y_plot y_plot y_plot+wy y_plot+wy], [z+hz z+hz z+hz z+hz], cor(bcor,:));
        fill3([x_plot x_plot+dx x_plot+dx x_plot], [y_plot y_plot y_plot y_plot], [z z z+hz z+hz], cor(bcor,:));
        fill3([x_plot x_plot+dx x_plot+dx x_plot], [y_plot+wy y_plot+wy y_plot+wy y_plot+wy], [z z z+hz z+hz], cor(bcor,:));
        fill3([x_plot x_plot x_plot x_plot], [y_plot y_plot+wy y_plot+wy y_plot], [z z z+hz z+hz], cor(bcor,:));
        fill3([x_plot+dx x_plot+dx x_plot+dx x_plot+dx], [y_plot y_plot+wy y_plot+wy y_plot], [z z z+hz z+hz], cor(bcor,:));
        
        plot_box_outline(x_plot, y_plot, z, dx, wy, hz);
    end
    fprintf('Total Boxes: %d\n', tbox);
    fprintf('Total Packed Volume: %.2f\n', total_volume);
end

% --- Helper Functions ---
function draw_compartimento_frame(x, y, z, cx, cy, cz)
    col = 'k'; lw = 2; 
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

function draw_door(x, y, z, dx, dy, dz)
    % Desenha uma superfície translúcida para representar a porta lateral
    % Neste caso, a porta é um plano em YZ no ponto X
    
    Y = [y, y+dy, y+dy, y];
    Z = [z, z, z+dz, z+dz];
    X = [x, x, x, x];
    
    % Adiciona um painel semi-transparente (azul claro)
    patch('XData', X, 'YData', Y, 'ZData', Z, ...
          'FaceColor', [0.2 0.6 1], 'FaceAlpha', 0.2, 'EdgeColor', 'b', 'LineWidth', 2, 'LineStyle', '--');
end

function plot_box_outline(x, y, z, dx, wy, hz)
    lcols = 'k';
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