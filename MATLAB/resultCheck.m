% ========================================================================
%  check_handshake.m
%
%  Verifies a CTA‑RTS‑CTS‑DATA‑ACK THz/µ‑wave uplink handshake and
%  computes end‑to‑end latency + throughput for one UE.
%
%  INPUT  ▸ fill the “USER PARAMETERS” section or load them from a .mat / csv
%  OUTPUT ▸ 1) table showing expected vs measured arrival times
%           2) latency and throughput numbers printed to console
% ========================================================================

clear, clc

%% ─────────────────────────── USER PARAMETERS ──────────────────────────
% ▼ replace with your real values or load from file ----------------------
c                 = 3e8;                 % speed of light  [m/s]

% ❶ physical + MAC parameters
ctrlRate      = 6.912e9;    %   Control‑packet PHY rate       [bit/s]
ctrlLen       = 208  ;      %   CTRL pkt length (e.g. 128 B)   [bit]
dataRate      = 131.328e9;  %   Uplink data rate              [bit/s]
dataLen       = 546144;     %   DATA pkt length  (e.g. 2 kB)   [bit]
distance2AP   = 43.5541;    %   UE ↔ AP distance              [m]

% ❷ timestamps  (all in **seconds** – use unix‑epoch or sim‑time)
ts = struct(...
    'CTA_tx',  0.001026,               'CTA_rx',  0.001026, ...
    'RTS_tx',  0.0010279536967361012,  'RTS_rx',  0.0010281290702780033, ...
    'CTS_tx',  0.0010281290702780033,  'CTS_rx',  0.0010283044438199054, ...
    'DATA_tx', 0.0010283044438199054,  'DATA_rx', 0.0010326083505002091, ...
    'ACK_tx',  0.0010326083505002091,  'ACK_rx',  0.0010327837240421112 );

UL_grant_slot = [0.0010283044438199054  , 4.158625730994152e-06+0.0010283044438199054];      % [start , end]  (s)
% ------------------------------------------------------------------------

%% helper lambdas
propDelay  = @(d) d / c;          % d [m] → delay [s]
txDelay    = @(len,rate) len / rate;

%% expected delays
d_prop  = propDelay(distance2AP);
d_ctrl  = txDelay(ctrlLen , ctrlRate);
d_data  = txDelay(dataLen , dataRate);

%% build an info table ---------------------------------------------------
names    = {'CTA','RTS','CTS','DATA','ACK'}';
tx_len   = [ctrlLen ctrlLen ctrlLen dataLen ctrlLen]';
tx_rate  = [ctrlRate ctrlRate ctrlRate dataRate ctrlRate]';
tx_delay = tx_len ./ tx_rate;
exp_arr  = struct2array(rmfield(ts,{'CTA_tx','RTS_tx','CTS_tx','DATA_tx','ACK_tx'})) ...
         + 0; % placeholder

% compute expected arrival time for each hop
exp_arr(1) = ts.CTA_tx  + tx_delay(1) + d_prop;   % CTA DL
exp_arr(2) = ts.RTS_tx  + tx_delay(2) + d_prop;   % RTS UL
exp_arr(3) = ts.CTS_tx  + tx_delay(3) + d_prop;   % CTS DL
exp_arr(4) = ts.DATA_tx + tx_delay(4) + d_prop;   % DATA UL
exp_arr(5) = ts.ACK_tx  + tx_delay(5) + d_prop;   % ACK  DL

meas_arr = [ts.CTA_rx ts.RTS_rx ts.CTS_rx ts.DATA_rx ts.ACK_rx]';

T = table(names , tx_delay , repmat(d_prop,5,1) , exp_arr' , meas_arr , ...
          'VariableNames',{'Pkt','TxDelay_s','PropDelay_s', ...
                           'Arr_expect_s','Arr_meas_s'});

disp('──────────────────────── Expected vs Measured ───────────────────────')
disp(T)

%% simple correctness check (|error| ≤ 2 µs)
tol = 2e-10;
if all(abs(T.Arr_meas_s - T.Arr_expect_s) < tol)
    disp('✅ All arrival times within tolerance.');
else
    warn = abs(T.Arr_meas_s - T.Arr_expect_s) >= tol;
    fprintf('❌ Mismatch in packets: %s\n', strjoin(T.Pkt(warn),', '))
end

%% latency & throughput --------------------------------------------------
e2e_latency = ts.ACK_rx - 0.00102793826025695;        % total handshake time
ul_databits = dataLen;                      % one UL DATA packet
throughput  = ul_databits / e2e_latency;    % bit/s

fprintf('\n── Results ─────────────────────────────────────────\n')
fprintf('End‑to‑end latency : %.10f ms\n', e2e_latency*1e3)
fprintf('Throughput        : %.2f Mbps\n', throughput/1e6)

%% optional: verify DATA tx lies inside the UL‑grant slot
insideSlot = (ts.DATA_tx >= UL_grant_slot(1)) && ...
             (ts.DATA_tx + d_data <= UL_grant_slot(2));
if ~insideSlot
    warning('UL‑DATA transmission falls outside its grant slot!')
end
