clc;
close all;
clear;

f = 130e9;
lambda = 3e8 / f;
c = 3e8;

control_packet_size = 25 * 8; 
data_packet_size    = 64000 * 8;

d = 1:1:18;
tprop = d./c;
tprop = max(tprop);

data_rate = [52.4 105.3 157.4 210.2 315.4] .* 1e9;
avg_date_rate = min(data_rate);

T_cts = control_packet_size / avg_date_rate;
T_ack = T_cts;
T_cta = T_cts;
T_rts = T_cts;
T_bo_max = 10e-9;

T_data = data_packet_size / max(data_rate);

T_tx = T_cts + T_data + T_ack + 2*(mean(tprop));
T_wait = T_cta +  T_bo_max + T_rts + 2*tprop;


T_total = (100:50:1000) .* 1e-6 ; %800e-6; %(100:100:1000) .*1e-6;
S_Results = [];

N_sec = 30;

for k = 1:length(T_total)
    T_ia = T_total(k);
    lambda_ = 1./T_ia;
    
    Nnodes = 30;
    t_cycle_max = N_sec*T_wait + (Nnodes*T_tx);
    t_cycle_min = N_sec*T_wait ;
    p = (N_sec*T_wait) / ((T_ia - (Nnodes*T_tx)));
    
    n = 0:1:Nnodes;
    t = 0:1e-7:t_cycle_max;
    % t = t(2:end);
    P_n = zeros(1,length(n));
    
    f_T_cycle  = zeros(1,length(t));
    f_T_face   = zeros(1,length(t));
    f_T_wait   = zeros(1,length(t));
    f_T_sector = zeros(1,length(t));
    f_T_success  = zeros(1,length(t));
    
    for i = 1:length(n)
        combv =  nchoosek(Nnodes,n(i));
        t_1 = ((1-p)^(Nnodes-n(i))) * p^(n(i));
        P_n(i) = combv*t_1;
        t_cycle_n = N_sec*T_wait + (n(i)*T_tx);
        idx = findClosestIndex(t , t_cycle_n);
        f_T_cycle(idx) = P_n(i);
        idx2 = findClosestIndex(t , t_cycle_n);
%         if(idx2 <= 2)
%             continue;
%         end
    %     disp("Target: " + string(t_cycle_n*P_n(i)));
    %     disp("Match: "  + string(t(idx2)));
    %     disp("Index: " + string(idx2));
    %     disp("Diff: " + string(abs(t(idx2)-(t_cycle_n*P_n(i)))));
    %     v_val = ((1/P_n(i))*(1/((t_cycle_n))));
        f_T_face(1:idx2) = f_T_face(1:idx2) + (ones(1,length(f_T_face(1:idx2))).*P_n(i));
    end
   f_T_face = f_T_face ./ sum(f_T_face);
%     f_T_cycle = f_T_cycle ./ sum(f_T_cycle);
    figure;
    plot(t,f_T_face);

return;


    big_k = 10;
    P_b = 0.05;
    
    for small_k = 1:big_k
        scale_constant = (1/small_k) * (1-P_b) * P_b^(small_k-1);
        f_T_success = f_T_success + (scale_constant .* f_T_face);
    end

    f_T_face = f_T_success;% ./ sum(f_T_success);
       figure;
    plot(t,f_T_face);
return;
    
    
    %% T - Wait Time: 
    f_T_wait(1) = (1-p);
    f_T_wait    = f_T_wait + (f_T_cycle.*p);
    f_T_wait    = f_T_wait ./ sum(f_T_wait);
    
    %% T - Sector Time
    distance_MCS     = [18, 17.6, 9.5];
    data_rate_MCS    = [157.4, 210.2, 315.4] .* 1e9;
    MCS_P_m = 1/length(distance_MCS);
    for i = 1:length(distance_MCS)
        t_prop2 = 3* (distance_MCS(i) / c) ;
        t_data2 = data_packet_size/data_rate_MCS(i);
        arg     = T_wait + t_prop2 + T_cts + t_data2 + T_ack;
        idx2 = findClosestIndex(t , arg);
        f_T_sector(1,idx2) = MCS_P_m;
    end
    
    f_T_sector  = f_T_sector ./ sum(f_T_sector);
    % f_T_face   = f_T_face(1,:);% ./ sum(f_T_face(1,:));
    % f_T_wait   = f_T_face(1,:);% ./ sum(f_T_wait(1,:));
    % f_T_sector = f_T_face(1,:);% ./ sum(f_T_sector(1,:));
    
    
    f_t_conv = conv(f_T_face, f_T_wait);
    f_t_conv = f_t_conv ./ sum(f_t_conv);
    f_t_conv = conv(f_t_conv,f_T_sector);
    f_t_conv = f_t_conv ./ sum(f_t_conv);
    
%     figure;
%     plot(f_t_conv);
    
    S=0;
    t(1) = 1.00000000000000e-09;
    f_t_conv(1) = 0;
    %     for i=1:1:length(pdf_t_conv)
    %         S = S + packet_size * 8 / i * pdf_t_conv(i);
    %     end
    for i = 1:length(t)
        S = S + ((data_packet_size/ t(i)) * f_t_conv(i));
    end
    S_Results = [S_Results S];
end
figure;
plot(T_total.*1e6, S_Results/1e9);
title("Throughput [Gbps] Accross different Inter-arrival Time");
grid on;
xlim([min(T_total*1e6) , max(T_total*1e6)]);
function idx = findClosestIndex(list, value)
    % Find the index of the closest value in the list
    [~, idx] = min(abs(list - value));
end