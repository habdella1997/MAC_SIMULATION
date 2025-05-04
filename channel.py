import math
import constants as C
import numpy as np
import math_toolkit

NF_mixer = 5
NF_LNA = 1
G_LNA = 14
L_mixer = 5
L_misc = 0
NF = 6


def freq_2_lambda(f):
    return C.SPEED_OF_LIGHT / f

def max_distance(p_tx, bandwidth, antenna_gain,ue_gain, f_c):
    ebn0_qpsk = 10.6 #BER 10^-6
    beff_qpsk = 2
    
    snr_needed = ebn0_qpsk - 10*math.log10(1/beff_qpsk)
    P_n = 10 * math.log10(C.BOLTZMAN * C.T * bandwidth)
    Noise = P_n + NF
    
    p_rx = snr_needed + Noise
    L_total = p_tx + antenna_gain + ue_gain - p_rx
    spreading_loss_needed = L_total - L_misc - 2*L_mixer

    return (10**(spreading_loss_needed/20)*freq_2_lambda(f_c)) / (4*math.pi)




def link_budget(p_tx, distance, max_bandwidth, antenna_gain, f_c, abs_loss): #verified - hussam
    p_tx = 10 * math.log10(p_tx)
    lambda_fc = C.SPEED_OF_LIGHT / f_c

    spreading_loss = 20 * math.log10((4 * math.pi * distance) / lambda_fc)
    L_total = 2*L_mixer + L_misc + abs_loss + spreading_loss


    #NF = 10 * math.log10(10 ** (NF_mixer / 10) + (10 ** (NF_LNA / 10) - 1) / 10 ** (G_LNA / 10))
    
    NF = 10 * math.log10(10 ** (NF_LNA / 10) + (10 ** (NF_mixer / 10) - 1) / 10 ** (G_LNA / 10))


    modulation_table =     [ "QPSK"   , "8-PSK"  , "16-QAM" , "64-QAM" ]
    B_efficiencies = [ 2   , 3  , 4    , 6   ]
    Eb_N0_min      = [ 10.6, 14 , 14.5 , 18.8]

    data_rate         = None
    max_data_rate     = 0
    modulation_scheme = None

    P_n  = 10 * math.log10(C.BOLTZMAN * C.T * (max_bandwidth)) + 30 #[dBm]
    p_rx = (p_tx + antenna_gain + G_LNA) - L_total

    SNR_Computed  = p_rx - (P_n + NF)

    for i in range(len(B_efficiencies)):
        EbNo_computed = SNR_Computed - (10 * math.log10(B_efficiencies[i]))
        if(EbNo_computed >= Eb_N0_min[i]):
            data_rate = (max_bandwidth * B_efficiencies[i]) 
            if data_rate > max_data_rate:
                max_data_rate = data_rate
                modulation_scheme = modulation_table[i]
    return p_rx, max_data_rate, SNR_Computed, modulation_scheme


# p_tx and p_rx in dBm!!!
def rx_power(p_tx, distance, f_c, g_tx, l_abs=0, g_rx=None):
    if g_rx is None:
        g_rx = g_tx

    lambda_fc = C.SPEED_OF_LIGHT / f_c
    l_spreading = 20 * math.log10((4 * math.pi) / lambda_fc * distance)

    p_rx = p_tx + g_tx - l_spreading - l_abs + g_rx
    return p_rx


def snr(p_tx, distance, f_c, g_tx, bw, T, l_abs=0, g_rx=None, nf=0):
    p_rx = rx_power(p_tx, distance, f_c, g_tx, l_abs, g_rx)
    p_n = 10 * np.log10(C.BOLTZMAN * T * bw)
    snr = p_rx - p_n - nf
    return snr

def compute_BERQPSK(eb_n0):
    print(eb_n0)
    return math_toolkit.Q_function(math.sqrt(2*(eb_n0)))

def compute_propagationDelay(d):
    return d/C.SPEED_OF_LIGHT

def compute_transmissionTime(packet_length, bit_rate):
    return packet_length / bit_rate



def compute_propabilityLoS_indoorMixed(distance):
    if distance <= 1.2:
        return 1
    if distance < 6.5 and distance > 1.2:
        return math.exp( -1*(distance-1.2) / (4.7))
    else:
        return math.exp(-1*(distance-6.5) / (32.6)) * 0.32
    
