# API Standards

## Versioning
### Rules:

1. Use /v1 as prefix in module level routers, and same naming convention
Example:
```bash
from fastapi import APIRouter

route_name_v1_route = APIRouter(prefix="/v1", tags=["Route_name v1"])
```

2. When a module gains a new version, add a new APIRouter in the same file following the same naming convention (e.g. route_name_v2_route).