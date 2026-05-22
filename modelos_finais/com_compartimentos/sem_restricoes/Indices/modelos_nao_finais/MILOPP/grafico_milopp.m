function grafico_multi(file, step_by_step)
    % Uso: grafico_multi('solucao_multi2.txt', 0)
    
    % Open file
    fid = fopen(file, 'r');
    if fid == -1
        error('Could not open file: %s', file);
    end
    
    % Lê todo resultado
    tfile = fscanf(fid, '%f');
    fclose(fid);
    
    % Lê o header no formato L W_global H num_compartimentos
    cx = tfile(1);
    cy_global = tfile(2); % Esta é a dimensão somada de todos os compartimentos
    cz = tfile(3);
    num_compartimentos = tfile(4);
    
    % A largura real (local) de um único compartimento
    cy_local = cy_global / num_compartimentos; 
    
    data_start_index = 5;
    
    % - Setup do grafico
    hf = figure;
    set(hf, 'color', [1 1 1]);
    hold on;
    axis equal;
    grid on;
    box on;
    xlabel('X'); ylabel('Y'); zlabel('Z');
    view(66, 30);
    rotate3d on;
    light;
    camlight headlight;
    
    % gap visual pra ver melhor entre os compartimentos (pode alterar para 1 ou 2)
    compartimento_gap = 0; 
    
    % - 3: desenhar o contorno dos compartimentos
    for c_id = 0:num_compartimentos-1
        % O deslocamento de cada "caixote" wireframe
        offset_y = c_id * (cy_local + compartimento_gap);
        
        % desenhar o compartimento usando a largura local
        draw_compartimento_frame(0, offset_y, 0, cx, cy_local, cz);
        
        % adicionar label
        text(cx/2, offset_y + cy_local/2, cz * 1.1, ...
             sprintf('compartimento %d', c_id), ...
             'HorizontalAlignment', 'center', 'FontWeight', 'bold');
    end
    
    % ajustar o tamanho do eixo
    total_y_width = num_compartimentos * cy_local + (num_compartimentos - 1) * compartimento_gap;
    axis([-1, cx+1, -1, total_y_width + 1, 0, cz+1]);
    
    % - 4: cores
    cor = []; ncor = 1;
    cor1 = 0;
    while cor1 <= 1
        cor2 = 0;
        while cor2 <= 1
            cor3 = 0;
            while cor3 <= 0.5
                cor3 = cor3 + 0.5;
                cor(ncor, :) = [cor1 cor2 cor3]; 
                ncor = ncor + 1;            
            end
            cor2 = cor2 + 0.5;
        end
        cor1 = cor1 + 0.5;
    end
    % Cores manuais
    cor(1,:) = [0.8 0.8 0];   cor(2,:) = [0.8 0.4 0];
    cor(3,:) = [0.6 0.2 0.8]; cor(4,:) = [0.6 0.4 0.2];
    cor(5,:) = [0.2 0.4 0.6]; cor(6,:) = [0.8 0.2 0.6];
    cor(7,:) = [0 0.4 0.8];   cor(8,:) = [0 0.8 0.8];
    
    % - 5: desenhar caixas
    l_tfile = length(tfile);
    k = data_start_index;
    tbox = 0;
    total_volume = 0;
    
    while k < l_tfile
        % ler 9 valores: x y z l w h type client compartimento_id
        if k + 8 > l_tfile
            break; 
        end
        
        x = tfile(k);     k = k + 1;
        y = tfile(k);     k = k + 1;
        z = tfile(k);     k = k + 1;
        dx = tfile(k);    k = k + 1;
        wy = tfile(k);    k = k + 1;
        hz = tfile(k);    k = k + 1;
        type_box = tfile(k); k = k + 1; 
        client = tfile(k);   k = k + 1;
        c_id = tfile(k);     k = k + 1; 
        
        % IMPORTANTE: Como a coordenada 'y' gerada no Python já é global 
        % (já contém c_id * cy_local), só somamos o gap visual se ele existir!
        y_plot = y + (c_id * compartimento_gap);
        
        % cor pelo TIPO de caixa (ajustável para client se quiser)
        bcor = mod(type_box, ncor); 
        if bcor == 0, bcor = 1; end
        
        tbox = tbox + 1;
        total_volume = total_volume + dx * wy * hz;
        if step_by_step == 1
             pause(0.1); 
        end
        
        % As chamadas de preenchimento 3D (faces da caixa)
        fill3([x x+dx x+dx x], [y_plot y_plot y_plot+wy y_plot+wy], [z z z z], cor(bcor,:));
        fill3([x x+dx x+dx x], [y_plot y_plot y_plot+wy y_plot+wy], [z+hz z+hz z+hz z+hz], cor(bcor,:));
        fill3([x x+dx x+dx x], [y_plot y_plot y_plot y_plot], [z z z+hz z+hz], cor(bcor,:));
        fill3([x x+dx x+dx x], [y_plot+wy y_plot+wy y_plot+wy y_plot+wy], [z z z+hz z+hz], cor(bcor,:));
        fill3([x x x x], [y_plot y_plot+wy y_plot+wy y_plot], [z z z+hz z+hz], cor(bcor,:));
        fill3([x+dx x+dx x+dx x+dx], [y_plot y_plot+wy y_plot+wy y_plot], [z z z+hz z+hz], cor(bcor,:));
        
        % contorno da caixa
        plot_box_outline(x, y_plot, z, dx, wy, hz);
    end
    
    fprintf('Total Boxes: %d\n', tbox);
    fprintf('Total Packed Volume: %.2f\n', total_volume);
