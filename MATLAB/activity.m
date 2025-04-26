clc;
close all;
clear all;


f = 130e9;
c = 3e8; %speed of light
control_packet_size = 25 * 8;  % bits
data_packet_size    = 64000 * 8; 

d = 9.5:1:18; % radius of room -> 18 meters 
tprop = d./c; %propagation delay across different distances. 

tpropmax = max(tprop);

data_rates = [157.4, 210.2, 315.4]  .* 1e9;

min_data_rate = min(data_rates);
avg_data_rate = mean(data_rates);

T_cts = control_packet_size / min_data_rate;
T_ack = T_cts;
T_cta = T_cts;
T_rts = T_cts;
T_bo_max = 10e-9;

T_data = data_packet_size / avg_data_rate;

T_tx = T_cts + T_data + T_ack + 2*(mean(tprop));
T_wait = 2*(control_packet_size / min_data_rate) +  T_bo_max  + 2*tpropmax;

inter_arrival_time_list = (150:50:1000) .* 1e-6 ; 
beam_width = [0.1 3 12];

S_Results = [];
N_sec = 360 ./beam_width;

Nnodes = 50;

t_cycle_max = N_sec*T_wait + (Nnodes*T_tx);
t = 1e-9:1e-7:t_cycle_max;

lambda_a = 0.05;
r = 18;
beam_width_rad = deg2rad(beam_width);
lengthsub          = r ./ tan((pi/2) - (beam_width_rad./2));
area_t     = 0.5 .* 2.*lengthsub .* r;

gamma_tx = 1;

pdf_activity = zeros(length(beam_width_rad), length(inter_arrival_time_list));

for bw = 1:length(beam_width_rad)
    for k = 1:length(inter_arrival_time_list)
        T_ia = inter_arrival_time_list(k);
        lambda_ = 1./T_ia; % packet rate
        p = (N_sec(bw).*(T_wait + 2e-6 )) ./ ((T_ia - (Nnodes*T_tx))); % System load.
        sum_tx = 0;
        for n = 1:1:Nnodes
            temp  = ((lambda_a.*area_t(bw)).^(n) .* (exp(-1.*lambda_a.*area_t(bw)))) ./ (factorial(n));
            temp2 = 1 - (1-p)^(gamma_tx*n); 
            sum_tx = sum_tx + (temp*temp2);
        end
        pdf_activity(bw,k) = sum_tx * (1-exp(-1*(lambda_a*area_t(bw))));
    end
end
pdf_activity =pdf_activity';
figure;
x = inter_arrival_time_list * 1e6;
plot(x, pdf_activity(:,1));
hold on
plot(x, pdf_activity(:,2));
hold on
plot(x, pdf_activity(:,3));
legend("0.1\circ","3\circ","12\circ");
grid on;
xlabel("Inter-Arrival Time [\mus]");
ylabel("Probability Of Uplink Transmission")
