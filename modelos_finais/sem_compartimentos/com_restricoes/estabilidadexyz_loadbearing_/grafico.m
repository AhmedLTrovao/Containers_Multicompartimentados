function grafico(file, step_by_step)

% le o arquivo de dados para construir o grafico 3d
fid=fopen(file,'r');
tfile=fscanf(fid,'%f');
fclose(fid); % Boa prática fechar o arquivo

% dimensoes globais do container
cx=tfile(1);
cy=tfile(2); % Agora este é o W_global (W * num_containers)
cz=tfile(3);
num_containers=tfile(4); % NOVO: Lê a quantidade de compartimentos

% inicializa o grafico
hf=figure;
set(hf,'color',[1 1 1]);
plot3(1,1,1); hold on;
plot3(cx,cy,cz); 

axis equal;
xlabel('X','FontWeight','bold','FontSize',12);
ylabel('Y','FontWeight','bold','FontSize',12);
zlabel('Z','FontWeight','bold','FontSize',12);
grid on;                
box on;                 
axis([0 cx 0 cy 0 cz]); 
view(66,30);
rotate3d on;
light;
camlight headlight;

% imprime os contornos do SUPER container
x=0; y=0; z=0;
h=line( [x x],       [y y],       [z z+cz]    ); set(h,'color','k'); 
h=line( [x x+cx],    [y y],       [z z]       ); set(h,'color','k'); 
h=line( [x+cx x+cx], [y y],       [z+cz z]    ); set(h,'color','k'); 
h=line( [x+cx x],    [y y],       [z+cz z+cz] ); set(h,'color','k'); 
h=line( [x+cx x+cx], [y y+cy],    [z z]       ); set(h,'color','k'); 
h=line( [x+cx x+cx], [y+cy y+cy], [z z+cz]    ); set(h,'color','k'); 
h=line( [x+cx x+cx], [y y+cy],    [z+cz z+cz] ); set(h,'color','k'); 
h=line( [x x],       [y y+cy],    [z z]       ); set(h,'color','k'); 
h=line( [x x],       [y+cy y],    [z+cz z+cz] ); set(h,'color','k'); 
h=line( [x+cx x],    [y+cy y+cy], [z+cz z+cz] ); set(h,'color','k'); 
h=line( [x+cx x],    [y+cy y+cy], [z z]       ); set(h,'color','k'); 
h=line( [x x],       [y+cy y+cy], [z z+cz]    ); set(h,'color','k'); 

% NOVO: Desenha as divisórias dos compartimentos
W_unit = cy / num_containers; % Largura de um único compartimento
for c = 1:(num_containers-1)
    y_div = c * W_unit;
    h=line([0 cx], [y_div y_div], [0 0]); set(h, 'color', 'r', 'LineStyle', '--');
    h=line([0 cx], [y_div y_div], [cz cz]); set(h, 'color', 'r', 'LineStyle', '--');
    h=line([0 0], [y_div y_div], [0 cz]); set(h, 'color', 'r', 'LineStyle', '--');
    h=line([cx cx], [y_div y_div], [0 cz]); set(h, 'color', 'r', 'LineStyle', '--');
end

% le coordenadas e dimensoes das caixas empacotadas
l_tfile=length(tfile);
k_idx=5; % NOVO: Começa a ler as caixas a partir do índice 5

% --- Definição de Cores ---
cor=[]; ncor=1;
cor1=0;
while cor1<=1
    cor2=0;
    while cor2 <=1
        cor3=0;
        while cor3<=0.5
            cor3=cor3+0.5;
            cor(ncor,:)=[cor1 cor2 cor3]; ncor=ncor+1;            
        end
        cor2=cor2+0.5;
    end;
    cor1=cor1+0.5;
end
cor(1,:)=[0.8 0.8 0];
cor(2,:)=[0.8 0.4 0];
cor(3,:)=[0.6 0.2 0.8];
cor(4,:)=[0.6 0.4 0.2];
cor(5,:)=[0.2 0.4 0.6];
cor(6,:)=[0.8 0.2 0.6];
cor(7,:)=[0 0.4 0.8];
cor(8,:)=[0 0.8 0.8];

