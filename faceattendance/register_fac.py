import os
import cv2

def register_face(name, save_dir='data/faces', num_images=10, camera_index=0):
    
    person_dir = os.path.join(save_dir, name)
    os.makedirs(person_dir, exist_ok=True)

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Cannot access camera")
        return

    print(f"Press SPACE to capture {num_images} images for {name}. ESC to exit.")

    count = 0
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f'{count}/{num_images}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        cv2.imshow('Register Face', frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            if len(faces) == 1:
                x, y, w, h = faces[0]
                face_img = frame[y:y+h, x:x+w]
                cv2.imwrite(os.path.join(person_dir, f'{name}_{count}.jpg'), face_img)
                count += 1
                print(f"Captured {count}/{num_images}")
            else:
                print("Ensure exactly one face is visible!")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    name = input("Enter person name: ").strip()
    register_face(name)
