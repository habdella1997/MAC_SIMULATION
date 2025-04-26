clc;
close all;
clear;

f = 230e9;
G = [50];

beamwidth = sqrt((4*pi)./(10.^(G./10)));
rad2deg(beamwidth)
lambda = 3e8 / f;
diameter = (1.22 * lambda) ./beamwidth;
w_0 = diameter./2;
z_r = (pi.*(w_0).^2) ./ lambda;

max_Distance = [1:1:25]; 
w_z = w_0 .* sqrt(1 + (max_Distance./z_r).^2);

figure;
plot(max_Distance, w_z.*39.3701);
xlabel('Distance to Reflector [m]');
ylabel('Diameter of Beam [inch]');
grid on;
% % title("Diameter of Beam at Varying Distances and Antenna Gain");
% figure;
% plot(G, rad2deg(beamwidth));
% xlabel('Gain [dBi]');
% ylabel('Antenna Beamwidth [deg]')
% % title("Antenna Beamwidth with Varying Gain Values");
% grid on;