RTS_timeSlots_requested = [5, 2, 8, 1, 7]
UEID_requested = ['A', 'B', 'C', 'D', 'E']
dataRates_requested = [10, 20, 30, 40, 50]
propDelay_forRequest = [0.1, 0.2, 0.3, 0.4, 0.5]
timeStamp_forRequest = [100, 200, 300, 400, 500]

# Combine all lists into a single structure for sorting
combined = list(zip(RTS_timeSlots_requested, UEID_requested, dataRates_requested, 
                    propDelay_forRequest, timeStamp_forRequest))

# Sort the combined data by RTS_timeSlots_requested (first element of the tuple)
combined_sorted = sorted(combined, key=lambda x: x[0])

# Unpack the sorted combined data back into separate lists
RTS_timeSlots_requested, UEID_requested, dataRates_requested, propDelay_forRequest, timeStamp_forRequest = zip(*combined_sorted)

# Convert back to lists (if needed)
RTS_timeSlots_requested = list(RTS_timeSlots_requested)
UEID_requested = list(UEID_requested)
dataRates_requested = list(dataRates_requested)
propDelay_forRequest = list(propDelay_forRequest)
timeStamp_forRequest = list(timeStamp_forRequest)

# Print the results
print("Sorted RTS_timeSlots_requested:", RTS_timeSlots_requested)
print("Sorted UEID_requested:", UEID_requested)
print("Sorted dataRates_requested:", dataRates_requested)
print("Sorted propDelay_forRequest:", propDelay_forRequest)
print("Sorted timeStamp_forRequest:", timeStamp_forRequest)