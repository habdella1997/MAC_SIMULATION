clc;
close all;
clear;

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

inter_arrival_time_list = (200) .* 1e-6 ; 
S_Results = [];
beamwidth = 0.5:0.5:20;
beamwidth_rad = deg2rad(beamwidth);
N_sec = ceil((2*pi) ./ beamwidth_rad);
Nnodes = 50;

T_ia = (200) .* 1e-6 ; 
lambda_ = 1./T_ia; % packet rate
p = (N_sec.*T_wait) ./ ((T_ia - (Nnodes*T_tx))); % System load.

t_cycle_avg  = N_sec.*T_wait + (Nnodes.*p.*T_tx);
t_cycle_avg2 = (N_sec.*T_wait) + (Nnodes.*p.*T_tx) + (N_sec.*(2e-6));

figure;
plot(beamwidth, t_cycle_avg.*1000);
hold on;
plot(beamwidth, t_cycle_avg2.*1000);

xlabel("Antenna Beamwidth [deg]");
ylabel("Time [ms]");
legend("0 Beam Steering Latency" , "2 us Beam Steering Latency")
grid on;

