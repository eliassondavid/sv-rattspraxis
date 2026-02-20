# Copyright 2026 David Eliasson
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
sv-rattspraxis: Harvester & RAG-pipeline för svensk rättspraxis.

Mer information: https://github.com/eliassondavid/sv-rattspraxis
"""

__version__ = "0.1.0"
__author__ = "David Eliasson"
__license__ = "Apache-2.0"

from sv_rattspraxis.api_client import APIClient
from sv_rattspraxis.models import MasterListEntry, Publication

__all__ = [
    "APIClient",
    "Publication",
    "MasterListEntry",
    "__version__",
]
