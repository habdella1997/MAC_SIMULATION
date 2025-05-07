% Settings
room_size = 16;         % 16x16 meters
num_samples = 1e5;      % number of uniformly placed UEs
distance_MCS = [93, 51, 42, 20];  % in meters
nlos_range = 5:1:50;    % possible NLoS path lengths

% Simulate random nodes uniformly
x = rand(num_samples,1) * room_size;
y = rand(num_samples,1) * room_size;

% Assign NLoS distance randomly from [5,50]
nlos_dists = datasample(nlos_range, num_samples);

% Initialize bins
mcs_bins = zeros(4,1);

% Count number of nodes in each MCS bin
mcs_bins(1) = sum(nlos_dists > distance_MCS(2) & nlos_dists <= distance_MCS(1));  % MCS 1
mcs_bins(2) = sum(nlos_dists > distance_MCS(3) & nlos_dists <= distance_MCS(2));  % MCS 2
mcs_bins(3) = sum(nlos_dists > distance_MCS(4) & nlos_dists <= distance_MCS(3));  % MCS 3
mcs_bins(4) = sum(nlos_dists <= distance_MCS(4));                                 % MCS 4

% Normalize to probability
mcs_probs = mcs_bins / num_samples;

% Display
fprintf('Probability per MCS bin:\n');
for i = 1:4
    fprintf('MCS %d: %.2f%%\n', i, mcs_probs(i) * 100);
end
