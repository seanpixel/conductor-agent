import uvicorn
import os
import sys
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Conductor Agent API server.')
    parser.add_argument('--load-test-data', dest='load_test_data', action='store_true',
                        help='Load test data into the system before starting')
    args = parser.parse_args()
    
    if args.load_test_data:
        print("Loading test data...")
        from test_data import load_test_data
        org, conductor = load_test_data()
        
        # Update the main app's organization and conductor
        from app.main import set_organization_and_conductor
        set_organization_and_conductor(org, conductor)
        
        print("Test data loaded successfully.")
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)