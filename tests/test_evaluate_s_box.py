from src.evaluate_s_box import evaluate_s_box


def test_evaluate_s_box_with_aes():
    # AES example (short version): 16x16 = 256 entries
    # The comment "# num_input_length=2" in your snippet is presumably not "bits" in the
    # classical sense for AES. True AES S-box is 8-bit in, 8-bit out.
    # We'll override to 8,8 to show standard usage:
    aes_s_box = [
        ["63", "7c", "77", "7b", "f2", "6b", "6f", "c5", "30", "01", "67", "2b", "fe", "d7", "ab", "76"],
        ["ca", "82", "c9", "7d", "fa", "59", "47", "f0", "ad", "d4", "a2", "af", "9c", "a4", "72", "c0"],
        ["b7", "fd", "93", "26", "36", "3f", "f7", "cc", "34", "a5", "e5", "f1", "71", "d8", "31", "15"],
        ["04", "c7", "23", "c3", "18", "96", "05", "9a", "07", "12", "80", "e2", "eb", "27", "b2", "75"],
        ["09", "83", "2c", "1a", "1b", "6e", "5a", "a0", "52", "3b", "d6", "b3", "29", "e3", "2f", "84"],
        ["53", "d1", "00", "ed", "20", "fc", "b1", "5b", "6a", "cb", "be", "39", "4a", "4c", "58", "cf"],
        ["d0", "ef", "aa", "fb", "43", "4d", "33", "85", "45", "f9", "02", "7f", "50", "3c", "9f", "a8"],
        ["51", "a3", "40", "8f", "92", "9d", "38", "f5", "bc", "b6", "da", "21", "10", "ff", "f3", "d2"],
        ["cd", "0c", "13", "ec", "5f", "97", "44", "17", "c4", "a7", "7e", "3d", "64", "5d", "19", "73"],
        ["60", "81", "4f", "dc", "22", "2a", "90", "88", "46", "ee", "b8", "14", "de", "5e", "0b", "db"],
        ["e0", "32", "3a", "0a", "49", "06", "24", "5c", "c2", "d3", "ac", "62", "91", "95", "e4", "79"],
        ["e7", "c8", "37", "6d", "8d", "d5", "4e", "a9", "6c", "56", "f4", "ea", "65", "7a", "ae", "08"],
        ["ba", "78", "25", "2e", "1c", "a6", "b4", "c6", "e8", "dd", "74", "1f", "4b", "bd", "8b", "8a"],
        ["70", "3e", "b5", "66", "48", "03", "f6", "0e", "61", "35", "57", "b9", "86", "c1", "1d", "9e"],
        ["e1", "f8", "98", "11", "69", "d9", "8e", "94", "9b", "1e", "87", "e9", "ce", "55", "28", "df"],
        ["8c", "a1", "89", "0d", "bf", "e6", "42", "68", "41", "99", "2d", "0f", "b0", "54", "bb", "16"],
    ]
    # ToDo, it should be possible to infer the input_length, output_length, and num_unique_symbols from the s_box
    aes_metrics = evaluate_s_box(
        s_box=aes_s_box,
        num_input_length=8,  # AES uses 8-bit inputs
        num_output_length=8,  # AES uses 8-bit outputs
        num_unique_symbols=16,  # (this is the base 16 representation, but not crucial here)
    )
    print("AES S-box evaluation:")
    for k, v in aes_metrics.items():
        print(f"  {k}: {v}")

    print("\n")

    # DES example (short snippet). The real DES has 8 S-boxes, each 6->4 bits,
    # but let's just show how the flattening might work with your example:
    des_s_box = [
        [
            "0010",
            "1100",
            "0100",
            "0001",
            "0111",
            "1010",
            "1011",
            "0110",
            "1000",
            "0101",
            "0011",
            "1111",
            "1101",
            "0000",
            "1110",
            "1001",
        ],
        [
            "1110",
            "1011",
            "0010",
            "1100",
            "0100",
            "0111",
            "1101",
            "0001",
            "0101",
            "0000",
            "1111",
            "1010",
            "0011",
            "1001",
            "1000",
            "0110",
        ],
        [
            "0100",
            "0010",
            "0001",
            "1011",
            "1010",
            "1101",
            "0111",
            "1000",
            "1111",
            "1001",
            "1100",
            "0101",
            "0110",
            "0011",
            "0000",
            "1110",
        ],
        [
            "1011",
            "1000",
            "1100",
            "0111",
            "0001",
            "1110",
            "0010",
            "1101",
            "0110",
            "1111",
            "0000",
            "1001",
            "1010",
            "0100",
            "0101",
            "0011",
        ],
    ]
    des_metrics = evaluate_s_box(
        s_box=des_s_box,
        num_input_length=6,  # typical for DES S-box input
        num_output_length=4,  # typical for DES S-box output
        num_unique_symbols=2,  # they're binary strings, so base=2 representation
    )
    print("DES S-box evaluation:")
    for k, v in des_metrics.items():
        print(f"  {k}: {v}")
