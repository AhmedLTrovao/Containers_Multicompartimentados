function grafico(file)

fid = fopen(file,'r');
data = fscanf(fid,'%f');
fclose(fid);

cx = data(1);
cy = data(2);
cz = data(3);

figure
set(gcf,'color',[1 1 1])
hold on
axis equal
grid on

xlabel('X')
ylabel('Y')
zlabel('Z')

axis([0 cx 0 cy 0 cz])

view(60,25)
rotate3d on

draw_container(cx,cy,cz)

k = 4;
l = length(data);

while k < l

    x = data(k); k=k+1;
    y = data(k); k=k+1;
    z = data(k); k=k+1;

    dx = data(k); k=k+1;
    dy = data(k); k=k+1;
    dz = data(k); k=k+1;

    type = data(k); k=k+1;

    if type == 1
        color = [0.5 0.5 0.5]; % parede
    else
        color = rand(1,3); % caixa
    end

    draw_box(x,y,z,dx,dy,dz,color)

end

end


function draw_container(cx,cy,cz)

plot3([0 cx cx 0 0],[0 0 cy cy 0],[0 0 0 0 0],'k')
plot3([0 cx cx 0 0],[0 0 cy cy 0],[cz cz cz cz cz],'k')

plot3([0 0],[0 0],[0 cz],'k')
plot3([cx cx],[0 0],[0 cz],'k')
plot3([cx cx],[cy cy],[0 cz],'k')
plot3([0 0],[cy cy],[0 cz],'k')

end


function draw_box(x,y,z,dx,dy,dz,color)

v = [
x y z
x+dx y z
x+dx y+dy z
x y+dy z
x y z+dz
x+dx y z+dz
x+dx y+dy z+dz
x y+dy z+dz
];

f = [
1 2 3 4
5 6 7 8
1 2 6 5
2 3 7 6
3 4 8 7
4 1 5 8
];

patch('Vertices',v,'Faces',f,...
      'FaceColor',color,...
      'EdgeColor','k',...
      'FaceAlpha',0.8);

end