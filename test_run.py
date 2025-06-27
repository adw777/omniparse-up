import requests

def parse_document(file_path):
    url="https://vast-prime-weasel.ngrok-free.app/parse_document/pdf"
    # url = "https://xyz.com/parse_document"  # Replace with actual endpoint

    # Open the file in binary mode
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f)}
        try:
            print(f"Uploading {file_path} to {url}...")
            response = requests.post(url, files=files)

            if response.status_code == 200:
                print("\n✅ Parsed Markdown Output:\n")
                print(response.text)  # Assuming API returns Markdown text
            else:
                print(f"\n❌ Failed: Status Code {response.status_code}")
                print("Response:", response.text)

        except Exception as e:
            print("⚠️ Error during request:", str(e))


# Example usage
if __name__ == "__main__":
    # Replace with your actual document path
    document_path = "the-illusion-of-thinking.pdf"
    parse_document(document_path)
