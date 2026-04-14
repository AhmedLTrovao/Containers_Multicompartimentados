function grafico(file)
    % Abertura e leitura do arquivo de dados
    fid = fopen(file,'r');
    if fid == -1
        error('Não foi possível abrir o arquivo: %s', file);
    end
    data = fscanf(fid,'%f');
    fclose(fid);
    
    % Dimensões do contêiner (primeiros 3 valores do arquivo)
    cx = data(1); 
    cy = data(2); 
    cz = data(3);
    
    % Configuração da Janela Gráfica
    figure('Name', ['Visualização: ', file], 'NumberTitle', 'off')
    set(gcf, 'color', [1 1 1])
    hold on; axis equal; grid on;
    xlabel('X (Comprimento)'); ylabel('Y (Largura)'); zlabel('Z (Altura)');
    axis([0 cx 0 cy 0 cz])
    view(60,25); 
    rotate3d on
    
    % Desenha a estrutura externa do contêiner
    draw_container(cx, cy, cz)
    
    % --- Lógica de Gerenciamento de Cores ---
    dimensoes_vistas = []; % Matriz para armazenar [dx, dy, dz] únicos
    cores_atribuidas = []; % Matriz para armazenar as cores [R, G, B] correspondentes
    % ----------------------------------------

    k = 4; % Início dos dados das caixas
    l = length(data);
    
    while k < l
        % Leitura dos dados da caixa/anteparo atual
        x  = data(k); k=k+1;
        y  = data(k); k=k+1;
        z  = data(k); k=k+1;
        dx = data(k); k=k+1;
        dy = data(k); k=k+1;
        dz = data(k); k=k+1;
        type = data(k); k=k+1;
        
        if type == 1
            % Cor para os Anteparos (Cinza Escuro)
            color = [0.2 0.2 0.2]; 
        else
            % Lógica para Caixas: mesma dimensão = mesma cor
            dim_atual = [dx, dy, dz];
            
            % Verifica se este tamanho de caixa já foi processado
            idx = 0;
            if ~isempty(dimensoes_vistas)
                [found, idx] = ismember(dim_atual, dimensoes_vistas, 'rows');
            end
            
            if idx > 0
                % Se já existe, recupera a cor salva
                color = cores_atribuidas(idx, :);
            else
                % Se é um novo tamanho, gera uma cor aleatória e armazena
                color = rand(1,3); 
                dimensoes_vistas = [dimensoes_vistas; dim_atual];
                cores_atribuidas = [cores_atribuidas; color];
            end
        end
        
        % Chama a função para desenhar o bloco
        draw_box(x, y, z, dx, dy, dz, color)
    end
    
    title('Resultado do Carregamento - Modelo de Anteparos Fictícios');
    hold off;
end

% --- Funções Auxiliares de Desenho ---

function draw_container(cx,cy,cz)
    % Desenha as arestas do contêiner
    plot3([0 cx cx 0 0],[0 0 cy cy 0],[0 0 0 0 0],'k','LineWidth',1.5)
    plot3([0 cx cx 0 0],[0 0 cy cy 0],[cz cz cz cz cz],'k','LineWidth',1.5)
    plot3([0 0],[0 0],[0 cz],'k','LineWidth',1.5)
    plot3([cx cx],[0 0],[0 cz],'k','LineWidth',1.5)
    plot3([cx cx],[cy cy],[0 cz],'k','LineWidth',1.5)
    plot3([0 0],[cy cy],[0 cz],'k','LineWidth',1.5)
end

function draw_box(x,y,z,dx,dy,dz,color)
    % Define os 8 vértices da caixa
    v = [
        x y z;           % 1
        x+dx y z;        % 2
        x+dx y+dy z;     % 3
        x y+dy z;        % 4
        x y z+dz;        % 5
        x+dx y z+dz;     % 6
        x+dx y+dy z+dz;  % 7
        x y+dy z+dz      % 8
    ];
    
    % Define as 6 faces da caixa conectando os vértices
    f = [
        1 2 3 4; % Base
        5 6 7 8; % Topo
        1 2 6 5; % Frente
        2 3 7 6; % Direita
        3 4 8 7; % Fundo
        4 1 5 8  % Esquerda
    ];
    
    % Renderiza a caixa usando o comando patch
    patch('Vertices',v,'Faces',f,...
          'FaceColor',color,...
          'EdgeColor','k',...
          'FaceAlpha',0.8); % Transparência para melhor visualização interna
end