# BTN API Service

BTN provides its own API over JSON-RPC. It requires a API key which can be obtained
from going to your profile and clicking the API tab. If you do not already have a key, you
can create a new API key, otherwise use your existing one.

## Config options

Below is a full set of configuration values which are used for the service. You should
only need to update the api_token to have a working service.

    [service_broadcastthenet]
    enabled = true
    url = http://api.btnapps.net/

    ; 32 character API Key.
    api_token = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
