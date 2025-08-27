# Sequence Diagram (Attendance Process)

```mermaid
sequenceDiagram
    participant User as Student/Employee
    participant Camera
    participant FR as Face Recognition
    participant DB as Stored Encodings
    participant AM as Attendance Manager
    participant CSV as Attendance.csv
    participant Log as performance.log

    User ->> Camera: Appears in front of camera
    Camera ->> FR: Capture frame
    FR ->> DB: Compare encoding with known faces
    DB -->> FR: Return match (if found)
    FR ->> AM: Send recognition result
    AM ->> CSV: Mark attendance (Name, Time)
    AM ->> Log: Record system performance
    CSV -->> AM: Save entry
    Log -->> AM: Save log
