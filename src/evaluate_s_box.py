def compute_ddt(sbox, n_bits, num_output_length: int):
    """Compute XOR-based difference distribution table for a bitwise S-box."""
    size = 2 ** n_bits
    # range size could be up to 2^m
    # We'll index DDT as DDT[input_diff][output_diff].
    # We'll find the maximum possible output_diff by checking the S-box outputs.
    max_sbox_out = max(sbox)
    # but to be safe, let's assume up to 2^num_output_length
    out_size = 2 ** num_output_length

    ddt = [[0] * out_size for _ in range(size)]

    for x in range(size):
        y = sbox[x]
        for dx in range(size):
            x2 = x ^ dx
            y2 = sbox[x2]
            dy = y ^ y2
            ddt[dx][dy] += 1

    return ddt


def compute_walsh_hadamard(sbox, n_in, n_out):
    """Compute the Walsh-Hadamard transform for an n_in->n_out bit S-box."""
    size_in = 2 ** n_in
    size_out = 2 ** n_out

    # We only compute up to the max output observed if it's smaller
    actual_max_out = max(sbox)
    if actual_max_out < size_out - 1:
        size_out = actual_max_out + 1

    # The WHT can be large, so be mindful of performance for big n_in
    # This is a naive implementation.
    wht = {}
    for alpha in range(size_in):
        for beta in range(size_out):
            total = 0
            for x in range(size_in):
                # dot product in GF(2) for alpha, x
                ax = bin(alpha & x).count('1') % 2
                # dot product in GF(2) for beta, sbox[x]
                bs = bin(beta & sbox[x]).count('1') % 2
                # exponent
                exponent = ax ^ bs
                # (-1)^exponent is +1 if exponent=0, -1 if exponent=1
                total += (1 if exponent == 0 else -1)
            wht[(alpha, beta)] = total

    return wht


