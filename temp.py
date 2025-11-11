import tempfile
import subprocess

def get_alsa_hw_params(device_name):
    """
    Dumps ALSA hardware parameters for a given device to a temporary file,
    then parses bit depths and sample rates.
    """
    with tempfile.NamedTemporaryFile(mode='w+', delete=True) as tmp:
        try:
            # Dump hardware params to the temp file
            result = subprocess.run(
                ["arecord", "--dump-hw-params", "-D", device_name],
                stdout=tmp,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            tmp.seek(0)
            bit_depths = set()
            sample_rates = set()
            for line in tmp:
                if "FORMAT:" in line:
                    # Example: FORMAT: S16_LE, S24_LE, S32_LE
                    formats = line.split(":", 1)[1].strip().split(",")
                    for fmt in formats:
                        fmt = fmt.strip()
                        if "S16" in fmt:
                            bit_depths.add(16)
                        elif "S24" in fmt:
                            bit_depths.add(24)
                        elif "S32" in fmt:
                            bit_depths.add(32)
                elif "RATE:" in line:
                    # Example: RATE: [8000 48000]
                    rates = re.findall(r'\d+', line)
                    for rate in rates:
                        sample_rates.add(int(rate))
            return sorted(bit_depths), sorted(sample_rates)
        except Exception as e:
            print(f"Error querying ALSA hw params: {e}")
            return [], []