"""
WEOS Backend Entry Point
Version: 0.2.0
"""

import uvicorn
from app.api import app


def main():
    print("===================================")
    print(" WEOS Backend")
    print(" Version : 0.2.0")
    print(" Status  : Starting...")
    print("===================================")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )


if __name__ == "__main__":
    main()
