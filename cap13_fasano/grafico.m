function grafico(file,step_by_step)

% le o arquivo de dados para construir o grafico 3d
fid=fopen(file,'r');
tfile=fscanf(fid,'%f');

% dimensoes do container
cx=tfile(1);
cy=tfile(2);
cz=tfile(3);

% inicializa o grafico
hf=figure;
set(hf,'color',[1 1 1]);
plot3(1,1,1); hold on;
plot3(cx,cy,cz); % hold on;

axis off;
rotate3d on;
light;
camlight headlight;

% imprime os contornos do container
x=0; y=0; z=0;
h=line( [x x],       [y y],       [z z+cz]    ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x x+cx],    [y y],       [z z]       ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x+cx x+cx], [y y],       [z+cz z]    ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x+cx x],    [y y],       [z+cz z+cz] ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x+cx x+cx], [y y+cy],    [z z]       ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x+cx x+cx], [y+cy y+cy], [z z+cz]    ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x+cx x+cx], [y y+cy],    [z+cz z+cz] ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x x],       [y y+cy],    [z z]       ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x x],       [y+cy y],    [z+cz z+cz] ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x+cx x],    [y+cy y+cy], [z+cz z+cz] ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x+cx x],    [y+cy y+cy], [z z]       ); set(h,'color','k'); % set(h,'visible','off');
h=line( [x x],       [y+cy y+cy], [z z+cz]    ); set(h,'color','k'); % set(h,'visible','off');

axis equal;
view(66,30);

% le coordenadas e dimensoes das caixas empacotadas
l_tfile=length(tfile);
k=4;

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
ant_con=0;
tbox=0;
volume=0;
max_x=0;
loss_vol=struct('vol',0,'x',-1,'y',-1,'z',-1,'d',-1,'w',-1,'h',-1);
tbloco=[-1, -1, -1];

while(k<l_tfile)
    x=tfile(k); k=k+1;
    y=tfile(k); k=k+1;
    z=tfile(k); k=k+1;
    dx=tfile(k); k=k+1;
    wy=tfile(k); k=k+1;
    hz=tfile(k); k=k+1;
    consumer=tfile(k); k=k+1;
    type_box=tfile(k); k=k+1;

    bcor=mod(consumer,ncor); if(bcor==0) bcor=1; end %estou usando o type_box para as cores

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


    h=line( [x x],       [y y],       [z z+hz]    ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x x+dx],    [y y],       [z z]       ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x+dx x+dx], [y y],       [z+hz z]    ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x+dx x],    [y y],       [z+hz z+hz] ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x+dx x+dx], [y y+wy],    [z z]       ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x+dx x+dx], [y+wy y+wy], [z z+hz]    ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x+dx x+dx], [y y+wy],    [z+hz z+hz] ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x x],       [y y+wy],    [z z]       ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x x],       [y+wy y],    [z+hz z+hz] ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x+dx x],    [y+wy y+wy], [z+hz z+hz] ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x+dx x],    [y+wy y+wy], [z z]       ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;
    h=line( [x x],       [y+wy y+wy], [z z+hz]    ); set(h,'color','k'); % if(ok_b==1) set(h,'color','k'); else set(h,'color',cor_vazio); end;


    fill3( [x x x+dx x+dx],       [y y y y],             [z+hz z z z+hz],       cor(bcor,:) );
    fill3( [x x+dx x+dx x],       [y y y+wy y+wy],       [z+hz z+hz z+hz z+hz], cor(bcor,:) );
    fill3( [x x+dx x+dx x],       [y y y+wy y+wy],       [z z z z],             cor(bcor,:) );
    fill3( [x x+dx x+dx x],       [y+wy y+wy y+wy y+wy], [z z z+hz z+hz],       cor(bcor,:) );
    fill3( [x+dx x+dx x+dx x+dx], [y y+wy y+wy y],       [z z z+hz z+hz],       cor(bcor,:) );
    fill3( [x x x x],             [y y y+wy y+wy],       [z+hz z z z+hz],       cor(bcor,:) );
    %h=text(x+dx/2,y,z+hz/2,num2str(type_box)); set(h,'fontsize',10); % imprime o tipo da caixa
    title(num2str(tbox));

    type_box    
end

vol_container=max_x*cy*cz;
disp(volume/vol_container)

vol_container=cx*cy*cz;
disp(volume/vol_container)

disp(max_x);