cor_vazio='k';
tbox=0;
volume=0;
max_x=0;
tbloco=[-1, -1, -1];

% Loop de leitura
while(k_idx <= l_tfile - 8) % Margem de segurança
    x=tfile(k_idx); k_idx=k_idx+1;
    y=tfile(k_idx); k_idx=k_idx+1;
    z=tfile(k_idx); k_idx=k_idx+1;
    dx=tfile(k_idx); k_idx=k_idx+1;
    wy=tfile(k_idx); k_idx=k_idx+1;
    hz=tfile(k_idx); k_idx=k_idx+1;
    
    % NOVO: Lê os 3 parâmetros finais na ordem correta do Python
    type_box=tfile(k_idx); k_idx=k_idx+1;
    consumer=tfile(k_idx); k_idx=k_idx+1;
    compartimento=tfile(k_idx); k_idx=k_idx+1; 

    % Cores baseadas no cliente (você pode trocar para 'compartimento' se preferir!)
    bcor=mod(consumer,ncor); if(bcor==0) bcor=1; end 

    tbox=tbox+1;
    if (dx+x>max_x) max_x=dx+x; end;
    volume=volume+dx*wy*hz;

    if(step_by_step==1)
        if(hz~=tbloco(3) | wy~=tbloco(2) | dx~= tbloco(1))
            if(tbloco(1)~=-1 )
                pause;
            end
            tbloco(3)=hz; tbloco(2)=wy; tbloco(1)=dx;
        end
    end

    h=line( [x x],       [y y],       [z z+hz]    ); set(h,'color','k'); 
    h=line( [x x+dx],    [y y],       [z z]       ); set(h,'color','k'); 
    h=line( [x+dx x+dx], [y y],       [z+hz z]    ); set(h,'color','k'); 
    h=line( [x+dx x],    [y y],       [z+hz z+hz] ); set(h,'color','k'); 
    h=line( [x+dx x+dx], [y y+wy],    [z z]       ); set(h,'color','k'); 
    h=line( [x+dx x+dx], [y+wy y+wy], [z z+hz]    ); set(h,'color','k'); 
    h=line( [x+dx x+dx], [y y+wy],    [z+hz z+hz] ); set(h,'color','k'); 
    h=line( [x x],       [y y+wy],    [z z]       ); set(h,'color','k'); 
    h=line( [x x],       [y+wy y],    [z+hz z+hz] ); set(h,'color','k'); 
    h=line( [x+dx x],    [y+wy y+wy], [z+hz z+hz] ); set(h,'color','k'); 
    h=line( [x+dx x],    [y+wy y+wy], [z z]       ); set(h,'color','k'); 
    h=line( [x x],       [y+wy y+wy], [z z+hz]    ); set(h,'color','k'); 

    fill3( [x x x+dx x+dx],       [y y y y],             [z+hz z z z+hz],       cor(bcor,:) );
    fill3( [x x+dx x+dx x],       [y y y+wy y+wy],       [z+hz z+hz z+hz z+hz], cor(bcor,:) );
    fill3( [x x+dx x+dx x],       [y y y+wy y+wy],       [z z z z],             cor(bcor,:) );
    fill3( [x x+dx x+dx x],       [y+wy y+wy y+wy y+wy], [z z z+hz z+hz],       cor(bcor,:) );
    fill3( [x+dx x+dx x+dx x+dx], [y y+wy y+wy y],       [z z z+hz z+hz],       cor(bcor,:) );
    fill3( [x x x x],             [y y y+wy y+wy],       [z+hz z z z+hz],       cor(bcor,:) );
    
    title(['Carga Total: ' num2str(tbox) ' caixas']);
end

vol_container_max=max_x*cy*cz;
disp(['Ocupação (considerando Max_X): ' num2str(volume/vol_container_max)]);

vol_container_total=cx*cy*cz;
disp(['Ocupação (Total): ' num2str(volume/vol_container_total)]);
disp(['X Máximo atingido: ' num2str(max_x)]);