clc;
close all;
clear;
lambda_ = 0.05;
r = 18;
N_nodes = lambda_ * pi * r^2;

% x = 0:1:N_nodes;

beam_width = [0.1 3 12];
beam_width = deg2rad(beam_width);
lengthsub          = r ./ tan((pi/2) - (beam_width./2));
area_t     = 0.5 .* 2.*lengthsub .* r;

pdf_a = []

for x = 0:1:6
    temp = ((lambda_.*area_t).^(x) .* (exp(-1.*lambda_.*area_t))) ./ (factorial(x));
    pdf_a = [pdf_a;temp];
end
x = [0:1:x]
figure;
plot(x, pdf_a(:,1));
hold on
plot(x, pdf_a(:,2));
hold on
plot(x, pdf_a(:,3));
legend("0.1\circ","3\circ","12\circ");
grid on;
xlabel("Number of Nodes");
ylabel("PDF")



