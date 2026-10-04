import requests
import time
import sys

API_URL = "http://localhost:8000/api"
FILE_PATH = "dataset/ServiceNow27kData.xlsx"

def run_benchmark():
    print(f"Uploading {FILE_PATH} to {API_URL}/upload...")
    with open(FILE_PATH, "rb") as f:
        response = requests.post(
            f"{API_URL}/upload",
            files={"file": ("ServiceNow27kData.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
    
    if response.status_code != 200:
        print(f"Failed to upload: {response.text}")
        sys.exit(1)
        
    print("Upload successful, processing started.")
    data = response.json()
    job_id = data.get("job_id")
    print(f"Job ID: {job_id}")
    
    start_time = time.time()
    
    while True:
        try:
            status_res = requests.get(f"{API_URL}/status")
            if status_res.status_code == 200:
                s = status_res.json()
                if s["status"] == "done":
                    print("\nProcessing Complete!")
                    print(s)
                    break
                elif s["status"] == "error":
                    print("\nProcessing Error!")
                    print(s)
                    break
                else:
                    elapsed = time.time() - start_time
                    sys.stdout.write(f"\r[{elapsed:.1f}s] {s['stage']} - {s['percent']}%: {s['message']}")
                    sys.stdout.flush()
        except Exception as e:
            print(f"\nError polling status: {e}")
            break
            
        time.sleep(2)

if __name__ == "__main__":
    run_benchmark()
