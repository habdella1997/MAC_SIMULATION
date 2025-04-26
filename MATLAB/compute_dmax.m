function d_max_mcs = compute_dmax(bandwidth_value,gain_value,lambda)
    P_tx    = 0.1; %watts
    P_tx_db = 10 * log10(P_tx);
    MCS_SNR_MIN = [12.4 19.2 25.4];
    P_N = 10 * log10( 1.3807e-23 * 290 * bandwidth_value); % Noise Power [dB]
    gamma = ((MCS_SNR_MIN - P_tx_db - (2*gain_value)) + P_N) ./ -20;
    d_max_mcs = (lambda .* (10.^(gamma))) ./ (4.*pi);
end

