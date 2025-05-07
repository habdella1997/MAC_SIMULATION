function [p_rx, max_data_rate, SNR_Computed, modulation_scheme] = link_budget(p_tx, distance, max_bandwidth, antenna_gain, f_c, abs_loss)
    % Constants
    SPEED_OF_LIGHT = 3e8;          % m/s
    BOLTZMAN = 1.38064852e-23;     % J/K
    T = 290;                       % K

    % Hardware parameters (replace these with your actual values)
    G_LNA = 20;      % [dB]
    NF_LNA = 3;      % [dB]
    NF_mixer = 10;   % [dB]
    L_mixer = 5;     % [dB]
    L_misc = 2;      % [dB]

    % Convert p_tx from mW to dBm
    p_tx = 10 * log10(p_tx);

    lambda_fc = SPEED_OF_LIGHT / f_c;
    spreading_loss = 20 * log10((4 * pi * distance) / lambda_fc);
    L_total = 2 * L_mixer + L_misc + abs_loss + spreading_loss;

    % Noise Figure calculation
    NF = 10 * log10(10^(NF_LNA / 10) + (10^(NF_mixer / 10) - 1) / 10^(G_LNA / 10));

    % Modulation parameters
    modulation_table = ["BPSK", "QPSK", "8-PSK", "16-QAM", "64-QAM"];
    B_efficiencies = [1, 2, 3, 4, 6];
    SNR_coded = [10.6, 12.4, 17.6, 19.2, 25.4];

    % Noise power
    P_n = 10 * log10(BOLTZMAN * T * max_bandwidth) + 30;  % dBm

    % Received power
    p_rx = (p_tx + antenna_gain + G_LNA) - L_total;

    % SNR
    SNR_Computed = p_rx - (P_n + NF);

    % Modulation selection
    max_data_rate = 0;
    modulation_scheme = '';
    for i = 1:length(B_efficiencies)
        if SNR_Computed >= SNR_coded(i)
            data_rate = max_bandwidth * B_efficiencies(i);
            if data_rate > max_data_rate
                max_data_rate = data_rate;
                modulation_scheme = modulation_table(i);
            end
        end
    end
end