def is_bent(n_in, n_out, max_corr):
    if n_in % 2 != 0:
        return False
    # the classical definition: n_out = n_in/2
    if n_out * 2 != n_in:
        return False
    # bent => max absolute WHT = 2^(n/2) (i.e. half the input bits)
    # but we used a sum from -1 to +1. The "peak" for a perfectly bent function
    # is 2^(n/2). Normalized correlation would then be 2^(n/2) / 2^n = 2^(-n/2).
    # So if max_corr (non-normalized) = 2^(n/2), that means normalized is 2^(-n/2).
    expected_non_normalized = 2 ** (n_in // 2)
    actual_non_normalized = max_corr * (2 ** n_in)
    return abs(actual_non_normalized - expected_non_normalized) < 1e-9


def evaluate_s_box(
    s_box: list[list[str]],
    num_input_length: int,
    num_output_length: int,
    num_unique_symbols: int
) -> dict:
    """
    Evaluate and score an S-box based on:
      1) Difference Distribution Table (DDT) & differential uniformity
      2) Walsh–Hadamard Transform (WHT) & linear correlation
      3) Bent function check (if n->n/2 bits)

    :param s_box: 2D array of output symbols. Dimensions depend on how the S-box was generated.
    :param num_input_length: number of bits in the input
    :param num_output_length: number of bits in the output
    :param num_unique_symbols: total unique symbols possible in the output alphabet
    :return: A dictionary of evaluation metrics
    """

    # -------------------------------------------------------------------------
    # 1. Flatten the S-box into a single list sbox_list, where
    #    sbox_list[x] = integer output for input x.
    #
    #    We'll assume the 2D array is row-major so that:
    #       input = row * (number_of_columns) + column
    #    is the index of that output.
    #
    #    If your S-box is arranged differently (like DES), you may need to
    #    adapt the flattening logic accordingly.
    # -------------------------------------------------------------------------
    flat_sbox = []
    row_count = len(s_box)
    col_count = len(s_box[0])

    # A dictionary to store 'seen_symbol -> assigned_int'
    symbol_to_int = {}
    next_id = 0

    for row in range(row_count):
        for col in range(col_count):
            symbol = s_box[row][col]

            # Try to parse as hex
            # e.g. '9f', '7c', ...
            try:
                value = int(symbol, 16)
            except ValueError:
                # If that fails, try binary
                # e.g. '0010', '1110', ...
                try:
                    value = int(symbol, 2)
                except ValueError:
                    # Otherwise, map any arbitrary string/emoji
                    if symbol not in symbol_to_int:
                        symbol_to_int[symbol] = next_id
                        next_id += 1
                    value = symbol_to_int[symbol]

            flat_sbox.append(value)

    domain_size = row_count * col_count  # total number of inputs found
    sbox_list = flat_sbox

    # Quick check: does domain_size match 2^(num_input_length)?
    # This is the standard assumption for an n-bit S-box.
    expected_domain_size = 2 ** num_input_length
    domain_consistency = (domain_size == expected_domain_size)

    # Also figure out the largest integer in sbox_list to gauge the range
    max_output_value = max(sbox_list) if sbox_list else 0
    # Potential range size is max_output_value+1, but let's see if it is 2^(num_output_length)
    expected_range_size = 2 ** num_output_length
    range_consistency = (max_output_value < expected_range_size)

    # -------------------------------------------------------------------------
    # 2. Compute the Difference Distribution Table (DDT)
    #    We'll only do standard XOR-based DDT if domain_size == 2^num_input_length.
    # -------------------------------------------------------------------------
    ddt = None
    max_ddt_entry = 0
    if domain_consistency:
        ddt = compute_ddt(sbox_list, num_input_length, num_output_length)
        # For differential uniformity, we often look at the max count
        # of nonzero input difference dx != 0.
        max_ddt_entry = max(
            ddt[dx][dy]
            for dx in range(1, len(ddt))  # skip dx=0 in some definitions
            for dy in range(len(ddt[dx]))
        )
    else:
        # If we cannot do standard XOR-based, we skip or do a fallback.
        pass

    # -------------------------------------------------------------------------
    # 3. Compute the Walsh-Hadamard Transform (WHT) to measure linear correlation
    #
    #    W(α, β) = sum over x of (-1)^( <α,x> XOR <β,S(x)> ).
    #    For each α in [0..(2^n-1)], β in [0..(2^m-1)].
    #
    #    The largest absolute value (in magnitude) corresponds to the "worst-case"
    #    linear approximation. Normalized by domain_size, that is your max correlation.
    # -------------------------------------------------------------------------
    wht = None
    max_linear_correlation = None
    if domain_consistency and range_consistency:
        wht = compute_walsh_hadamard(sbox_list, num_input_length, num_output_length)
        # max absolute correlation:
        max_correlation = max(abs(v) for v in wht.values()) if wht else 0
        # Normalized by the domain size:
        max_linear_correlation = max_correlation / (2 ** num_input_length)
    else:
        # Not well-defined if input or output domain isn't a standard 2^n
        pass

    # -------------------------------------------------------------------------
    # 4. Bent function check
    #
    #    A function f : {0,1}^n -> {0,1}^{m} is "bent" in the classical sense only if:
    #       - n is even
    #       - m = n/2
    #       - The Walsh spectrum is flat (all nonzero freq have magnitude 2^(n/2)).
    #
    #    We do a simple check: if (n, m) fits that pattern and the maximum correlation
    #    has absolute value = 2^(n/2), then it is bent. (For multi-bit output, the concept
    #    typically references each coordinate function. But here is a simplified approach.)
    # -------------------------------------------------------------------------
    bent_flag = False
    if max_linear_correlation is not None:
        bent_flag = is_bent(num_input_length, num_output_length, max_linear_correlation)

    # 5. Synthesize
    results = {
        "domain_size": domain_size,
        "expected_domain_size": expected_domain_size,
        "domain_consistency": domain_consistency,
        "range_consistency": range_consistency,
        "max_ddt_entry": max_ddt_entry if ddt else None,
        "max_linear_correlation": max_linear_correlation,
        "is_bent": bent_flag,
    }

    return results
