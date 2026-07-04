# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

calendar_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@cocal/google-calendar-mcp"],
            env={
                "GOOGLE_OAUTH_CREDENTIALS": os.getenv(
                    "GOOGLE_OAUTH_CREDENTIALS",
                    os.path.abspath(
                        os.path.join(
                            os.path.dirname(__file__),
                            "../gcp-oauth.keys.json",
                        )
                    ),
                ),
                "PATH": os.getenv("PATH", ""),  # npx needs PATH to locate node/npm
            },
        ),
    ),
)
