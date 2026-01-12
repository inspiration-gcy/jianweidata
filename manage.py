import argparse
import os
import uvicorn
from app.database import db

def load_data_only(directory):
    """
    Test loading data from the directory without starting the web server.
    Useful for verifying data integrity and loading logic.
    """
    print(f"--- Testing Data Load from {directory} ---")
    if not os.path.exists(directory):
        print(f"Error: Directory {directory} does not exist.")
        return
        
    try:
        db.load_from_directory(directory)
        print("--- Data Load Successful ---")
        # Since we moved to database queries, these attributes no longer exist on the db object.
        # We can just print a success message.
    except Exception as e:
        print(f"--- Data Load Failed ---")
        print(e)

def start_server(directory, host, port, reload):
    """
    Start the FastAPI server with the specified data directory.
    """
    # Set environment variable so manual load trigger can pick it up
    os.environ["DATA_DIR"] = directory
    
    print(f"--- Starting Server ---")
    print(f"Data Directory Configured: {directory}")
    print(f"Address: http://{host}:{port}")
    
    uvicorn.run("app.api:app", host=host, port=port, reload=reload)

def main():
    parser = argparse.ArgumentParser(description="Jianwei Data Manager")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Command: load
    # Usage: python manage.py load --dir /path/to/data
    load_parser = subparsers.add_parser("load", help="Load data from directory into database")
    load_parser.add_argument("--dir", default="/Users/bytedance/pycodes/jianweidata/data", help="Data directory path")

    # Command: start
    # Usage: python manage.py start --dir /path/to/data --port 8000
    start_parser = subparsers.add_parser("start", help="Start the API server")
    start_parser.add_argument("--dir", default="/Users/bytedance/pycodes/jianweidata/data", help="Data directory path")
    start_parser.add_argument("--host", default="0.0.0.0", help="Host address")
    start_parser.add_argument("--port", type=int, default=8000, help="Port number")
    start_parser.add_argument("--reload", action="store_true", help="Enable auto-reload (dev mode)")

    args = parser.parse_args()

    if args.command == "load":
        load_data_only(args.dir)
    elif args.command == "start":
        start_server(args.dir, args.host, args.port, args.reload)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
