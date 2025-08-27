# System Architecture Diagram

```mermaid
graph LR
    subgraph Hardware
        Camera
        Computer[Processing Unit]
    end

    subgraph Software
        OpenCV
        FaceRecognition[face_recognition Library]
        AttendanceManager
        Logger
    end

    Camera --> Computer
    Computer --> OpenCV
    OpenCV --> FaceRecognition
    FaceRecognition --> AttendanceManager
    AttendanceManager -->|Writes| CSV[(Attendance.csv)]
    AttendanceManager -->|Logs| Logger
    Logger --> LogFile[(performance.log)]
