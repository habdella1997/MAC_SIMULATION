% clc;
% close all;
% clear;
% bw_range = [15:1:72]; 
% beam_width_range = [0.1 : 1: 50];
% room_radius      = [3:1:20]; % [m] 
% 
% % Step-1 Compute the Antenna Gain Relative to that of the beam-width
% G = 10 .* log10((4*pi) ./ (deg2rad(beam_width_range))); %[dB]
% 
% % Example throughput values (use your tput_results instead)
% tput_results = load("tput7.mat").tput_results;
% t_flat = [];
% g_flat = [];
% bw_flat = [];
% r_flat = [];
% 
% 
% for gain = 1:length(G)
%     disp(gain)
%     for bw = 1:length(bw_range)
%         for rad = 1:length(room_radius)
%             t_val = tput_results(gain,bw,rad);
%             t_val = t_val /1e9;
%               t_flat = [t_flat t_val];
%               g_flat = [g_flat beam_width_range(gain) ];
%               bw_flat = [bw_flat bw_range(bw)];
%               r_flat = [r_flat (2*room_radius(rad))^2];
% %             scatter3(G(gain), bw_range(bw), (2*room_radius(rad))^2, 50,t_val,'filled');
% %             hold on;
%     end
% end
% end
% figure;
% scatter3(g_flat, bw_flat, r_flat, 30,t_flat,'filled');
% 
% % ax = gca;
% % ax.XDir = 'reverse';
% view(-31,14)
% xlabel('Antenna Beanwidth [Degree]')
% ylabel('Bandwidth [GHz]')
% zlabel('Room Size [m^2]')
% 
% cb = colorbar;                                     % create and label the colorbar
% cb.Label.String = 'Tput [G
% bps]';
% 


% MATLAB Script to Simulate a Room and Compute Distance to the Rightmost Corner
% MATLAB Script to Simulate a Room and Compute Distance to the Rightmost Corner

% Parameters for the room (length, width, height)
% Parameters
% Parameters
room_size = 40;       % Room size (40x40 meters)
d_thresh = 5;         % Distance threshold
d_user = 10;          % Distance of the user to the corner
user_x = 30;          % User's x-coordinate
user_y = 0;          % User's y-coordinate

% Define the corner coordinates (you can change these values)
corner_x = 40;         % X-coordinate of the corner
corner_y = 40;         % Y-coordinate of the corner

% Create the grid of coordinates for the room
[x, y] = meshgrid(1:room_size, 1:room_size);

% Calculate the distance from the user's position to the corner
dist_user_to_corner = sqrt((user_x - corner_x)^2 + (user_y - corner_y)^2);

% Calculate the distance from each point in the room to the corner
dist_to_corner = sqrt((x - corner_x).^2 + (y - corner_y).^2);

% Plot the room
figure;
hold on;
axis([0 room_size 0 room_size]);
title('Room Visualization');
xlabel('X Coordinate (meters)');
ylabel('Y Coordinate (meters)');

% Iterate through each point in the room
red_area = 0;
green_area = 0;
for i = 1:room_size
    for j = 1:room_size
        % Compute the distance from the current point to the corner
        d_compute = dist_to_corner(i,j);
        
        % Check if the distance difference is less than or equal to d_thresh
        if abs(d_compute - dist_user_to_corner) <= d_thresh
            % Color red if within threshold
            plot(x(i,j), y(i,j), 'ro');
            red_area = red_area + 1;
        else
            % Color green if outside threshold
            plot(x(i,j), y(i,j), 'go');
            green_area = green_area + 1;
        end
    end
end

% Display the areas
total_area = room_size * room_size;
fprintf('Red Area: %.2f square meters (%.2f%%)\n', red_area, (red_area / total_area) * 100);
fprintf('Green Area: %.2f square meters (%.2f%%)\n', green_area, (green_area / total_area) * 100);

hold off;