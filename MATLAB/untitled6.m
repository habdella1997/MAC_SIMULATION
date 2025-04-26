clc;
close all;
clear;
bw_range = [15 25 35 55 65 75]; 
beam_width_range = [0.1 0.5 3 6 12 18];
room_radius      = [5 10 15 20 25]; % [m] 


% Step-1 Compute the Antenna Gain Relative to that of the beam-width
G = 10 .* log10((4*pi) ./ (deg2rad(beam_width_range))); %[dB]

% Example throughput values (use your tput_results instead)
tput_results = load("tput.mat").tput_results;
t_flat = []
figure;
for gain = 1:length(G)
    for bw = 1:length(bw_range)
        for rad = 1:length(room_radius)
            t_val = tput_results(gain,bw,rad);
            t_val = t_val /1e9;
            scatter3(G(gain), bw_range(bw), (2*room_radius(rad))^2, 50,t_val,'filled');
            hold on;
    end
end
end
% ax = gca;
% ax.XDir = 'reverse';
view(-31,14)
xlabel('Antenna Gain [dB]')
ylabel('Bandwidth [GHz]')
zlabel('Room Size [m^2]')

cb = colorbar;                                     % create and label the colorbar
cb.Label.String = 'Tput [Gbps]';

