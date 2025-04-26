function S = compute_lat(f, ...
    room_size,Nsec,Nnodes,T_ia, lambda_nodes, MCS_Areas, bandwidth)
    
    c = 3e8; %speed of light
    control_packet_size = 25 * 8;  % bits
    data_packet_size    = 64000 * 8; 
    
    tprop_max = room_size./c; %propagation delay across different distances. 
    data_rates = [bandwidth*2, bandwidth*log2(16), bandwidth*log2(64)] .* 0.7605 .*1e9;
%     data_rates = [157.4, 210.2, 315.4]  .* 1e9;
    
    min_data_rate = min(data_rates);
    avg_data_rate = mean(data_rates);
   
    T_cts = control_packet_size / min_data_rate;
    T_ack = T_cts;
    T_cta = T_cts;
    T_rts = T_cts;
    T_bo_max = 10e-9;
    
    T_data_max = data_packet_size / min_data_rate;
    T_tx_max = T_cts + T_data_max + T_ack + 2*(tprop_max);

    T_wait = 2*(control_packet_size / min_data_rate) +  T_bo_max  + 2*tprop_max;
    
    t_cycle_max = Nsec*T_wait + (Nnodes*T_tx_max);
    t = 1e-9:1e-7:t_cycle_max;

    %% compute the pdf of transmission time: 
    f_t_tx = zeros(1,length(t));

    for m=1:length(MCS_Areas)
%         p_m = (lambda_nodes * MCS_Areas(m)) * exp(-1*lambda_nodes*MCS_Areas(m))
        p_m = MCS_Areas(m) / ((2*room_size)^2);
        time_m = (data_packet_size) / data_rates(m);
        time_m = time_m + T_cts  + T_ack + 2*(mean((1:1:room_size)./c));
        idx = findClosestIndex(t , time_m);
        f_t_tx(idx) = f_t_tx(idx) + p_m;
    end

    mean_t_tx = sum(t .* f_t_tx);
    
    %% compute the system Load rho
    p = (Nsec*T_wait) / (T_ia - (Nnodes*mean_t_tx));

%     figure;plot(t,f_t_tx);
    

    counter = 4;
    lambda_ = 1./T_ia; % packet rate
    p = (Nsec*T_wait) / ((T_ia - (Nnodes*mean_t_tx))); % System load.
    f_t_cycle = zeros(1,length(t));
    f_t_face  = zeros(1,length(t));
    %% Compute T_cycle Now:
    T_tx_static = T_cts  + T_ack + 2*(mean((1:1:room_size)./c));

    for n = 0 : Nnodes
        P_n = probn(Nnodes,n,p);
        t_static2 = Nsec*T_wait;
        t_total = 0 ;
        for x = 0:n
            tau = n-x;
            node_prop_m1 = MCS_Areas(end) / ((2*room_size)^2);
            p_x_m1 = probn(n,x,node_prop_m1);
            t_total = t_total + (x*(T_tx_static + ( (data_packet_size) / data_rates(end)) ));
            for y = 0:tau
                zeta = tau - y;
                node_prop_m2 = MCS_Areas(end-1) / ((2*room_size)^2);
                p_x_m2 = probn(tau,y,node_prop_m2);
                t_total = t_total + (y*(T_tx_static + ( (data_packet_size) / data_rates(end-1)) ));
                for z = 0: zeta
                    if(x+y+z ~= n)
                        t_total = 0;
                        continue;
                    end
                    node_prop_m3 = MCS_Areas(end-2) / ((2*room_size)^2);
                    p_x_m3 = probn(zeta,z,node_prop_m3);
                    t_total = t_total + (z*(T_tx_static + ( (data_packet_size) / data_rates(end-2)) ));
%                     if((x+y+z == n))
%                         total_possibility = [total_possibility; [x y z n]];
% 
%                     end
                    total_prop = P_n * p_x_m1*p_x_m2*p_x_m3;
%                     disp(t_total +t_static2);
                    index = findClosestIndex(t, t_total +t_static2 );
                    t_total = 0;
                    f_t_cycle(index) = f_t_cycle(index) + total_prop;
                    f_t_face(1:index) = f_t_face(1:index) + (ones(1,length(f_t_face(1:index))).*total_prop);
                end
            end
        end

    end

    area = trapz(t, f_t_face);
    f_t_face = f_t_face ./area;



    %% T - Wait Time: 
    f_T_wait   = zeros(1,length(t)); % PDF of t_wait
    f_T_wait(1) = (1-p);
    f_T_wait    = f_T_wait + (f_t_cycle.*p);
    
    area = trapz(t, f_T_wait);
    f_T_wait = f_T_wait ./area;

    f_T_sector = zeros(1,length(t));
    for m=1:length(MCS_Areas)
        p_m = MCS_Areas(m) / ((2*room_size)^2);
        time_m = (data_packet_size) / data_rates(m);
        time_m = time_m + T_wait +T_cts  + T_ack + 3*(mean((1:1:room_size)./c));
        idx = findClosestIndex(t , time_m);
        f_T_sector(idx) = f_T_sector(idx) + p_m;
    end
    area = trapz(t, f_T_sector);
    f_T_sector = f_T_sector ./ area;

    f_t_conv = conv(f_t_face, f_T_wait);
    f_t_conv = f_t_conv ./ sum(f_t_conv);
    f_t_conv = conv(f_t_conv,f_T_sector);
    f_t_conv = f_t_conv ./ sum(f_t_conv);
    S=0;
    for i = 1:length(t)
        S = S + ((data_packet_size/ t(i)) * f_t_conv(i));
    end
    
    end


    function P_n = probn(n_nodes,n,rho)
        P_n = nchoosek(n_nodes,n) * (1-rho)^(n_nodes-n)*rho^n;
    end

function idx = findClosestIndex(list, value)
    % Find the index of the closest value in the list
    [~, idx] = min(abs(list - value));
end

