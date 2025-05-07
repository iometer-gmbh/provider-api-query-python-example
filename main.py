import asyncio
import logging
import signal
import sys

from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport

def signal_handler(signum, frame):
    sys.exit()

async def get_readings():
    transport = HTTPXAsyncTransport(url="https://provider-api.prod.iometer.cloud/v1/query",
                                    headers={
                                        'authorization': 'Basic YOUR_API_TOKEN_HERE'
                                    },
                                    timeout=60
                                    )
    async with Client(
            transport=transport,
            execute_timeout=60,
            fetch_schema_from_transport=True,
    ) as session:
        cursor = None
        query = gql(
            """
           query GetReadings ($startTime: DateTime, $cursor: String) {
              provider {
                readings (startTime: $startTime, limit:25, cursor: $cursor) {
                  cursor
                  readings {
                    receiveTime
                    time
                    meter {
                      number
                    }
                    installation {
                      id
                      externalId
                    }
                    values {
                      obisCode
                      unit
                      value
                    }
                  }
                }
              }
            }
        """
        )
        while True:
            params = {
                #"startTime": "2025-05-07T00:00:00Z",
                "cursor": cursor,
            }
            try:
                results = await session.execute(query, variable_values=params)
                print(results)
                cursor = results["provider"]["readings"]["cursor"]
                if cursor is None:
                    break
            except Exception as e:
                logging.error(e)
                break


logging.basicConfig(level=logging.ERROR)
signal.signal(signal.SIGINT, signal_handler)
asyncio.run(get_readings())
