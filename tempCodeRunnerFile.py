import cv2
import os

# Load base image (carrier)
img = cv2.imread("cat_img.jpg.webp")  # Update this path accordingly
if img is None:
    print("Error: Carrier image not found.")
    exit()

# Encoding dictionaries
d = {chr(i): i for i in range(256)}
c = {i: chr(i) for i in range(256)}

def embed_message(img, msg):
    """Embed a text message into an image."""
    n, m, z = 0, 0, 0
    for char in msg:
        img[n, m, z] = d[char]
        z = (z + 1) % 3
        if z == 0:
            m += 1
        if m >= img.shape[1]:
            m = 0
            n += 1
        if n >= img.shape[0]:
            raise ValueError("Message too long to embed in the image.")
    return img

def embed_binary_file(img, file_path, start_pixel=(100, 100)):
    """Embed binary data from a file into an image."""
    with open(file_path, "rb") as f:
        file_data = f.read()
    length = len(file_data)
    length_bytes = length.to_bytes(4, byteorder='big')  # Store file length in first 4 bytes

    n, m = start_pixel
    z = 0
    for byte in length_bytes + file_data:
        img[n, m, z] = byte
        z = (z + 1) % 3
        if z == 0:
            m += 1
        if m >= img.shape[1]:
            m = 0
            n += 1
        if n >= img.shape[0]:
            raise ValueError("File too large to embed in the image.")
    return img

def extract_binary_file(img, output_path, start_pixel=(100, 100)):
    """Extract binary data from an image and save it to a file."""
    n, m = start_pixel
    z = 0

    # Extract the length of the file (4 bytes)
    length_bytes = bytearray()
    for _ in range(4):
        length_bytes.append(img[n, m, z])
        z = (z + 1) % 3
        if z == 0:
            m += 1
        if m >= img.shape[1]:
            m = 0
            n += 1
    file_length = int.from_bytes(length_bytes, byteorder='big')

    # Extract the file data
    byte_data = bytearray()
    for _ in range(file_length):
        byte_data.append(img[n, m, z])
        z = (z + 1) % 3
        if z == 0:
            m += 1
        if m >= img.shape[1]:
            m = 0
            n += 1

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(byte_data)

# --- USER INTERFACE ---
print("Choose an option:")
print("1. Hide Message")
print("2. Hide PDF")
print("3. Hide Image")
print("4. Hide Video")
choice = input("Enter choice (1/2/3/4): ")

password = input("Enter a passcode: ")

if choice == "1":
    msg = input("Enter secret message: ")
    img = embed_message(img, msg)

elif choice == "2":
    file_path = input("Enter path to PDF file: ")
    if not os.path.exists(file_path):
        print("Error: PDF file not found.")
        exit()
    img = embed_binary_file(img, file_path, start_pixel=(100, 100))

elif choice == "3":
    file_path = input("Enter path to IMAGE file: ")
    if not os.path.exists(file_path):
        print("Error: Image file not found.")
        exit()
    img = embed_binary_file(img, file_path, start_pixel=(200, 200))

elif choice == "4":
    # Extract a video frame to embed
    video_capture = cv2.VideoCapture("2616637-hd_1920_1080_30fps.mp4")
    success, frame = video_capture.read()
    if not success:
        print("Error: Could not read video frame.")
        exit()

    # Save the frame as an image
    os.makedirs("stego", exist_ok=True)
    frame_path = "stego/video_frame.jpg"
    cv2.imwrite(frame_path, frame)

    # Embed the frame (as a saved image) into the carrier
    img = embed_binary_file(img, frame_path, start_pixel=(300, 300))
else:
    print("Invalid choice.")
    exit()

cv2.imwrite("encryption_image.jpeg", img)
print("Data successfully embedded into 'encryption_image.jpg'.")
os.system("encryption_image.jpeg")

# --- DECRYPTION ---
pas = input("Enter passcode for Decryption: ")
if password == pas:
    if choice == "1":
        length = int(input("Enter message length: "))
        print("Decrypted Message:", extract_message(img, length))
    elif choice == "2":
        extract_binary_file(img, "stego/decrypted_output.pdf", start_pixel=(100, 100))
        print("PDF extracted to: stego/decrypted_output.pdf")
    elif choice == "3":
        extract_binary_file(img, "stego/decrypted_image.jpg", start_pixel=(200, 200))
        print("Image extracted to: stego/decrypted_image.jpg")
    elif choice == "4":
        extract_binary_file(img, "stego/decrypted_video_frame.jpg", start_pixel=(300, 300))
        print("Video frame extracted to: stego/decrypted_video_frame.jpg")
else:
    print("YOU ARE NOT AUTHORIZED.")