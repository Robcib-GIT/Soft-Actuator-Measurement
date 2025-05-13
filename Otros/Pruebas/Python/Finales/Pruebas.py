if __name__ == '__main__':
    hist = [0, 0, 0, 60, 0, 6, 0, 7, 4, 6, 5]
    # hist = [0, 0, 0, 6, 6, 0, 7, 4, 6, 5]

    print(hist)
    idx_bins_range = (None, None)
    max_peaks_count = 0
    current_start = None
    current_peaks_count = 0
    max_bins = 3

    for i, freq in enumerate(hist):
        if freq > 0:
            if current_start is None:
                current_start = i

            if (i - current_start) == max_bins:
                current_peaks_count += (freq - hist[current_start])
                current_start += 1
            else:
                current_peaks_count += freq

            print(f"Hist: {str(hist[current_start:i+1]):<10}    |   count: {current_peaks_count:<4}   |    range({current_start:>2}, {i:>2})")
            if current_peaks_count > max_peaks_count:
                max_peaks_count = current_peaks_count
                idx_bins_range = (current_start, i)

        else:
            current_start = None
            current_peaks_count = 0

    print(f"Concentración máxima entre: {idx_bins_range[0]} - {idx_bins_range[1]}")
