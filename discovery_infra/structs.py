from dataclasses import dataclass
from pathlib import Path
from discovery_infra.consts import NUMBER_OF_MASTERS

@dataclass
class Deployment:
    namespace: str
    profile: str
    storage_pool_path: Path
    namespace_index: int = 0
    master_count: int = NUMBER_OF_MASTERS
    worker_count: int = 0
