from fixinventorydata.utils import LazyLoadedDict


regions = LazyLoadedDict("regions.json")
instances = LazyLoadedDict("instances.json")

instances2ccfmap = {
    "aws": {
        "cpu": {
            "AMD EPYC 7571": "AMD EPYC 1st Gen",
            "AMD EPYC 7R13 Processor": "AMD EPYC 3rd Gen",
            "AMD EPYC 7R32": "AMD EPYC 2nd Gen",
            "AWS Graviton Processor": None,
            "AWS Graviton2 Processor": "AWS Graviton2",
            "AWS Graviton3 Processor": None,
            "Apple M1 chip with 8-core CPU, 8-core GPU, and 16-core Neural Engine": "",
            "High Frequency Intel Xeon E7-8880 v3 (Haswell)": "Haswell",
            "Intel Core i7-8700B CPU": "Coffee Lake",
            "Intel Skylake E5 2686 v5": "Skylake",
            "Intel Xeon 8375C (Ice Lake)": None,
            "Intel Xeon E5-2650": "Sandy Bridge",
            "Intel Xeon E5-2666 v3 (Haswell)": "Haswell",
            "Intel Xeon E5-2670": "Sandy Bridge",
            "Intel Xeon E5-2670 (Sandy Bridge)": "Sandy Bridge",
            "Intel Xeon E5-2670 v2 (Ivy Bridge)": "Ivy Bridge",
            "Intel Xeon E5-2670 v2 (Ivy Bridge/Sandy Bridge)": "Ivy Bridge",
            "Intel Xeon E5-2676 v3 (Haswell)": "Haswell",
            "Intel Xeon E5-2680 v2 (Ivy Bridge)": "Ivy Bridge",
            "Intel Xeon E5-2686 v4 (Broadwell)": "Broadwell",
            "Intel Xeon Family": None,
            "Intel Xeon Platinum 8124M": "Skylake",
            "Intel Xeon Platinum 8151": "Skylake",
            "Intel Xeon Platinum 8175": "Skylake",
            "Intel Xeon Platinum 8175 (Skylake)": "Skylake",
            "Intel Xeon Platinum 8252": "Cascade Lake",
            "Intel Xeon Platinum 8259 (Cascade Lake)": "Cascade Lake",
            "Intel Xeon Platinum 8259CL": "Cascade Lake",
            "Intel Xeon Platinum 8275CL (Cascade Lake)": "Cascade Lake",
            "Intel Xeon Platinum 8275L": "Cascade Lake",
            "Intel Xeon Platinum 8280L (Cascade Lake)": "Cascade Lake",
            "Intel Xeon Scalable (Icelake)": None,
            "Intel Xeon Scalable (Skylake)": "Skylake",
        },
        "gpu": {
            "AMD Radeon Pro V520": "AMD Radeon Pro V520",
            "NVIDIA A100": "Nvidia Tesla A100",
            "NVIDIA A10G": "Nvidia A10G",
            "NVIDIA GRID K520": "Nvidia K520",
            "NVIDIA T4 Tensor Core": "Nvidia T4",
            "NVIDIA T4G Tensor Core": "Nvidia T4",
            "NVIDIA Tesla K80": "Nvidia Tesla K80",
            "NVIDIA Tesla M60": "Nvidia Tesla M60",
            "NVIDIA Tesla V100": "Nvidia Tesla V100",
        },
    }
}
