clc;
close all;
clear;

f = 130e9;
c = 3e8; % speed of light

control_packet_size = 25 * 8;  % bits
data_packet_size    = 64000 * 8; 


room_max = 60;
d = 5:1:60;

tprop = d./c; %propagation delay across different distances. 
tpropmax = max(tprop);
tpropmean = mean(tprop);

data_rates = [1,2,3,4,6 ] .* 69.12e9 ;

control_datarates = data_rates .* 0.05;
data_datarates    = data_rates .* 0.95;

T_cts = control_packet_size / min(control_datarates);
T_ack = T_cts;
T_cta = T_cts;
T_rts = T_cts;
T_bo_max = 20e-9;

T_data = data_packet_size / mean(data_datarates);



inter_arrival_time_list = (200:100:1000) .* 1e-6 ; 
S_Results = [];
t = 1e-9:1e-9:300e-6;
Nnodes = 50;
for k = 1:length(inter_arrival_time_list)
    n = 0:1:Nnodes;    
    f_T_rts    = zeros(1,length(t)); % PDF of t_cycle
    f_T_slot   = zeros(1,length(t)); % PDF of t_face
    f_T_wait   = zeros(1,length(t)); % PDF of t_wait
    f_T_sector = zeros(1,length(t)); % PDF of t_sector
    t_cycle_n  = zeros(1,Nnodes);    % Cycle Time over different n transmissions

    tia = inter_arrival_time_list(k);
    lambda = 1/tia;
    mu     = 1/T_data;
    rho = (50*lambda)/mu;

    mean_backoff = T_bo_max /2;
    
    %% Compute T_rts
    for i = 1:10
        p_collision = 1- (exp(-1*lambda*T_rts)^(Nnodes-1-i));
        T_c         = (i) * ((tpropmean*2) + mean_backoff + 2*T_rts + ((2^i)*1e-9)/2) ;
        idx = findClosestIndex(t , T_c);
        f_T_rts(1:idx) = f_T_rts(1:idx) + (ones(1,length(f_T_rts(1:idx))).*p_collision);
    end
    area = trapz(t, f_T_rts);
    f_T_rts = f_T_rts ./area;

    for n = 0:100
        p_n = (1-rho)*rho^n;
        T_slot = (T_data)*n;
        idx = findClosestIndex(t , T_slot);
        f_T_slot(idx) = f_T_slot(idx) + p_n;
    end    
    area = trapz(t, f_T_slot);
    f_T_slot = f_T_slot ./area;

    %% T - Sector Time
    distance_MCS     = [18, 17.6];
    beff             = [10,8];
    data_rate_MCS    = beff.*0.95.*69.12e9;

    MCS_P_m = 1/length(distance_MCS); % Probability of m out of M {doing a 1/M}
    
    for i = 1:length(distance_MCS)
        t_prop2 = 3* (distance_MCS(i) / c) ;
        t_data2 = data_packet_size/data_rate_MCS(i);
        arg     =  t_prop2 + T_cts + T_rts + t_data2 + T_ack;
        idx2 = findClosestIndex(t , arg);
        f_T_sector(1,idx2) = f_T_sector(1,idx2) + MCS_P_m;
    end
    area = trapz(t, f_T_sector);
    f_T_sector = f_T_sector ./ area;


    f_t_conv = conv(f_T_rts, f_T_slot);
    f_t_conv = f_t_conv ./ sum(f_t_conv);
    f_t_conv = conv(f_t_conv,f_T_sector);
    f_t_conv = f_t_conv ./ sum(f_t_conv);
    
    S = 0;
    for i = 1:length(t)
    S = S + ((data_packet_size/ t(i)) * f_t_conv(i));
    end
    S_Results = [S_Results S];
end
  

figure;
plot(inter_arrival_time_list.*1e6, S_Results./1e9);

title("Throughput [Gbps] Accross Different Inter-arrival Time");
grid on;
xlim([min(inter_arrival_time_list*1e6) , max(inter_arrival_time_list*1e6)]);
% hold on;
% 
% plot(inter_arrival_time_list.*1e6, [185,193,203,211,219,228,234,247,249]);
% legend("Analytical","Simulation");
xlabel("Inter-Arrival Time [us]");
ylabel("Avg. Tput [Gbps]");
% ylim([0, 40]);
% legend('P_{LoS} = 0.1' , 'P_{LoS} = 0.3' , 'P_{LoS} = 0.5', 'P_{LoS} = 0.7', 'P_{LoS} = 0.9' , 'P_{LoS} = 0.98' , ...
%     'P_{LoS} = 1');
function idx = findClosestIndex(list, value)
    % Find the index of the closest value in the list
    [~, idx] = min(abs(list - value));
end