end

% --- Helper Functions ---
function draw_compartimento_frame(x, y, z, cx, cy, cz)
    col = 'k';
    lw = 2; 
    
    % verticais
    line([x x],       [y y],       [z z+cz],    'Color', col, 'LineWidth', lw);
    line([x+cx x+cx], [y y],       [z z+cz],    'Color', col, 'LineWidth', lw);
    line([x x],       [y+cy y+cy], [z z+cz],    'Color', col, 'LineWidth', lw);
    line([x+cx x+cx], [y+cy y+cy], [z z+cz],    'Color', col, 'LineWidth', lw);
    
    % baixo
    line([x x+cx],    [y y],       [z z],       'Color', col, 'LineWidth', lw);
    line([x+cx x+cx], [y y+cy],    [z z],       'Color', col, 'LineWidth', lw);
    line([x+cx x],    [y+cy y+cy], [z z],       'Color', col, 'LineWidth', lw);
    line([x x],       [y+cy y],    [z z],       'Color', col, 'LineWidth', lw);
    
    % topo
    line([x x+cx],    [y y],       [z+cz z+cz], 'Color', col, 'LineWidth', lw);
    line([x+cx x+cx], [y y+cy],    [z+cz z+cz], 'Color', col, 'LineWidth', lw);
    line([x+cx x],    [y+cy y+cy], [z+cz z+cz], 'Color', col, 'LineWidth', lw);
    line([x x],       [y+cy y],    [z+cz z+cz], 'Color', col, 'LineWidth', lw);
end

function plot_box_outline(x, y, z, dx, wy, hz)
    lcols = 'k';
    
    % verticais
    line([x x],       [y y],       [z z+hz],    'Color', lcols);
    line([x+dx x+dx], [y y],       [z z+hz],    'Color', lcols);
    line([x x],       [y+wy y+wy], [z z+hz],    'Color', lcols);
    line([x+dx x+dx], [y+wy y+wy], [z z+hz],    'Color', lcols);
    
    % baixo
    line([x x+dx],    [y y],       [z z],       'Color', lcols);
    line([x+dx x+dx], [y y+wy],    [z z],       'Color', lcols);
    line([x+dx x],    [y+wy y+wy], [z z],       'Color', lcols);
    line([x x],       [y+wy y],    [z z],       'Color', lcols);
    
    % topo 
    line([x x+dx],    [y y],       [z+hz z+hz], 'Color', lcols);
    line([x+dx x+dx], [y y+wy],    [z+hz z+hz], 'Color', lcols);
    line([x+dx x],    [y+wy y+wy], [z+hz z+hz], 'Color', lcols);
    line([x x],       [y+wy y],    [z+hz z+hz], 'Color', lcols);
end