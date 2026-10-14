import filecmp

def verify_runs(file_a: str, file_b: str) -> bool:
    is_identical = filecmp.cmp(file_a, file_b)
    print(f"Reproducibility check ({file_a} vs {file_b}): {'PASSED' if is_identical else 'FAILED'}")
    return is_identical