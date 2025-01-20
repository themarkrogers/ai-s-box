def parse_s_box_2d_to_1d(s_box_2d):
    """
    Convert a 16x16 array of hex strings into a 1D list of 256 integers.
    s_box_2d[row][col] is a two-hex-digit string, e.g. '63'.
    The index for row,col is: input = (row << 4) ^ col.
    """
    s_box_1d = [0] * 256
    for row in range(16):
        for col in range(16):
            index = (row << 4) ^ col
            val_hex = s_box_2d[row][col]
            s_box_1d[index] = int(val_hex, 16)
    return s_box_1d


def compute_ddt(s_box):
    """
    Compute and return the 256x256 difference distribution table for the given S-box.

    s_box: A list of 256 integers, each in [0..255].
    Returns: A 2D list ddt[a][b].
    """
    size = 256
    # Initialize a 256x256 table of zeros
    ddt = [[0] * size for _ in range(size)]

    # For each possible input difference a
    for a in range(size):
        # For each input x
        for x in range(size):
            # y = x ^ a
            y = x ^ a
            # output difference
            out_diff = s_box[x] ^ s_box[y]
            ddt[a][out_diff] += 1

    return ddt


def differential_uniformity(ddt):
    """
    Compute the maximum value in DDT[a][b] for a != 0.
    """
    max_count = 0
    for a in range(1, 256):  # skip a=0 for differential uniformity
        for b in range(256):
            if ddt[a][b] > max_count:
                max_count = ddt[a][b]
    return max_count


def bit_parity(x):
    """
    Returns the parity of the integer x (number of 1 bits mod 2).
    """
    return bin(x).count("1") % 2


def compute_lat(s_box):
    """
    Compute the Linear Approximation Table (LAT) of size 256x256 for the 8-bit S-box.

    LAT[a][b] = sum_{x=0..255} [(-1)^( (x & a).parity ^ (S(x) & b).parity )].

    s_box: list of 256 integers (8-bit values).
    Returns: A 2D list lat[a][b].
    """
    size = 256
    lat = [[0] * size for _ in range(size)]

    for a in range(size):
        for b in range(size):
            total = 0
            for x in range(size):
                # Dot product mod 2 for input bits
                in_parity = bit_parity(a & x)
                # Dot product mod 2 for output bits
                out_parity = bit_parity(b & s_box[x])
                # (-1)^(in_parity ^ out_parity) => +1 if they match, -1 if they differ
                if in_parity ^ out_parity == 0:
                    total += 1
                else:
                    total -= 1
            lat[a][b] = total
    return lat


def max_linear_correlation(lat):
    """
    Find the maximum absolute correlation in the LAT for a != 0 or b != 0.
    Typically one also excludes the (a=0, b=0) case in the maximum.
    """
    max_corr = 0
    for a in range(256):
        for b in range(256):
            # You can decide whether or not to exclude (a=0,b=0).
            # Commonly, (a=0,b=0) correlation is just 256 because everything matches zero.
            # We'll exclude that from the measure:
            if a == 0 and b == 0:
                continue
            corr = abs(lat[a][b])
            if corr > max_corr:
                max_corr = corr
    return max_corr

def evaluate_s_box(s_box_2d) -> float:
    """
    Given a 16x16 S-box of 2-hex-digit strings (like the AES S-box),
    compute:
      1. Differential uniformity
      2. Maximum absolute linear correlation
      3. (Optional) a combined "score"

    Returns a dict with these values.
    """
    # 1. Parse 2D hex S-box into a flat list of 256 integer values
    s_box_1d = parse_s_box_2d_to_1d(s_box_2d)

    # 2. Compute the DDT and get differential uniformity
    ddt = compute_ddt(s_box_1d)
    diff_uni = differential_uniformity(ddt)

    # 3. Compute the LAT (linear approximation table) and get max correlation
    lat = compute_lat(s_box_1d)
    max_corr = max_linear_correlation(lat)

    # Optionally define a single "score" that combines both.
    # For instance, lower differential uniformity is better, lower max correlation is better.
    # This combination is arbitrary; you can weight them differently.
    # Example: invert both measures and multiply, or some weighted sum.
    # We'll do a simple example:
    #   bigger = worse, so do something like
    #   score = 1 / ((diff_uni + 1) * (max_corr + 1))  # +1 avoids division by zero
    # You can define your own formula.
    combined_score = 1.0 / ((diff_uni + 1) * (max_corr + 1))

    # return {
    #     "differential_uniformity": diff_uni,
    #     "max_linear_correlation": max_corr,
    #     "score": combined_score
    # }
    return combined_score
